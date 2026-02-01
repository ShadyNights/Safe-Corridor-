# SafeCorridor — Urban Safety Safety System (Production Grade)
**Passive, Trust-Aware Ride Monitoring**

## 🛡️ Mission
To provide a fail-safe, passive safety monitoring system for ride-sharing that works even when the user is under duress, frozen, or in a trusted-but-compromised situation.

---

## 🚀 Round 2 Status: PRODUCTION READY
This system has been hardened for real-world deployment.

### Key Production Features
- **Zero-Trust Intelligence:** No reliance on external community data or APIs. All risk math is local.
- **Privacy-First:** "Safe" rides are hard-deleted. No surveillance state.
- **Network Resilient:** Idempotent ingestion pipeline handles 4G dead zones and bursts.
- **Anti-Tamper:** Detects Mock Locations/GPS Spoofing.

---

## 🛠️ Tech Stack
- **Android:** Kotlin, Room (Offline Buffer), Foreground Service, Geofencing.
- **Backend:** Python (FastAPI), Socket.IO, SQLite (WAL Enabled), NumPy (Vectorized Math).
- **Intelligence:** Cumulative Risk Engine with Sigmoid Probability & Great Circle Geometry.

---

## 🏃‍♂️ Quick Start

### 1. Start Backend (Risk Engine)
The backend manages ride sessions, risk analysis, and database storage.

```powershell
cd backend
pip install -r requirements.txt
python main.py
```
*Server runs on `http://0.0.0.0:3000`*

### 2. Run Android App (Tracker)
Since this project simulates a real Background Service:
1.  Open `android-app/SafeCorridorTracker` in **Android Studio**.
2.  Click **Run** (Green Play Button).
3.  Ensure Emulator/Device is on the same network (or use `10.0.2.2` for Emulator).
4.  *Note: The app sends telemetry to the backend automatically.*

### 3. Run Dashboard (Ops Center)
The dashboard provides the live map and risk timeline.

```powershell
cd dashboard
npm install
npm run dev
```
*Web App runs on `http://localhost:5173`*

---

## 📂 Documentation (For Judges)
- **[Defense Guide (Strategy)](file:///./production_defense_guide.md)**: Read this for Q&A (Liability, Privacy, Failure Modes).
- **[Final Audit](file:///./final_audit.md)**: Verification of all Round 2 requirements.
- **[Build Steps](file:///./ANDROID_BUILD_STEPS.md)**: Detailed Android build instructions.
