# Private GitHub Setup - Quick Start Guide

## ✅ Privacy Guarantee
- Your repository will be **100% PRIVATE**
- Only YOU can see it
- Free for all GitHub users
- You control who (if anyone) can access it
- Make public on presentation day (optional)

---

## 🚀 Step-by-Step Setup (15 minutes)

### Step 1: Create GitHub Account (if you don't have one)

1. Go to https://github.com
2. Click "Sign up"
3. Use your email (student email recommended for free perks)
4. Choose a username (can be professional or personal)
5. Verify your email

**Student Benefits** (optional):
- Visit https://education.github.com/pack
- Get GitHub Pro free (unlimited private repos)
- Plus other student developer tools

---

### Step 2: Create Private Repository

1. Log in to GitHub
2. Click the **"+"** button (top right) → "New repository"
3. Fill in:
   - **Repository name**: `nursing-research-agents` (or your choice)
   - **Description**: "Healthcare improvement project - Nursing Residency"
   - **⚠️ IMPORTANT**: Select **"Private"** (not Public!)
   - Check "Add a README file"
4. Click **"Create repository"**

**Screenshot of what to look for:**
```
◉ Private  ← MAKE SURE THIS IS SELECTED!
○ Public
```

---

### Step 3: Prepare Your Project

Run these commands on your desktop:

```bash
cd /Users/hdz_agents/Projects/agno

# Create .gitignore (tells git what NOT to upload)
cat > .gitignore << 'EOF'
# Virtual environment (too large, reinstall on each computer)
.venv/
__pycache__/
*.pyc
*.pyo

# Environment variables (API keys - NEVER commit these!)
.env
.env.local

# Database files (contains conversation history - optional to exclude)
tmp/
*.db
*.sqlite

# System files
.DS_Store
.idea/
.vscode/

# Log files
*.log

# Large files we don't need
libs/agno/agno/vectordb/*/data/
EOF

# Check what will be uploaded (should NOT show .venv or .env)
git status
```

---

### Step 4: Upload to GitHub

```bash
# Initialize git in your project
git init
git branch -M main

# Add your files
git add .

# Create first commit
git commit -m "Initial setup - nursing research project agents"

# Connect to GitHub (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nursing-research-agents.git

# Push to GitHub
git push -u origin main
```

**GitHub will ask for authentication:**
- Option 1: Username + Personal Access Token (recommended)
- Option 2: GitHub CLI
- Option 3: SSH key

**To create Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Give it a name: "Nursing Project"
4. Check: ☑ repo (full control)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

---

### Step 5: Verify Privacy

1. Go to your repository on GitHub
2. Look for 🔒 **Private** badge next to repo name
3. Check: Settings → Danger Zone → "Change repository visibility"
4. Should say "This repository is currently private"

✅ **You're secure!** Nobody can see your project.

---

### Step 6: Set Up on Laptop (When Ready)

On your laptop, run:

```bash
# Clone your private repository
git clone https://github.com/YOUR_USERNAME/nursing-research-agents.git
cd nursing-research-agents

# Install dependencies
./scripts/dev_setup.sh

# Create .env file with your API keys (NOT uploaded to GitHub)
nano .env
```

In the `.env` file, paste:
```
OPENAI_API_KEY=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
EXA_API_KEY=f786797a-3063-4869-ab3f-bb95b282f8ab
SERP_API_KEY=cf91e3f9c1ba39340e3b4dc3a905215d78790c2f9004520209b35878921f8a7b
```

Save and run:
```bash
./start_nursing_project.sh
```

---

## 📅 Daily Workflow

### On Desktop (after making changes):
```bash
cd /Users/hdz_agents/Projects/agno

# See what changed
git status

# Add changes
git add .

# Commit with message describing what you did
git commit -m "Added PICOT question for fall prevention"

# Upload to GitHub
git push
```

### On Laptop (before starting work):
```bash
cd ~/nursing-research-agents  # or wherever you cloned it

# Download latest changes
git pull

# Start working
./start_nursing_project.sh
```

---

## 🔒 Security Checklist

Before pushing to GitHub, verify:

- [ ] Repository is set to **Private**
- [ ] `.gitignore` file exists
- [ ] `.env` file is NOT in git (run `git status` to check)
- [ ] API keys are in `.env` file, not in Python files
- [ ] You're using Personal Access Token (not password)

---

## 🎓 For Presentation Day (June 2026)

If you want to share your code:

**Option 1: Keep Private, Share Access**
```
Settings → Collaborators → Add people
(Add instructors/classmates by username)
```

**Option 2: Make Public Temporarily**
```
Settings → Danger Zone → Change visibility → Make public
```

**Option 3: Keep Private, Export Code**
```
Download ZIP from GitHub
Share the ZIP file
```

---

## 🆘 Common Issues & Solutions

### "Authentication failed"
**Solution**: Use Personal Access Token, not password
- Create token at: GitHub → Settings → Developer settings → Tokens
- Use token as password when prompted

### "I see my .env file on GitHub!"
**Solution**: Remove it immediately
```bash
# Remove from git (keeps local copy)
git rm --cached .env
git commit -m "Remove API keys"
git push

# Make sure .gitignore includes .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore"
git push
```

### "My repository is public!"
**Solution**: Change to private
```
Settings → Danger Zone → Change visibility → Make private
```

### "Conflict when pulling"
**Solution**: Commit your local changes first
```bash
git add .
git commit -m "My local changes"
git pull
# Fix any conflicts, then push
git push
```

---

## 📱 GitHub Mobile App

You can also check your project from your phone:
- Download "GitHub" app
- View code (read-only)
- Check what you committed
- See project history

---

## ✅ Benefits Summary

### With Private GitHub, You Get:

1. **Privacy**: 100% private until you decide otherwise
2. **Backup**: Your work is safe in the cloud
3. **Version History**: Can see/restore any previous version
4. **Multi-Computer**: Work from desktop, laptop, library computer
5. **Collaboration**: Can add group members if needed
6. **Professional**: Industry-standard tool
7. **Free**: Completely free for students
8. **Presentation**: Easy to share on presentation day

---

## 🎯 You're Ready!

Follow these steps and you'll have:
- ✅ Private, secure repository
- ✅ Easy sync between computers
- ✅ Automatic backup
- ✅ Professional setup for your 7-month project

**Questions?** Just ask! I'm here to help you set it up. 🏥

---

## Quick Reference Card

```bash
# Daily Commands Cheat Sheet

# Morning routine (before working):
git pull

# Evening routine (after working):
git add .
git commit -m "What I did today"
git push

# Check status anytime:
git status

# See history:
git log

# That's it! Only 5 commands you need to know.
```

