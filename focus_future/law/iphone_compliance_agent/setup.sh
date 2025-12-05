#!/bin/bash
# iPhone Compliance Agent - Setup Script

echo "════════════════════════════════════════════════════════════════════"
echo "  iPhone Compliance Agent - Setup"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ Error: This setup requires macOS for iOS Simulator${NC}"
    echo "   For Android testing, use a different setup script"
    exit 1
fi

echo "Step 1: Checking prerequisites..."
echo "──────────────────────────────────────────────────────────────────"
echo ""

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo -e "${RED}❌ Xcode not found${NC}"
    echo "   Please install Xcode from the App Store"
    echo "   Then run: xcode-select --install"
    exit 1
else
    echo -e "${GREEN}✅ Xcode installed${NC}"
    xcodebuild -version | head -n 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "   Please install Node.js from: https://nodejs.org/"
    exit 1
else
    echo -e "${GREEN}✅ Node.js installed${NC}"
    node --version
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "   Please install Python 3.9 or later"
    exit 1
else
    echo -e "${GREEN}✅ Python installed${NC}"
    python3 --version
fi

echo ""
echo "Step 2: Installing Appium..."
echo "──────────────────────────────────────────────────────────────────"
echo ""

# Install Appium
if ! command -v appium &> /dev/null; then
    echo "Installing Appium globally..."
    npm install -g appium
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install Appium${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Appium already installed${NC}"
    appium --version
fi

# Install XCUITest driver
echo ""
echo "Installing XCUITest driver for iOS..."
appium driver install xcuitest
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ XCUITest driver installed${NC}"
else
    echo -e "${YELLOW}⚠️  XCUITest driver may already be installed${NC}"
fi

echo ""
echo "Step 3: Setting up Python environment..."
echo "──────────────────────────────────────────────────────────────────"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install Python dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python dependencies installed${NC}"

echo ""
echo "Step 4: Configuring environment..."
echo "──────────────────────────────────────────────────────────────────"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your ANTHROPIC_API_KEY${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create directories
echo "Creating directory structure..."
mkdir -p reports/screenshots
mkdir -p agents
mkdir -p utils

echo ""
echo "Step 5: Testing installation..."
echo "──────────────────────────────────────────────────────────────────"
echo ""

# Test iOS Simulator list
echo "Available iOS Simulators:"
xcrun simctl list devices | grep "iPhone"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and add your ANTHROPIC_API_KEY:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Start Appium server (in a separate terminal):"
echo "   ${YELLOW}appium --allow-cors${NC}"
echo ""
echo "3. Run the compliance agent:"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}python compliance_agent.py${NC}"
echo ""
echo "Or run the full orchestrator:"
echo "   ${YELLOW}python orchestrator.py${NC}"
echo ""
echo "For more information, see README.md"
echo ""
