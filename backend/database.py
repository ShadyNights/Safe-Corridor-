import sqlite3
import json
from datetime import datetime

DB_NAME = "safecorridor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS rides (
                 ride_session_id TEXT PRIMARY KEY,
                 start_time TEXT,
                 end_time TEXT,
                 start_lat REAL,
                 start_lon REAL,
                 end_lat REAL,
                 end_lon REAL,
                 final_state TEXT
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS telemetry (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ride_session_id TEXT,
                 timestamp TEXT,
                 lat REAL,
                 lon REAL,
                 speed REAL,
                 risk_score REAL,
                 FOREIGN KEY(ride_session_id) REFERENCES rides(ride_session_id)
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS risk_log (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ride_session_id TEXT,
                 timestamp TEXT,
                 reasons TEXT,
                 risk_score REAL,
                 FOREIGN KEY(ride_session_id) REFERENCES rides(ride_session_id)
                 )''')
                 
    conn.commit()
    conn.close()
    print("Database Initialized")

def create_ride(session_id, start_loc, end_loc):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO rides (ride_session_id, start_time, start_lat, start_lon, end_lat, end_lon, final_state) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (session_id, datetime.now().isoformat(), start_loc['lat'], start_loc['lon'], end_loc['lat'], end_loc['lon'], "ACTIVE"))
    conn.commit()
    conn.close()

def log_telemetry(session_id, data, risk_score):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO telemetry (ride_session_id, timestamp, lat, lon, speed, risk_score) VALUES (?, ?, ?, ?, ?, ?)",
              (session_id, datetime.now().isoformat(), data.location.lat, data.location.lon, data.speed, risk_score))
    conn.commit()
    conn.close()

def log_risk_event(session_id, reasons, risk_score):
    if not reasons: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    reasons_str = json.dumps(reasons)
    c.execute("INSERT INTO risk_log (ride_session_id, timestamp, reasons, risk_score) VALUES (?, ?, ?, ?)",
              (session_id, datetime.now().isoformat(), reasons_str, risk_score))
    conn.commit()
    conn.close()

def get_active_rides():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM rides WHERE final_state = 'ACTIVE'")
    rows = c.fetchall()
    
    rides = []
    for row in rows:
        rides.append(dict(row))
    conn.close()
    return rides

def update_ride_status(session_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE rides SET final_state = ?, end_time = ? WHERE ride_session_id = ?",
              (status, datetime.now().isoformat(), session_id))
    conn.commit()
    conn.close()

def delete_ride_data(session_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM telemetry WHERE ride_session_id = ?", (session_id,))
    c.execute("DELETE FROM risk_log WHERE ride_session_id = ?", (session_id,))
    c.execute("DELETE FROM rides WHERE ride_session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    print(f"PRIVACY AUDIT: Hard deleted session {session_id} (Ride Safe)")
    print(f"PRIVACY: Deleted Normal Ride Data for {session_id}")
