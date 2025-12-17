#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Container Security Visualizer...${NC}"

# Get project root directory
PROJECT_ROOT=$(pwd)

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${RED}Stopping all services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# 1. Start Backend
echo -e "${GREEN}[1/3] Starting Backend...${NC}"
# Check if port 8000 is in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8000 is busy, killing existing process..."
    fuser -k 8000/tcp > /dev/null 2>&1
fi

python3 -m backend.main > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID). Logs: tail -f backend.log"

# 2. Start Frontend
echo -e "${GREEN}[2/3] Starting Frontend...${NC}"
cd frontend
# Check if port 8080 is in use
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8080 is busy, killing existing process..."
    fuser -k 8080/tcp > /dev/null 2>&1
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend running (PID: $FRONTEND_PID). Logs: tail -f frontend.log"

# Wait a moment for services to initialize
sleep 3

# 3. Start Collector
echo -e "${GREEN}[3/3] Starting Collector...${NC}"
echo -e "${RED}NOTE: Collector requires sudo privileges for eBPF${NC}"

# We use the current directory as PYTHONPATH so it can find 'utilities'
# We use the system python3 assuming bcc is installed there, or the venv python if bcc is available
if [ -d ".venv" ]; then
    PYTHON_EXEC=".venv/bin/python3"
    # Check if bcc is available in venv, otherwise fall back to system python
    if ! $PYTHON_EXEC -c "import bcc" >/dev/null 2>&1; then
        echo "bcc not found in venv, trying system python..."
        PYTHON_EXEC="python3"
    fi
else
    PYTHON_EXEC="python3"
fi

echo "Using Python executable: $PYTHON_EXEC"
sudo PYTHONPATH=$PROJECT_ROOT $PYTHON_EXEC collector/collector.py

# When collector exits (Ctrl+C), cleanup will be called via trap
cleanup
