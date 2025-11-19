#!/bin/bash
# iPhone Compliance Agent - Quick Run Script

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  iPhone Compliance Agent${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "   Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "   Creating from template..."
    cp .env.example .env
    echo "   Please edit .env and add your ANTHROPIC_API_KEY"
    exit 1
fi

# Menu
echo "Select mode:"
echo ""
echo "  1. Tier 4 - Multi-Agent System (automated testing)"
echo "  2. Tier 5 - Full Orchestrator (with human review)"
echo "  3. Test emulator connection"
echo "  4. Interactive Python shell"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Running Tier 4 Multi-Agent Compliance Test...${NC}"
        echo ""
        python compliance_agent.py
        ;;
    2)
        echo ""
        echo -e "${GREEN}Running Tier 5 Orchestrated Workflow...${NC}"
        echo ""
        python orchestrator.py
        ;;
    3)
        echo ""
        echo -e "${GREEN}Testing emulator connection...${NC}"
        echo ""
        python emulator/ios_emulator.py
        ;;
    4)
        echo ""
        echo -e "${GREEN}Starting interactive Python shell...${NC}"
        echo ""
        echo "Available modules:"
        echo "  - from compliance_agent import run_compliance_test"
        echo "  - from orchestrator import ComplianceOrchestrator"
        echo "  - from emulator.ios_emulator import iOSEmulator"
        echo ""
        python -i -c "
import sys
sys.path.append('.')
from compliance_agent import run_compliance_test, COMPLIANCE_STANDARDS
from orchestrator import ComplianceOrchestrator
print('Ready! Try: run_compliance_test(\"Instagram\")')
"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
