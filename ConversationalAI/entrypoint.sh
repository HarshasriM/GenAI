#!/bin/bash

# Start the backend
echo "Starting the backend server..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Wait for the backend to start
sleep 5

# Start the frontend
echo "Starting the frontend application..."
streamlit run frontend/streamlit.py

