@echo off
chcp 65001 >nul
echo ============================================
echo   🦞 KimiClaw Master Coder Interface
echo ============================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Set encoding
set PYTHONIOENCODING=utf-8

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing streamlit...
    pip install streamlit -q
)

echo Starting interface...
echo.
echo Browser will open automatically.
echo.

REM Start streamlit
python -m streamlit run interface\app.py --server.port 8502 --server.address localhost

pause
