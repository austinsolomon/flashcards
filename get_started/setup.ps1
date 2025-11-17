# Automation Architecture Setup Script for Windows
# Installs all dependencies needed to run the automation examples
# Run in PowerShell as Administrator (for some installations)

# Requires PowerShell 5.1 or higher

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check if command exists
function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Install Chocolatey
function Install-Chocolatey {
    Write-Header "Checking Chocolatey Package Manager"

    if (Test-CommandExists choco) {
        Write-Success "Chocolatey is already installed"
    } else {
        Write-Info "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "Chocolatey installed"
    }
}

# Check and install Python
function Install-Python {
    Write-Header "Checking Python Installation"

    if (Test-CommandExists python) {
        $pythonVersion = (python --version 2>&1) -replace 'Python ', ''
        $versionParts = $pythonVersion.Split('.')
        $major = [int]$versionParts[0]
        $minor = [int]$versionParts[1]

        if ($major -ge 3 -and $minor -ge 10) {
            Write-Success "Python $pythonVersion is installed (>= 3.10)"
        } else {
            Write-Warning "Python $pythonVersion found, but 3.10+ is recommended"
        }
    } else {
        Write-Info "Python not found. Installing Python 3.11..."
        choco install python311 -y
        refreshenv
        Write-Success "Python installed"
    }
}

# Check and install Node.js
function Install-NodeJS {
    Write-Header "Checking Node.js Installation"

    if (Test-CommandExists node) {
        $nodeVersion = node --version
        Write-Success "Node.js $nodeVersion is installed"
    } else {
        Write-Info "Node.js not found. Installing..."
        choco install nodejs -y
        refreshenv
        Write-Success "Node.js installed"
    }

    if (Test-CommandExists npm) {
        $npmVersion = npm --version
        Write-Success "npm $npmVersion is installed"
    } else {
        Write-Error "npm not found. This should have been installed with Node.js"
        exit 1
    }
}

# Create Python virtual environment
function Setup-PythonVenv {
    Write-Header "Setting Up Python Virtual Environment"

    if (-not (Test-Path "venv")) {
        Write-Info "Creating virtual environment..."
        python -m venv venv
        Write-Success "Virtual environment created"
    } else {
        Write-Success "Virtual environment already exists"
    }

    # Activate virtual environment
    & .\venv\Scripts\Activate.ps1

    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip setuptools wheel --quiet
    Write-Success "pip upgraded"
}

# Install Python dependencies
function Install-PythonDeps {
    Write-Header "Installing Python Dependencies"

    if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
        Write-Error "Virtual environment not found. Run setup again."
        exit 1
    }

    & .\venv\Scripts\Activate.ps1

    # Install core dependencies
    Write-Info "Installing core Python packages..."
    pip install --quiet langchain langchain-anthropic langchain-openai langchain-community
    pip install --quiet langgraph
    pip install --quiet python-dotenv requests httpx
    pip install --quiet fastapi uvicorn
    pip install --quiet pydantic pydantic-settings

    # Install optional but useful packages
    Write-Info "Installing additional packages..."
    pip install --quiet beautifulsoup4 lxml
    pip install --quiet pytest pytest-asyncio
    pip install --quiet black ruff

    Write-Success "Python dependencies installed"
}

# Install n8n
function Install-N8N {
    Write-Header "Installing n8n"

    if (Test-CommandExists n8n) {
        Write-Success "n8n is already installed"
    } else {
        Write-Info "Installing n8n globally..."
        npm install -g n8n
        Write-Success "n8n installed"
    }

    Write-Info "You can start n8n later with: n8n start"
}

# Create environment file template
function Create-EnvTemplate {
    Write-Header "Creating Environment Configuration"

    if (-not (Test-Path ".env")) {
        $envContent = @'
# ===================================
# Automation Architecture - Environment Variables
# ===================================
# Copy this to .env and fill in your actual API keys

# =========================
# AI/LLM API Keys
# =========================

# Anthropic Claude API (Required for Tier 2+ examples)
# Get your key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API (Optional - for GPT-4 Vision examples)
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# =========================
# Data & Search APIs
# =========================

# Serper API (Google Search - for GTM research examples)
# Get your key from: https://serper.dev/
SERPER_API_KEY=your_serper_api_key_here

# Proxycurl API (LinkedIn data - for GTM examples)
# Get your key from: https://nubela.co/proxycurl/
PROXYCURL_API_KEY=your_proxycurl_api_key_here

# Clearbit API (Company enrichment - for GTM examples)
# Get your key from: https://clearbit.com/
CLEARBIT_API_KEY=your_clearbit_api_key_here

# =========================
# CRM & Productivity
# =========================

# HubSpot API (Optional - for GTM CRM integration)
# Get your key from: HubSpot Settings > Integrations > API Key
HUBSPOT_API_KEY=your_hubspot_api_key_here

# Google Sheets API (Optional - for data sources)
GOOGLE_SHEETS_CREDENTIALS_PATH=C:\path\to\credentials.json

# =========================
# Email Configuration
# =========================

# SMTP Settings (for email automation)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password_here

# From/To Emails
FROM_EMAIL=automations@yourcompany.com
USER_EMAIL=you@yourcompany.com

# =========================
# Obsidian (BR2 Examples)
# =========================

# Obsidian Vault Path (absolute path to your vault)
OBSIDIAN_VAULT_PATH=C:\Users\YourName\Documents\ObsidianVault

# Obsidian Local REST API (if using the plugin)
# Install plugin: https://github.com/coddingtonbear/obsidian-local-rest-api
OBSIDIAN_LOCAL_API=http://localhost:27123

# =========================
# Unreal Engine (UE5 Examples)
# =========================

# Unreal Engine Project Path
UE5_PROJECT_PATH=C:\Users\YourName\Documents\UnrealProjects\MyGame

# Cloud Storage for Backups
CLOUD_STORAGE_URL=https://api.dropbox.com/2/files

# =========================
# Calendar APIs
# =========================

# Google Calendar API
CALENDAR_API_URL=https://www.googleapis.com/calendar/v3

# =========================
# Logging & Monitoring
# =========================

# Log file paths
GTM_LOG_PATH=C:\logs\gtm_automation.log
BR2_LOG_PATH=C:\logs\br2_automation.log
BACKUP_LOG_PATH=C:\logs\ue5_backup.log

# =========================
# n8n Configuration
# =========================

# n8n Webhook Base URL (for production)
N8N_WEBHOOK_URL=http://localhost:5678

# n8n Basic Auth (optional, for security)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password_here
'@
        Set-Content -Path ".env" -Value $envContent
        Write-Success "Environment template created: .env"
        Write-Warning "⚠️  IMPORTANT: Edit .env and add your API keys before running examples"
    } else {
        Write-Success ".env file already exists"
    }
}

