#!/bin/bash

# Automation Architecture Setup Script
# Installs all dependencies needed to run the automation examples
# Compatible with macOS and Linux

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Detected macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Detected Linux"
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew (macOS only)
install_homebrew() {
    if [[ "$OS" == "macos" ]]; then
        if ! command_exists brew; then
            print_info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            print_success "Homebrew installed"
        else
            print_success "Homebrew already installed"
        fi
    fi
}

# Check and install Python 3.10+
install_python() {
    print_header "Checking Python Installation"

    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        REQUIRED_VERSION="3.10"

        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python $PYTHON_VERSION is installed (>= 3.10)"
            PYTHON_CMD="python3"
        else
            print_warning "Python $PYTHON_VERSION found, but 3.10+ is recommended"
            PYTHON_CMD="python3"
        fi
    else
        print_info "Python 3 not found. Installing..."

        if [[ "$OS" == "macos" ]]; then
            brew install python@3.11
        elif [[ "$OS" == "linux" ]]; then
            sudo apt-get update
            sudo apt-get install -y python3.11 python3.11-venv python3-pip
        fi

        PYTHON_CMD="python3"
        print_success "Python installed"
    fi
}

# Check and install Node.js and npm
install_nodejs() {
    print_header "Checking Node.js Installation"

    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION is installed"
    else
        print_info "Node.js not found. Installing..."

        if [[ "$OS" == "macos" ]]; then
            brew install node
        elif [[ "$OS" == "linux" ]]; then
            # Install Node.js 20.x
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
        fi

        print_success "Node.js installed"
    fi

    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION is installed"
    else
        print_error "npm not found. This should have been installed with Node.js"
        exit 1
    fi
}

# Create Python virtual environment
setup_python_venv() {
    print_header "Setting Up Python Virtual Environment"

    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    print_success "pip upgraded"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"

    if [ ! -f "venv/bin/activate" ]; then
        print_error "Virtual environment not found. Run setup again."
        exit 1
    fi

    source venv/bin/activate

    # Install core dependencies
    print_info "Installing core Python packages..."
    pip install -q langchain langchain-anthropic langchain-openai langchain-community
    pip install -q langgraph
    pip install -q python-dotenv requests httpx
    pip install -q fastapi uvicorn
    pip install -q pydantic pydantic-settings

    # Install optional but useful packages
    print_info "Installing additional packages..."
    pip install -q beautifulsoup4 lxml
    pip install -q pytest pytest-asyncio
    pip install -q black ruff  # Code formatting

    print_success "Python dependencies installed"
}

# Install n8n
install_n8n() {
    print_header "Installing n8n"

    if command_exists n8n; then
        N8N_VERSION=$(n8n --version 2>/dev/null || echo "installed")
        print_success "n8n is already installed"
    else
        print_info "Installing n8n globally..."
        npm install -g n8n
        print_success "n8n installed"
    fi

    print_info "You can start n8n later with: n8n start"
}

# Create environment file template
create_env_template() {
    print_header "Creating Environment Configuration"

    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
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
GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/credentials.json

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
OBSIDIAN_VAULT_PATH=/Users/yourname/Documents/ObsidianVault

# Obsidian Local REST API (if using the plugin)
# Install plugin: https://github.com/coddingtonbear/obsidian-local-rest-api
OBSIDIAN_LOCAL_API=http://localhost:27123

# =========================
# Unreal Engine (UE5 Examples)
# =========================

# Unreal Engine Project Path
UE5_PROJECT_PATH=/Users/yourname/UnrealProjects/MyGame

# Cloud Storage for Backups
CLOUD_STORAGE_URL=https://api.dropbox.com/2/files
# or
# CLOUD_STORAGE_URL=https://storage.googleapis.com/upload/storage/v1/b/my-bucket

# =========================
# Calendar APIs
# =========================

# Google Calendar API
CALENDAR_API_URL=https://www.googleapis.com/calendar/v3

# =========================
# Logging & Monitoring
# =========================

# Log file paths
GTM_LOG_PATH=/var/log/gtm_automation.log
BR2_LOG_PATH=/var/log/br2_automation.log
BACKUP_LOG_PATH=/var/log/ue5_backup.log

# =========================
# n8n Configuration
# =========================

# n8n Webhook Base URL (for production)
N8N_WEBHOOK_URL=http://localhost:5678

# n8n Basic Auth (optional, for security)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password_here
EOF
        print_success "Environment template created: .env"
        print_warning "⚠️  IMPORTANT: Edit .env and add your API keys before running examples"
    else
        print_success ".env file already exists"
    fi
}

