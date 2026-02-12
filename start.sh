#!/bin/bash
# Startup script for the Todo AI Chatbot

echo "Starting Todo AI Chatbot..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "Starting the application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload