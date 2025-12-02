#!/bin/bash

# Simple virtual environment setup script for the nurseRN project
# This script creates and activates a Python virtual environment and installs required packages

echo "Setting up Python virtual environment for nurseRN project..."

# Check if virtual environment already exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Removing it first..."
    rm -rf .venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Check if virtual environment was created successfully
if [ ! -d ".venv" ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment and install packages
echo "Activating virtual environment and installing packages..."
source .venv/bin/activate

# Upgrade pip first
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install required packages from requirements.txt
echo "Installing required packages..."
python -m pip install -r requirements.txt

# Install additional packages needed for the project
echo "Installing additional packages..."
python -m pip install google-genai==1.17.0
python -m pip install mcp==1.9.2
python -m pip install fastmcp
python -m pip install crawl4ai==0.6.3
python -m pip install firecrawl-py==3.4.0
python -m pip install chonkie[st] chonkie
python -m pip install pylance
python -m pip install psycopg-binary psycopg psycopg2

echo "Virtual environment setup complete!"
echo "To activate the virtual environment, run: source .venv/bin/activate"
echo "To deactivate, run: deactivate"
