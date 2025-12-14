#!/bin/bash
# sync_finish.sh - Run this when you FINISH working
# Commits and pushes changes to GitHub

echo "🔴 Finishing work session..."

# Check if there are any changes
if [ -z "$(git status --porcelain)" ]; then
    echo "📝 No changes to commit. You're all set!"
    exit 0
fi

# Show what changed
echo "📋 Files changed:"
git status --short

# Ask for commit message
echo ""
read -p "📝 Describe what you changed: " commit_message

if [ -z "$commit_message" ]; then
    commit_message="Update from $(date +'%Y-%m-%d %H:%M')"
    echo "Using default message: $commit_message"
fi

# Add, commit, and push
echo "💾 Saving changes..."
git add .
git commit -m "$commit_message"

echo "☁️ Pushing to GitHub..."
git push

if [ $? -eq 0 ]; then
    echo "✅ All done! Your changes are synced to GitHub."
else
    echo "❌ Push failed. You may need to pull first."
    echo "Run: git pull"
fi
