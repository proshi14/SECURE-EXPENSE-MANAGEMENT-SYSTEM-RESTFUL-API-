@echo off
REM Expense Tracker - Start Script
REM This script starts the FastAPI server and opens the browser automatically

echo Starting Expense Tracker...
cd /d "%~dp0"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
