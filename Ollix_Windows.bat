@echo off
title Ollix Quantamental Terminal
setlocal enabledelayedexpansion

:: Force terminal execution context to match the folder where the file lives
cd /d "%~dp0"

echo ======================================================================
echo 🏛️  OLLIX QUANTAMENTAL TERMINAL - AUTOMATED BOOT LOADER
echo ======================================================================
echo.

:: Stage 1: Verify Python presence on the host machine
echo 🔍 Verifying local Python architecture...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python was not detected on your system.
    echo    Please install Python 3.10+ and check 'Add Python to PATH'.
    echo.
    pause
    exit /b
)
echo ✅ Python environment mapped.

:: Stage 2: Silently verify or provision library dependencies
echo ⚡ Auditing system dependency arrays...
pip install --quiet streamlit pandas numpy yfinance scipy requests beautifulsoup4 lxml openpyxl
echo ✅ Core software modules verified and locked.
echo.

:: Stage 3: Boot the local presentation layers
echo 🚀 Launching Ollix Core UI Dashboard...
echo ----------------------------------------------------------------------
python run_ollix.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Execution halted due to an unexpected application error.
    pause
)