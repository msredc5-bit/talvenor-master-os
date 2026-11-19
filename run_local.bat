@echo off
REM run_local.bat — Talvenor Master OS local dashboard (Windows, Boss-এর PC)
REM যা করে:
REM   1) sync_status.py চালায় — আসল ফাইল থেকে dashboards\status.json তাজা করে
REM   2) dashboards ফোল্ডারে local server চালায় (http://localhost:8765)
REM   3) ব্রাউজারে 3D dashboard খোলে
REM বন্ধ করতে: এই window-এ Ctrl+C চাপুন।
cd /d "%~dp0"
echo ============================================
echo  Talvenor Master OS — Local Dashboard
echo ============================================
where python >nul 2>nul
if errorlevel 1 (
  echo [X] Python পাওয়া যায়নি। python.org থেকে Python 3.10+ install করুন,
  echo     install-এর সময় "Add Python to PATH" টিক দিতে হবে।
  pause
  exit /b 1
)
echo [1/3] Status sync হচ্ছে (আসল ফাইল থেকে সংখ্যা)...
python scripts\sync_status.py
if errorlevel 1 (
  echo [X] sync_status.py চলল না — উপরের error দেখুন।
  pause
  exit /b 1
)
echo [2/3] Local server চালু হচ্ছে — http://localhost:8765/dashboard-3d.html
echo [3/3] ব্রাউজার খুলছে...
start "" "http://localhost:8765/dashboard-3d.html"
echo.
echo Server চলছে। Dashboard বন্ধ করতে এই window-এ Ctrl+C চাপুন।
python -m http.server 8765 --directory dashboards
