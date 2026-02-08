#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Function to handle script termination
cleanup() {
    echo "Stopping servers..."
    # Check if PIDs are set before killing
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID
    fi
    exit
}

# Trap SIGINT (Ctrl+C) to cleanup
# Trap signals for cleanup
trap cleanup SIGINT SIGTERM SIGHUP

# Start Backend
echo "Starting Backend..."
# Run from the root directory
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for servers to initialize (5 seconds)
sleep 5

# Open Browser (macOS uses 'open')
echo "Opening Browser..."
open http://localhost:3000/

# Keep script running to maintain processes
wait $BACKEND_PID $FRONTEND_PID
