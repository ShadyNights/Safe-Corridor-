from risk_engine import RiskEngine
from datetime import datetime
import database

class RideSession:
    def __init__(self, session_id, start_loc, end_loc):
        self.id = session_id
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.start_time = datetime.now()
        self.path = [start_loc]
        self.status = "ACTIVE"
        
        self.risk_engine = RiskEngine()
        self.consecutive_stops = 0
        self.last_location = start_loc
        self.current_risk = 0
        self.severity = "NORMAL"

    def update_telemetry(self, data):
        current_ts = getattr(data, 'timestamp', None) or int(datetime.now().timestamp() * 1000)
        
        if hasattr(self, 'last_timestamp') and current_ts <= self.last_timestamp:
            print(f"WARN: Dropped duplicate packet {current_ts}")
            return {
                "sessionId": self.id,
                "location": self.last_location,
                "riskScore": self.current_risk,
                "riskProbability": 0.0,
                "severity": self.severity,
                "reasons": [],
                "speed": 0.0
            }
            
        self.last_timestamp = current_ts

        if data.speed < 2.0:
            self.consecutive_stops += 1
        else:
            self.consecutive_stops = 0
            
        self.path.append(data.location)
        self.last_location = data.location

        if not hasattr(self, 'risk_state'):
            self.risk_state = {
                'consecutive_stops': 0,
                'start_loc': self.start_loc.dict(),
                'end_loc': self.end_loc.dict(),
                'last_dist': 999999,
                'bad_trend_count': 0,
                'is_overdue': False
            }
        
        self.risk_state['consecutive_stops'] = self.consecutive_stops
        self.risk_state['is_overdue'] = self.check_eta()

        import numpy as np
        curr_dist = np.sqrt((data.location.lat - self.end_loc.lat)**2 + (data.location.lon - self.end_loc.lon)**2)
        
        last_dist = self.risk_state.get('last_dist', curr_dist)
        if curr_dist > last_dist:
             self.risk_state['bad_trend_count'] = self.risk_state.get('bad_trend_count', 0) + 1
        else:
             self.risk_state['bad_trend_count'] = 0
             
        self.risk_state['last_dist'] = curr_dist
        
        result = self.risk_engine.calculate_risk(self.risk_state, data)

        self.current_risk = result['score']
        self.severity = result['severity']

        database.log_telemetry(self.id, data, self.current_risk)
        if result['reasons']:
            database.log_risk_event(self.id, result['reasons'], self.current_risk)

        return {
            "sessionId": self.id,
            "location": data.location,
            "riskScore": self.current_risk,
            "riskProbability": result.get('probability', 0.0),
            "severity": self.severity,
            "reasons": result['reasons'],
            "speed": data.speed
        }

    def end_ride(self):
        self.status = "COMPLETED"
        database.update_ride_status(self.id, "COMPLETED")
        
        if self.severity == "NORMAL":
             database.delete_ride_data(self.id)

    def check_eta(self):
        import numpy as np
        dist = np.sqrt((self.start_loc.lat - self.end_loc.lat)**2 + (self.start_loc.lon - self.end_loc.lon)**2) * 111000 
        expected_seconds = dist / 8.3
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if elapsed > (expected_seconds * 2.0) and elapsed > 300: 
            return True 
        return False
