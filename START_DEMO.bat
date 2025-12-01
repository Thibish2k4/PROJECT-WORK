@echo off
REM Honeytoken Detection System - One-Click Demo Launcher
REM Double-click this file to start the demo

title Honeytoken Detection System - Demo

echo.
echo ========================================
echo  HONEYTOKEN DETECTION SYSTEM
echo  Starting Demo Environment...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Run the demo launcher
python start_demo.py

REM Pause on error
if errorlevel 1 (
    echo.
    echo An error occurred. Check the output above.
    pause
)
