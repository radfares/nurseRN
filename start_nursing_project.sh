#!/bin/bash
# Easy launcher for Nursing Research Project Assistant

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Load environment variables from .env file
set -a
source .env
set +a

echo "🏥 Starting Nursing Research Project Assistant..."
echo ""

# Run with python3
python3 run_nursing_project.py

