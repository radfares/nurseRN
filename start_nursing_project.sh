#!/bin/bash
# Easy launcher for Nursing Research Project Assistant

cd /Users/hdz_agents/Projects/agno

# Activate virtual environment
source .venv/bin/activate

# Set OpenAI API key
export OPENAI_API_KEY='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'

echo "🏥 Starting Nursing Research Project Assistant..."
echo ""

# Run with python3
python3 run_nursing_project.py

