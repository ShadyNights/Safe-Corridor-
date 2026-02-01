import numpy as np
import datetime
import math

class RiskEngine:
    """
    NO-BLIND-TRUST POLICY ENFORCEMENT
    ---------------------------------
    This engine MUST NOT import or make calls to external APIs.
    It must rely SOLELY on:
    1. Telemetry provided by the Rider App (GPS, Speed).
    2. Local geometric calculations.
    3. Time-based inference.
    """
    def __init__(self):
        # Persistent Risk State (Cumulative)
        self.risk_score = 0.0
        self.history = []
        
        # Configuration
        self.MAX_RISK = 100.0
        self.DECAY_RATE = 2.0
        
        # Production-Grade Thresholds (Tuned)
        self.CORRIDOR_WIDTH_M = 2000.0  # 2km wide corridor (1km each side) - Forgiving
        self.MAX_SPEED_MPS = 36.0       # ~130 km/h
        self.ELEVATED_THRESHOLD = 30.0
        self.MONITORING_THRESHOLD = 60.0
        self.CRITICAL_THRESHOLD = 80.0
        
        # Weights
        self.WEIGHT_STOP = 15.0
        self.WEIGHT_DEVIATION = 15.0  # Increased for corridor violation
        self.WEIGHT_DIRECTION = 5.0
        self.WEIGHT_SPEED = 10.0      # New
        self.WEIGHT_OVERDUE = 20.0

        self.window_size = 5
        self.location_window = [] 

    def _cross_track_error(self, start_loc, end_loc, curr_lat, curr_lon):
        """
        Calculates perpendicular distance (meters) from current point to the 
        straight line between start and end. (Production Grade Geometry)
        """
        R = 6371000 # Earth radius in meters
        
        # Convert to radians
        lat1 = math.radians(start_loc['lat'])
        lon1 = math.radians(start_loc['lon'])
        lat2 = math.radians(end_loc['lat'])
        lon2 = math.radians(end_loc['lon'])
        lat3 = math.radians(curr_lat)
        lon3 = math.radians(curr_lon)
        
        # Great Circle Bearing (Start to End)
        y = math.sin(lon2 - lon1) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        bearing12 = math.atan2(y, x)
        
        # Great Circle Bearing (Start to Current)
        y3 = math.sin(lon3 - lon1) * math.cos(lat3)
        x3 = math.cos(lat1) * math.sin(lat3) - math.sin(lat1) * math.cos(lat3) * math.cos(lon3 - lon1)
        bearing13 = math.atan2(y3, x3)
        
        # Angular distance from start to current
        d13 = math.acos(math.sin(lat1) * math.sin(lat3) + math.cos(lat1) * math.cos(lat3) * math.cos(lon3 - lon1))
        
        # Cross-track distance
        d_xt = math.asin(math.sin(d13) * math.sin(bearing13 - bearing12)) * R
        return abs(d_xt)

    def calculate_risk(self, session_state, telemetry):
        risk_delta = 0.0
        reasons = []

        # 1. Smooth GPS
        self.location_window.append((telemetry.location.lat, telemetry.location.lon))
        if len(self.location_window) > self.window_size:
            self.location_window.pop(0)

        if len(self.location_window) >= 3:
            locs = np.array(self.location_window)
            current_lat = np.median(locs[:, 0])
            current_lon = np.median(locs[:, 1])
        else:
            current_lat = telemetry.location.lat
            current_lon = telemetry.location.lon

        # 2. Data Quality Check
        accuracy = getattr(telemetry, 'accuracy', 0.0)
        is_trusted_location = accuracy <= 50.0 # 50m accuracy required
        
        if is_trusted_location:
            # A. Corridor Check (Cross-Track Error)
            start_loc = session_state.get('start_loc') # Need to ensure this is passed, fallback if not
            if start_loc:
                xt_error = self._cross_track_error(start_loc, session_state['end_loc'], current_lat, current_lon)
                if xt_error > self.CORRIDOR_WIDTH_M:
                    risk_delta += self.WEIGHT_DEVIATION
                    reasons.append(f"Corridor violation (+{int(xt_error)}m)")
            
            # B. Speed Check
            if telemetry.speed > self.MAX_SPEED_MPS:
                risk_delta += self.WEIGHT_SPEED
                reasons.append(f"Unsafe speed ({int(telemetry.speed*3.6)} km/h)")
            
            # C. Prolonged Stops
            if telemetry.speed < 2.0 and session_state.get('consecutive_stops', 0) > 24: 
                 risk_delta += self.WEIGHT_STOP
                 reasons.append(f"Prolonged stationary ({session_state['consecutive_stops']} ticks)")

            # D. Moving Away (Trend)
            curr_dist = np.sqrt((current_lat - session_state['end_loc']['lat'])**2 + 
                                (current_lon - session_state['end_loc']['lon'])**2)
            last_dist = session_state.get('last_dist', curr_dist)
            if curr_dist > (last_dist + 0.0001) and session_state.get('bad_trend_count', 0) > 5:
                 risk_delta += self.WEIGHT_DIRECTION
                 reasons.append("Moving away from destination")

        else:
             if risk_delta == 0:
                reasons.append(f"Low confidence GPS ({accuracy}m) - Monitoring paused")

        # E. Time Overdue (Always Valid)
        if session_state.get('is_overdue', False):
             risk_delta += self.WEIGHT_OVERDUE
             reasons.append("Ride overdue")

        # 3. Apply Cumulative Logic
        if risk_delta > 0:
            self.risk_score = min(self.MAX_RISK, self.risk_score + risk_delta)
        else:
            self.risk_score = max(0.0, self.risk_score - self.DECAY_RATE)

        # 4. Probabilistic Output (Sigmoid)
        # Map 0-100 score to 0.0-1.0 probability with sigmoid curve centered at 50
        # k=0.1 steepness
        probability = 1 / (1 + math.exp(-0.1 * (self.risk_score - 50)))
        
        # 5. Severity State
        severity = "NORMAL"
        if self.risk_score >= self.CRITICAL_THRESHOLD: severity = "CRITICAL"
        elif self.risk_score >= self.MONITORING_THRESHOLD: severity = "MONITORING"
        elif self.risk_score >= self.ELEVATED_THRESHOLD: severity = "ELEVATED"

        if risk_delta > 0:
             self.history.append({
                 "time": datetime.datetime.now().isoformat(),
                 "score": self.risk_score,
                 "probability": round(probability, 4),
                 "reasons": reasons
             })

        return {
            "score": round(self.risk_score, 1),
            "probability": round(probability, 4),
            "severity": severity,
            "reasons": reasons
        }
