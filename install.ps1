#!/usr/bin/env powershell
# KimiClaw Docker Installation Script
# Installiert Docker (falls nötig) und startet den Container

param(
    [switch]$SkipDockerInstall,
    [switch]$OnlyStartContainer
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   🦞 KimiClaw Docker Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Warning: Not running as Administrator. Docker installation may fail." -ForegroundColor Yellow
}

# Function to check if Docker is installed
function Test-DockerInstalled {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $info = docker info 2>$null
        if ($info) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Step 1: Check/Install Docker
if (-not $OnlyStartContainer) {
    Write-Host "🔍 Checking Docker installation..." -NoNewline
    
    if (Test-DockerInstalled) {
        Write-Host " ✅ Docker found" -ForegroundColor Green
        
        Write-Host "🔍 Checking if Docker is running..." -NoNewline
        if (Test-DockerRunning) {
            Write-Host " ✅ Docker is running" -ForegroundColor Green
        } else {
            Write-Host " ❌ Docker is not running" -ForegroundColor Red
            Write-Host ""
            Write-Host "Please start Docker Desktop manually:" -ForegroundColor Yellow
            Write-Host "  1. Press Windows key"
            Write-Host "  2. Type 'Docker Desktop'"
            Write-Host "  3. Click to start"
            Write-Host ""
            Read-Host "Press Enter after Docker Desktop has started"
            
            # Check again
            if (-not (Test-DockerRunning)) {
                Write-Host "❌ Docker still not running. Exiting." -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host " ❌ Docker not found" -ForegroundColor Red
        
        if ($SkipDockerInstall) {
            Write-Host "❌ Docker is required. Exiting." -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "📦 Docker Installation Options:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Option 1: Install Docker Desktop (Recommended)" -ForegroundColor Green
        Write-Host "  Download from: https://www.docker.com/products/docker-desktop"
        Write-Host "  Or run: winget install Docker.DockerDesktop"
        Write-Host ""
        Write-Host "Option 2: Install Rancher Desktop (Alternative)" -ForegroundColor Yellow
        Write-Host "  Download from: https://rancherdesktop.io/"
        Write-Host "  Or run: winget install Rancher.RancherDesktop"
        Write-Host ""
        
        $installChoice = Read-Host "Install Docker Desktop now? (Y/N)"
        
        if ($installChoice -eq 'Y' -or $installChoice -eq 'y') {
            Write-Host "🚀 Installing Docker Desktop via winget..." -ForegroundColor Cyan
            
            try {
                winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
                Write-Host "✅ Docker Desktop installed!" -ForegroundColor Green
                Write-Host ""
                Write-Host "📝 Please complete the Docker Desktop setup wizard." -ForegroundColor Yellow
                Write-Host "   Then restart your computer and run this script again." -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 0
            } catch {
                Write-Host "❌ Installation failed. Please install manually:" -ForegroundColor Red
                Write-Host "   https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
                exit 1
            }
        } else {
            Write-Host "❌ Docker is required. Please install manually:" -ForegroundColor Red
            Write-Host "   https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
            exit 1
        }
    }
}

# Step 2: Check .env file
Write-Host ""
Write-Host "🔍 Checking .env file..." -NoNewline

$envFile = Join-Path $PSScriptRoot ".env"
$envExample = Join-Path $PSScriptRoot ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Write-Host " ⚠️  Not found, copying from .env.example" -ForegroundColor Yellow
        Copy-Item $envExample $envFile
        Write-Host "✅ Created .env file" -ForegroundColor Green
    } else {
        Write-Host " ❌ No .env file found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host " ✅ Found" -ForegroundColor Green
}

# Check if API key is set
$envContent = Get-Content $envFile -Raw
if ($envContent -match "sk-your-key-here" -or $envContent -match "sk-dein-api-key-hier") {
    Write-Host ""
    Write-Host "⚠️  API Key not configured!" -ForegroundColor Yellow
    Write-Host "Please edit the .env file and add your API key:" -ForegroundColor Cyan
    Write-Host "   File: $envFile" -ForegroundColor White
    Write-Host ""
    Write-Host "Get your API key from:" -ForegroundColor Cyan
    Write-Host "   - SiliconFlow: https://cloud.siliconflow.cn/ (14M free tokens)"
    Write-Host "   - Kimi: https://platform.moonshot.cn/"
    Write-Host ""
    
    $editNow = Read-Host "Open .env in Notepad now? (Y/N)"
    if ($editNow -eq 'Y' -or $editNow -eq 'y') {
        notepad $envFile
        Read-Host "Press Enter after saving the file"
        
        # Check again
        $envContent = Get-Content $envFile -Raw
        if ($envContent -match "sk-your-key-here" -or $envContent -match "sk-dein-api-key-hier") {
            Write-Host "❌ API key still not set. Exiting." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Please configure the API key and run again." -ForegroundColor Red
        exit 1
    }
}

# Step 3: Build and Start Container
Write-Host ""
Write-Host "🐳 Building Docker image..." -ForegroundColor Cyan

try {
    docker-compose build
    Write-Host "✅ Image built successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Build failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting KimiClaw container..." -ForegroundColor Cyan

try {
    docker-compose up -d
    Write-Host "✅ Container started!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Show status
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Open in browser:" -ForegroundColor Cyan
Write-Host "   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f    # View logs"
Write-Host "   docker-compose down       # Stop container"
Write-Host "   docker-compose restart    # Restart"
Write-Host ""
Write-Host "🛑 To stop:" -ForegroundColor Yellow
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""

# Try to open browser
$openBrowser = Read-Host "Open browser now? (Y/N)"
if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
    Start-Process "http://localhost:8501"
}

Write-Host "🦞 Happy coding with KimiClaw!" -ForegroundColor Cyan
Write-Host ""
