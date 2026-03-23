@echo off
chcp 65001 >nul
echo ========================================
echo   🦞 KimiClaw Docker Starter
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found!
    echo Please install Docker Desktop first:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker found
echo.

echo Checking .env file...
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from template...
        copy .env.example .env
        echo ⚠️  Please edit .env and add your API key!
        notepad .env
        pause
    ) else (
        echo ❌ No .env file found!
        pause
        exit /b 1
    )
)

echo.
echo 🐳 Starting container...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Failed to start!
    pause
    exit /b 1
)

echo.
echo ✅ Container started!
echo.
echo 🌐 Opening http://localhost:8501
timeout /t 2 >nul
start http://localhost:8501

echo.
echo 📋 Commands:
echo   docker-compose logs -f  (view logs)
echo   docker-compose down     (stop)
echo.
pause
