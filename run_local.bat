@echo off
REM run_local.bat — Talvenor Master OS local dashboard (Windows, Boss's PC)
REM What it does:
REM   0) Shows brain key status - META_API_KEY (Muse Spark, production) and
REM      GEMINI_API_KEY (Gemini free, dev brain). Keys are optional: without
REM      them the dashboard still works and the brain stays mock. The key
REM      VALUES are never printed here.
REM   1) Runs sync_status.py - refreshes dashboards\status.json from the real files
REM   2) Runs a local server in the dashboards folder (http://localhost:8765)
REM   3) Opens the 3D dashboard in the browser
REM What it does NOT do:
REM   Does not run the taskboard - run it with a separate command:
REM   python scripts\taskboard_server.py  (http://localhost:8766/)
REM   Details: LOCAL-RUN.md step 4 + dashboards\TASKBOARD-README.md
REM   Does not prove the live brain - after setting a key, run the proof
REM   from LOCAL-RUN.md Step 5: python scripts\check_live_brain.py --live
REM   (Gemini free dev brain) or the Muse Spark curl test first.
REM To stop: press Ctrl+C in this window.
cd /d "%~dp0"
echo ============================================
echo  Talvenor Master OS — Local Dashboard
echo ============================================
where python >nul 2>nul
if errorlevel 1 (
echo [X] Python not found. Install Python 3.10+ from python.org,
echo     and tick "Add Python to PATH" during install.
  pause
  exit /b 1
)
echo [0/3] Brain key status (keys optional - dashboard works without them)...
if defined META_API_KEY (
echo       [ok] META_API_KEY is set - Muse Spark key ready for the production brain.
) else (
echo       [ ] META_API_KEY not set - production brain stays locked; see LOCAL-RUN.md Step 5.
)
if defined GEMINI_API_KEY (
echo       [ok] GEMINI_API_KEY is set - Gemini free dev brain ready.
) else (
echo       [ ] GEMINI_API_KEY not set - dev brain stays mock; see LOCAL-RUN.md Step 5.
)
echo [1/3] Syncing status (numbers from the real files)...
python scripts\sync_status.py
if errorlevel 1 (
  echo [X] sync_status.py did not run - see the error above.
  pause
  exit /b 1
)
echo [2/3] Starting local server - http://localhost:8765/dashboard-3d.html
echo [3/3] Opening the browser...
start "" "http://localhost:8765/dashboard-3d.html"
echo.
echo Server is running. To stop the dashboard, press Ctrl+C in this window.
python -m http.server 8765 --directory dashboards
