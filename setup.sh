#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up AI Resume Matcher project...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create project directory structure
echo -e "${YELLOW}Creating project directory structure...${NC}"

mkdir -p backend/app/routers backend/app/schemas
mkdir -p frontend/components frontend/utils

# Copy files to respective directories
echo -e "${YELLOW}Creating project files...${NC}"

# Create files from artifact templates here
# ...

# Set executable permissions for script files
chmod +x setup.sh

echo -e "${YELLOW}Setting up environment variables...${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "# Environment variables for AI Resume Matcher" > .env
    echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
    echo -e "${YELLOW}Created .env file. Please edit it and add your Gemini API key.${NC}"
else
    echo -e "${YELLOW}.env file already exists. Please make sure your Gemini API key is set.${NC}"
fi

echo -e "${GREEN}Setup completed!${NC}"
echo -e "${GREEN}To start the application, run:${NC}"
echo -e "${YELLOW}docker-compose up -d${NC}"
echo -e "${GREEN}Then visit http://localhost:8501 in your browser.${NC}"