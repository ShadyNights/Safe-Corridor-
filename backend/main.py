import socketio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from datetime import datetime
from session_manager import RideSession
import database

class Location(BaseModel):
    lat: float
    lon: float

class StartRideRequest(BaseModel):
    startLocation: Location
    endLocation: Location

class EndRideRequest(BaseModel):
    sessionId: str

class TelemetryRequest(BaseModel):
    sessionId: str
    location: Location
    speed: float
    deviation: Optional[float] = 0.0
    accuracy: Optional[float] = 0.0
    timestamp: Optional[int] = None

app = FastAPI()

database.init_db()

sessions: Dict[str, RideSession] = {}

def cleanup_stale_sessions():
    cutoff = datetime.now().timestamp() - 7200
    active_sids = list(sessions.keys())
    count = 0
    
    for sid in active_sids:
        session = sessions[sid]
        last_ts = getattr(session, 'last_timestamp', 0) / 1000.0
        if last_ts == 0: last_ts = session.start_time.timestamp()
        
        if last_ts < cutoff:
            print(f"CLEANUP: Closing stale session {sid}")
            session.status = "ABANDONED"
            database.update_ride_status(sid, "ABANDONED")
            del sessions[sid]
            count += 1
            
    if count > 0:
        print(f"Cleanup: Removed {count} stale sessions.")

def load_active_rides():
    cleanup_stale_sessions()
    
    active_rows = database.get_active_rides()
    count = 0
    for row in active_rows:
        s_id = row['ride_session_id']
        start_loc = Location(lat=row['start_lat'], lon=row['start_lon'])
        end_loc = Location(lat=row['end_lat'], lon=row['end_lon'])
        
        session = RideSession(s_id, start_loc, end_loc)
        sessions[s_id] = session
        count += 1
    print(f"Global State Recovery: Rehydrated {count} active rides.")

load_active_rides()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

@app.get("/")
def read_root():
    return {"message": "SafeCorridor Backend Running"}

@app.post("/api/ride/start")
async def start_ride(req: StartRideRequest):
    session_id = str(int(datetime.now().timestamp() * 1000))
    database.create_ride(session_id, req.startLocation.dict(), req.endLocation.dict())
    new_session = RideSession(session_id, req.startLocation, req.endLocation)
    sessions[session_id] = new_session
    print(f"Ride started: {session_id}")
    await sio.emit('ride_started', {
        "sessionId": session_id,
        "startLocation": req.startLocation.dict(),
        "endLocation": req.endLocation.dict()
    })
    return {"sessionId": session_id, "status": "STARTED"}

@app.post("/api/ride/telemetry")
async def ride_telemetry(req: TelemetryRequest):
    session = sessions.get(req.sessionId)
    if not session:
        print(f"Auto-creating session for {req.sessionId}")
        start_loc = req.location
        end_loc = req.location
        database.create_ride(req.sessionId, start_loc.dict(), end_loc.dict())
        session = RideSession(req.sessionId, start_loc, end_loc)
        sessions[req.sessionId] = session
        await sio.emit('ride_started', {
            "sessionId": req.sessionId,
            "startLocation": start_loc.dict(),
            "endLocation": end_loc.dict()
        })

    result = session.update_telemetry(req)
    result['location'] = req.location.dict()
    await sio.emit('ride_update', result)
    return result

@app.post("/api/ride/end")
async def end_ride(req: EndRideRequest):
    session = sessions.get(req.sessionId)
    if session:
        print(f"Ride ended: {req.sessionId}")
        session.end_ride()
        await sio.emit('ride_ended', {"sessionId": req.sessionId})
        del sessions[req.sessionId]
    return {"status": "ENDED"}

@sio.event
async def connect(sid, environ):
    print("Dashboard connected", sid)

@sio.event
async def disconnect(sid):
    print("Dashboard disconnected", sid)

if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=3000, reload=True)
