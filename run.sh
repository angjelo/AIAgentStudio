#!/bin/bash

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        echo "OPENAI_API_KEY=" > .env
        echo "ANTHROPIC_API_KEY=" >> .env
    fi
    echo "Please edit the .env file to add your API keys."
fi

# Start the PostgreSQL database with Docker Compose
echo "Starting PostgreSQL database..."
docker-compose up -d

# Run the application
echo "Starting AI Agent Studio..."
streamlit run app.py

# Trap SIGINT to clean up when terminating with Ctrl+C
trap 'echo "Stopping services..."; docker-compose down' INT