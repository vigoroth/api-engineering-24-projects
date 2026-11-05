@echo off
rem Start the P01 API with the env's Python and the M5 logging setup.
rem Usage: run.bat [port]   (default 8000)
cd /d "%~dp0"
set "PY=%LOCALAPPDATA%\miniconda3\envs\apis24\python.exe"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8000"
if not exist "%PY%" (
  echo Python not found at %PY%
  pause
  exit /b 1
)
echo Starting on http://127.0.0.1:%PORT%  (Ctrl+C to stop)
"%PY%" -m uvicorn app.main:app --host 127.0.0.1 --port %PORT% --no-access-log --log-config logging.json
pause