# Create project directories
function Create-Directories {
    Write-Header "Creating Project Directories"

    # n8n data directory
    $n8nDir = "$env:USERPROFILE\.n8n"
    if (-not (Test-Path $n8nDir)) {
        New-Item -ItemType Directory -Path $n8nDir -Force | Out-Null
    }

    # Logs directory
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }

    # Temporary files
    if (-not (Test-Path "tmp")) {
        New-Item -ItemType Directory -Path "tmp" -Force | Out-Null
    }

    Write-Success "Project directories created"
}

# Display next steps
function Show-NextSteps {
    Write-Header "Setup Complete! 🎉"

    Write-Host "All dependencies installed successfully!`n" -ForegroundColor Green

    Write-Host "📋 Next Steps:`n" -ForegroundColor Blue

    Write-Host "1. " -NoNewline
    Write-Host "Activate Python virtual environment:" -ForegroundColor Yellow
    Write-Host "   .\venv\Scripts\Activate.ps1"
    Write-Host ""

    Write-Host "2. " -NoNewline
    Write-Host "Configure your API keys:" -ForegroundColor Yellow
    Write-Host "   Edit the .env file and add your API keys"
    Write-Host "   notepad .env"
    Write-Host ""

    Write-Host "3. " -NoNewline
    Write-Host "Choose your quickstart path:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Option A: iOS Shortcuts (Tier 0) - 5 minutes" -ForegroundColor Green
    Write-Host "   - No APIs needed, works offline"
    Write-Host "   - See: gtm\tier_0\tier_0_toy_ios_shortcuts_gtm_lead_capture.md"
    Write-Host ""
    Write-Host "   Option B: n8n Workflow (Tier 1) - 30 minutes" -ForegroundColor Green
    Write-Host "   - Start n8n: n8n start"
    Write-Host "   - Open: http://localhost:5678"
    Write-Host "   - Import: gtm\tier_1\tier_1_toy_n8n_gtm_daily_metrics.json"
    Write-Host ""
    Write-Host "   Option C: AI-Enhanced (Tier 2) - 1 hour" -ForegroundColor Green
    Write-Host "   - Requires: ANTHROPIC_API_KEY in .env"
    Write-Host "   - Start n8n and import: gtm\tier_2\tier_2_toy_n8n_gtm_email_classifier.json"
    Write-Host ""
    Write-Host "   Option D: Agent (Tier 3) - 1 hour" -ForegroundColor Green
    Write-Host "   - Requires: ANTHROPIC_API_KEY, SERPER_API_KEY in .env"
    Write-Host "   - Run: python gtm\tier_3\tier_3_toy_langchain_gtm_prospect_finder.py"
    Write-Host ""

    Write-Host "4. " -NoNewline
    Write-Host "Read the Quick Start Guide:" -ForegroundColor Yellow
    Write-Host "   Get-Content QUICKSTART.md"
    Write-Host ""

    Write-Host "📚 Documentation:" -ForegroundColor Blue
    Write-Host "   - EXAMPLES_SUMMARY.md - Complete inventory of all examples"
    Write-Host "   - README.md - Architecture overview"
    Write-Host ""

    Write-Host "🔧 Useful Commands:" -ForegroundColor Blue
    Write-Host "   - Start n8n:          n8n start"
    Write-Host "   - Activate Python:    .\venv\Scripts\Activate.ps1"
    Write-Host "   - Test Python setup:  python -c 'import langchain; print(\""✓ LangChain installed\"")'"
    Write-Host ""

    Write-Info "Need help? See QUICKSTART.md or individual example setup guides"
}

# Main setup flow
function Main {
    Clear-Host
    Write-Header "Automation Architecture - Setup Script (Windows)"

    Write-Host "This script will install:"
    Write-Host "  • Python 3.11 and virtual environment"
    Write-Host "  • Node.js and npm"
    Write-Host "  • n8n workflow automation platform"
    Write-Host "  • LangChain, LangGraph, and AI libraries"
    Write-Host "  • Environment configuration template"
    Write-Host ""

    if (-not (Test-Administrator)) {
        Write-Warning "Some installations may require administrator privileges"
        Write-Host "Consider running PowerShell as Administrator for best results"
        Write-Host ""
    }

    $continue = Read-Host "Continue? (y/n)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Warning "Setup cancelled"
        exit 0
    }

    # Run setup steps
    Install-Chocolatey
    Install-Python
    Install-NodeJS
    Setup-PythonVenv
    Install-PythonDeps
    Install-N8N
    Create-EnvTemplate
    Create-Directories

    # Success!
    Show-NextSteps
}

# Run main function
Main
