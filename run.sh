# Define colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Display welcome message
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  Secure Access Surveillance System    ${NC}"
echo -e "${GREEN}=======================================${NC}"

# Check if venv directory exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv --system-site-packages venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    # Activate virtual environment
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Run the main application
echo -e "${YELLOW}Starting the application...${NC}"
python main.py

# Deactivate virtual environment when done
deactivate