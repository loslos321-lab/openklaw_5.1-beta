#!/usr/bin/env powershell
<#
.SYNOPSIS
    Start KimiClaw Master Coder Agent
.DESCRIPTION
    Initializes and runs the master coder agent with the specified mode
.PARAMETER Mode
    Run mode: interactive (default), work, learn, or sandbox
.PARAMETER Days
    Number of days to run in work mode
.EXAMPLE
    .\start_agent.ps1
    Starts in interactive mode
.EXAMPLE
    .\start_agent.ps1 -Mode work -Days 5
    Runs work mode for 5 days
#>

param(
    [ValidateSet("interactive", "work", "learn", "sandbox")]
    [string]$Mode = "interactive",
    
    [int]$Days = 1,
    
    [switch]$Help
)

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit
}

# Colors for output
$Green = "`e[32m"
$Cyan = "`e[36m"
$Yellow = "`e[33m"
$Reset = "`e[0m"

Write-Host ""
Write-Host "$Cyan========================================$Reset"
Write-Host "$Cyan   🦞 KimiClaw Master Coder$Reset"
Write-Host "$Cyan========================================$Reset"
Write-Host ""

# Check Python
Write-Host "${Yellow}Checking Python...$Reset" -NoNewline
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " ${Green}✓$Reset $pythonVersion"
} else {
    Write-Host " ${Red}✗ Python not found$Reset"
    exit 1
}

# Check virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "${Yellow}Creating virtual environment...$Reset"
    python -m venv venv
}

# Activate virtual environment
Write-Host "${Yellow}Activating virtual environment...$Reset" -NoNewline
& .\venv\Scripts\Activate.ps1
Write-Host " ${Green}✓$Reset"

# Check dependencies
Write-Host "${Yellow}Checking dependencies...$Reset" -NoNewline
$missingDeps = $false
try {
    python -c "import langchain, fastapi, uvicorn" 2>$null
    if ($LASTEXITCODE -ne 0) { $missingDeps = $true }
} catch {
    $missingDeps = $true
}

if ($missingDeps) {
    Write-Host " ${Yellow}Installing...$Reset"
    pip install -r requirements.txt -q
} else {
    Write-Host " ${Green}✓$Reset"
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "${Yellow}Creating .env file...$Reset"
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    if (-not (Test-Path ".env")) {
        @"
# KimiClaw Master Coder Environment
OPENAI_API_KEY=your-api-key-here
EVALUATION_API_KEY=your-api-key-here
WEB_SEARCH_API_KEY=your-tavily-api-key-here
E2B_API_KEY=your-e2b-api-key-here
MCP_SERVER_URL=http://127.0.0.1:64342/sse
"@ | Out-File -FilePath ".env" -Encoding UTF8
    }
    Write-Host "${Yellow}⚠️  Please edit .env with your API keys$Reset"
}

# Check MCP server
Write-Host "${Yellow}Checking MCP server...$Reset" -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:64342/sse" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host " ${Green}✓ Connected$Reset"
} catch {
    Write-Host " ${Yellow}⚠ Not responding (will retry during run)$Reset"
}

Write-Host ""
Write-Host "$Cyan----------------------------------------$Reset"
Write-Host "  Mode: $Mode"
if ($Mode -eq "work") {
    Write-Host "  Days: $Days"
}
Write-Host "$Cyan----------------------------------------$Reset"
Write-Host ""

# Run the agent
if ($Mode -eq "work") {
    python run_agent.py work --days $Days
} else {
    python run_agent.py $Mode
}

Write-Host ""
Write-Host "$Cyan========================================$Reset"
Write-Host "  Agent session completed"
Write-Host "$Cyan========================================$Reset"
Write-Host ""
