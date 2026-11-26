@echo off
REM FOUNDER OS environment checker (F1, C1-C5) — checks only, installs nothing.
REM Double-click this file. Results are written to pc-env-check.txt and opened in Notepad.
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH.
  echo Install Python 3.11 or newer, close this window, then double-click again.
  pause
  exit /b 1
)
python scripts\check_pc_env.py
if errorlevel 1 (
  echo The checker hit an error. See pc-env-check.txt for details.
  pause
  exit /b 1
)
notepad pc-env-check.txt
