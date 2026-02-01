# SafeCorridor System Guide

This is the complete guide to running the SafeCorridor Pilot system (Backend + Dashboard) and building the Android Client.

## 1. Prerequisites
-   **Python 3.10+** (For Backend)
-   **Node.js 16+** (For Dashboard)
-   **Android Studio (Latest)** (For building the Mobile App)

---

## 2. Running the Backend (Python)
The backend manages ride sessions, risk analysis, and database storage.

1.  **Navigate to backend**:
    ```powershell
    cd backend
    ```
2.  **Install dependencies**:
    ```powershell
    pip install fastapi uvicorn python-socketio scikit-learn numpy
    ```
3.  **Run the Server**:
    ```powershell
    python main.py
    ```
    *Server will start on `http://0.0.0.0:3000`*

---

## 3. Running the Dashboard (React)
The dashboard provides the Ops Center view (Map, Risk Timeline, Logs).

1.  **Navigate to dashboard**:
    ```powershell
    cd dashboard
    ```
2.  **Install dependencies**:
    ```powershell
    npm install
    ```
3.  **Start the Dev Server**:
    ```powershell
    npm run dev
    ```
    *Dashboard will open at `http://localhost:5173`*

---

## 4. Building the Android APK
Since this project was scaffolded for the pilot, the best way to build the APK is via Android Studio, which will automatically set up the Gradle build environment for you.

### Step-by-Step Build:
1.  Open **Android Studio**.
2.  Select **Open** (or "Open an existing project").
3.  Navigate to and select this folder:  
    `D:\Hacknagpur\android-app\SafeCorridorTracker`
4.  **Wait for Sync**: Android Studio will download the necessary Gradle versions and SDKs.
    -   *Note: If asked to trust the project, select "Trust Project".*
5.  **Build the APK**:
    -   Go to Menu: **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
6.  **Locate the File**:
    -   Once finished, a popup "Build APK(s)" will appear. Click **locate**.
    -   Or find it manually in: `android-app/SafeCorridorTracker/app/build/outputs/apk/debug/app-debug.apk`.

### Installing on Phone:
1.  Connect your Android phone via USB.
2.  Enable **USB Debugging** in Developer Options.
3.  Run from Android Studio (Green Play Button) **OR** copy the `.apk` file to your phone and install it manually.

---

## 5. Pilot Architecture Notes
-   **Database**: A `safecorridor.db` (SQLite) file will be created in the `backend/` folder automatically.
-   **Logs**: All risk events are logged to this database.
-   **Sanitization**: This codebase has been scrubbed of all comments and legacy files for the final submission.
