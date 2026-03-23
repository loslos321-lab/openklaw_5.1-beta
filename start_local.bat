@echo off
cd /d "C:\Users\Student\kimiclaw"
call venv\Scripts\activate.bat
set PYTHONIOENCODING=utf-8
streamlit run interface\app.py --server.port 8501
echo.
echo KimiClaw stopped.
pause
