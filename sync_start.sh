#!/bin/bash
# sync_start.sh - Run this when you START working
# Pulls latest changes from GitHub

echo "🟢 Starting work session..."
echo "📥 Pulling latest changes from GitHub..."

git pull

if [ $? -eq 0 ]; then
    echo "✅ Ready to work! Your project is up to date."
else
    echo "❌ Pull failed. You may need to resolve conflicts."
    echo "Run: git status"
fi
