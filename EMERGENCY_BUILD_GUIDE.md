# 🚨 EMERGENCY BUILD GUIDE 🚨

**Problem:** Your computer only has **Java 8** installed.
**Requirement:** Android App requires **Java 17**.

Because of this, running commands in the terminal (PowerShell/CMD) will **ALWAYS FAIL**.

## ✅ THE SOLTUION: Use Android Studio

Android Studio comes with its own hidden internal Java 17. You MUST use it to build the app.

### Step 1: Open the Project Correctly
1.  Open **Android Studio**.
2.  File > **Open**.
3.  Select ONLY this folder: `D:\Hacknagpur\android-app\SafeCorridorTracker`.

### Step 2: Sync and Build
1.  Click the **Elephant Icon** (Sync Project with Gradle Files) in the top-right toolbar.
    *   *Wait for the bottom status bar to finish.*
2.  Go to the menu bar: **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.

### Step 3: Get the App
1.  Once the build finishes, a small "notification" bubble will appear in the bottom right corner.
2.  Click **"locate"**.
3.  It will open the folder containing `app-debug.apk`.
4.  Copy this file to your phone.

---
**DO NOT RUN `./gradlew` IN THE TERMINAL. IT WILL NOT WORK.**