# Create project directories
create_directories() {
    print_header "Creating Project Directories"

    # n8n data directory
    mkdir -p ~/.n8n

    # Logs directory
    mkdir -p logs

    # Temporary files
    mkdir -p tmp

    print_success "Project directories created"
}

# Display next steps
show_next_steps() {
    print_header "Setup Complete! 🎉"

    echo -e "${GREEN}All dependencies installed successfully!${NC}\n"

    echo -e "${BLUE}📋 Next Steps:${NC}\n"

    echo "1. ${YELLOW}Activate Python virtual environment:${NC}"
    echo "   source venv/bin/activate"
    echo ""

    echo "2. ${YELLOW}Configure your API keys:${NC}"
    echo "   Edit the .env file and add your API keys"
    echo "   nano .env"
    echo ""

    echo "3. ${YELLOW}Choose your quickstart path:${NC}"
    echo ""
    echo "   ${GREEN}Option A: iOS Shortcuts (Tier 0) - 5 minutes${NC}"
    echo "   - No APIs needed, works offline"
    echo "   - See: gtm/tier_0/tier_0_toy_ios_shortcuts_gtm_lead_capture.md"
    echo ""
    echo "   ${GREEN}Option B: n8n Workflow (Tier 1) - 30 minutes${NC}"
    echo "   - Start n8n: n8n start"
    echo "   - Open: http://localhost:5678"
    echo "   - Import: gtm/tier_1/tier_1_toy_n8n_gtm_daily_metrics.json"
    echo ""
    echo "   ${GREEN}Option C: AI-Enhanced (Tier 2) - 1 hour${NC}"
    echo "   - Requires: ANTHROPIC_API_KEY in .env"
    echo "   - Start n8n and import: gtm/tier_2/tier_2_toy_n8n_gtm_email_classifier.json"
    echo ""
    echo "   ${GREEN}Option D: Agent (Tier 3) - 1 hour${NC}"
    echo "   - Requires: ANTHROPIC_API_KEY, SERPER_API_KEY in .env"
    echo "   - Run: python gtm/tier_3/tier_3_toy_langchain_gtm_prospect_finder.py"
    echo ""

    echo "4. ${YELLOW}Read the Quick Start Guide:${NC}"
    echo "   cat QUICKSTART.md"
    echo ""

    echo "5. ${YELLOW}Explore complete use cases:${NC}"
    echo "   - GTM Lead Research: gtm/tier_1/tier_1_cldchoice_gtm_lead_research_setup.md"
    echo "   - BR2 Capture: br2/tier_0/tier_0_cldchoice_br2_capture.md"
    echo "   - UE5 Assets: ue5/tier_3/tier_3_cldchoice_ue5_procedural_gen.py"
    echo ""

    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "   - EXAMPLES_SUMMARY.md - Complete inventory of all examples"
    echo "   - README.md - Architecture overview"
    echo ""

    echo -e "${BLUE}🔧 Useful Commands:${NC}"
    echo "   - Start n8n:          n8n start"
    echo "   - Activate Python:    source venv/bin/activate"
    echo "   - Test Python setup:  python -c 'import langchain; print(\"✓ LangChain installed\")'"
    echo ""

    print_info "Need help? See QUICKSTART.md or individual example setup guides"
}

# Main setup flow
main() {
    clear
    print_header "Automation Architecture - Setup Script"

    echo "This script will install:"
    echo "  • Python 3.10+ and virtual environment"
    echo "  • Node.js and npm"
    echo "  • n8n workflow automation platform"
    echo "  • LangChain, LangGraph, and AI libraries"
    echo "  • Environment configuration template"
    echo ""

    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Setup cancelled"
        exit 0
    fi

    # Run setup steps
    detect_os
    install_homebrew
    install_python
    install_nodejs
    setup_python_venv
    install_python_deps
    install_n8n
    create_env_template
    create_directories

    # Success!
    show_next_steps
}

# Run main function
main
