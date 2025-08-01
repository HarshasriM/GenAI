#!/bin/bash

#Start the backend server
echo "Starting the backend server"
nohup uvicorn backend.main:app --reload &

#Wait for the backend server to start
sleep 5

#Start the frontend server
echo "Starting the frontend server"
streamlit run frontend/AI_chatbot.py