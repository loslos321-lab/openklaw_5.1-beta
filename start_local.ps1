$env:PYTHONIOENCODING = "utf-8"
Set-Location "C:\Users\Student\kimiclaw"
& .\venv\Scripts\Activate.ps1
streamlit run interface\app.py --server.port 8501
