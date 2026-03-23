# KimiClaw Master Coder Interface Launcher

$Host.UI.RawUI.WindowTitle = "KimiClaw Interface"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   🦞 KimiClaw Master Coder Interface" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set encoding
$env:PYTHONIOENCODING = "utf-8"

# Change to script directory
Set-Location $PSScriptRoot

# Check if streamlit is installed
Write-Host "Checking dependencies..." -NoNewline
try {
    python -c "import streamlit" 2>$null
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " Installing..." -ForegroundColor Yellow
    pip install streamlit -q
}

Write-Host ""
Write-Host "Starting interface..." -ForegroundColor Green
Write-Host "Browser will open automatically at http://localhost:8501"
Write-Host ""

# Start streamlit
python -m streamlit run interface\app.py --server.port 8502 --server.address localhost

Write-Host ""
Write-Host "Interface closed." -ForegroundColor Yellow
