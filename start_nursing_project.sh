#!/bin/bash
# Easy launcher for Nursing Research Project Assistant

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH to include vendored agno library
export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno"

# Load environment variables from .env file (if it exists)
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "⚠️  Warning: .env file not found. Some features may not work."
    echo "   Create a .env file with your API keys (see .env.example)"
fi

echo "🏥 Starting Nursing Research Project Assistant..."
echo ""

# Run with python3
python3 run_nursing_project.py

