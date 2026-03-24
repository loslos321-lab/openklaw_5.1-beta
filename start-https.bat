@echo off
chcp 65001 >nul
cls

echo ╔══════════════════════════════════════════════════════════════╗
echo ║          KimiClaw - HTTPS Setup                              ║
echo ║          Secure Deployment with SSL                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Creating from .env.example...
    copy .env.example .env >nul
    echo ✅ Created .env - please configure your API keys and domain!
    echo.
    pause
    exit /b 1
)

:: Load environment variables
for /f "tokens=*" %%a in (.env) do (
    set %%a
)

echo 📋 Configuration:
echo    Domain: %DOMAIN%
echo    Email:  %ACME_EMAIL%
echo.

:: Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

echo 🚀 Starting KimiClaw with HTTPS...
echo.

:: Create letsencrypt directory
if not exist letsencrypt mkdir letsencrypt

:: Start services
docker-compose -f docker-compose.https.yml up -d

if errorlevel 1 (
    echo.
    echo ❌ Failed to start services!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ KimiClaw is starting with HTTPS!
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🌐 Access your secure application:                          ║
echo ║     https://%DOMAIN%                                         ║
echo ║                                                                ║
echo ║  📊 Traefik Dashboard (optional):                            ║
echo ║     http://localhost:8080                                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  First startup may take 1-2 minutes for SSL certificate.
echo    Check logs: docker-compose -f docker-compose.https.yml logs -f
echo.
pause
