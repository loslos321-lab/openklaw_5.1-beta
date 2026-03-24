#!/usr/bin/env pwsh
# KimiClaw HTTPS Startup Script
# Automatic SSL with Let's Encrypt

$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "White"
Clear-Host

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║          KimiClaw - HTTPS Setup                              ║
║          Secure Deployment with SSL                          ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating from .env.example..."
    Copy-Item .env.example .env
    Write-Host "✅ Created .env - please configure your API keys and domain!" -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Load environment variables
$envContent = Get-Content .env -Raw
$envVars = @{}
$envContent -split "`n" | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        $envVars[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$domain = $envVars['DOMAIN'] -or 'localhost'
$email = $envVars['ACME_EMAIL'] -or 'admin@example.com'

Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   Domain: $domain"
Write-Host "   Email:  $email"
Write-Host ""

# Check if Docker is running
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
} catch {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🚀 Starting KimiClaw with HTTPS..." -ForegroundColor Green
Write-Host ""

# Create letsencrypt directory
if (-not (Test-Path letsencrypt)) {
    New-Item -ItemType Directory -Name letsencrypt | Out-Null
}

# Start services
try {
    docker-compose -f docker-compose.https.yml up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Docker compose failed"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Failed to start services!" -ForegroundColor Red
    Write-Host "Check the error messages above."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "✅ KimiClaw is starting with HTTPS!" -ForegroundColor Green
Write-Host ""
Write-Host @"
╔══════════════════════════════════════════════════════════════╗
  🌐 Access your secure application:
     https://$domain

  📊 Traefik Dashboard (optional):
     http://localhost:8080
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  First startup may take 1-2 minutes for SSL certificate." -ForegroundColor Yellow
Write-Host "   Check logs: docker-compose -f docker-compose.https.yml logs -f"
Write-Host ""
Read-Host "Press Enter to continue"
