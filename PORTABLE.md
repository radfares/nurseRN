# Making Your Nursing Research Agents Portable

## 🎯 Three Ways to Use Your Project Across Multiple Computers

---

## Option 1: Private GitHub Repository (RECOMMENDED) ⭐

### What It Is
GitHub is like Google Drive for code. A **private repository** means ONLY YOU can see it.

### Privacy & Security
- ✅ **100% Private** - Only you can access it
- ✅ **Free for students** - Unlimited private repos
- ✅ **Make public later** - Switch to public on presentation day if you want
- ✅ **Invite collaborators** - Add classmates only if YOU choose
- ✅ **Delete anytime** - Complete control

### How It Works
1. Upload your project to GitHub (private)
2. On any computer: Download it, run setup, start working
3. When you make changes: Push updates to GitHub
4. On other computer: Pull latest changes

### Setup Steps

#### First Time Setup (Desktop):

**Step 1: Create GitHub Account**
```
Go to github.com
Sign up (use your student email for free benefits)
Verify email
```

**Step 2: Create Private Repository**
```
1. Click "New Repository" (green button)
2. Name: "nursing-research-agents" (or any name)
3. Description: "Healthcare improvement project agents"
4. ✅ CHECK "Private" (IMPORTANT!)
5. ✅ CHECK "Add README"
6. Click "Create repository"
```

**Step 3: Upload Your Project**
```bash
cd /Users/hdz_agents/Projects/agno

# Initialize git
git init
git branch -M main

# Add files (excluding sensitive/large files)
git add *.py *.md *.sh

# Commit
git commit -m "Initial setup - nursing research agents"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/nursing-research-agents.git

# Push (will ask for GitHub username/password or token)
git push -u origin main
```

**Step 4: Secure Your API Keys**

Create `.env` file (NOT uploaded to GitHub):
```bash
cat > .env << 'EOF'
OPENAI_API_KEY=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
EXA_API_KEY=f786797a-3063-4869-ab3f-bb95b282f8ab
SERP_API_KEY=cf91e3f9c1ba39340e3b4dc3a905215d78790c2f9004520209b35878921f8a7b
EOF
```

#### Using on Laptop (or any other computer):

**Step 1: Clone Repository**
```bash
# One-time setup
cd ~/Projects  # or wherever you want it
git clone https://github.com/YOUR_USERNAME/nursing-research-agents.git
cd nursing-research-agents
```

**Step 2: Install Dependencies**
```bash
./scripts/dev_setup.sh
```

**Step 3: Add API Keys**
```bash
# Create .env file with your keys (same as desktop)
nano .env  # paste your API keys
```

**Step 4: Run It**
```bash
./start_nursing_project.sh
```

#### Daily Workflow:

**On Desktop (after making changes):**
```bash
git add *.py *.md
git commit -m "Updated PICOT questions" # or whatever you changed
git push
```

**On Laptop (before starting work):**
```bash
git pull  # Gets latest changes
./start_nursing_project.sh
```

### Pros:
- ✅ **Private & secure**
- ✅ **Version history** (can go back to any previous version)
- ✅ **Works from anywhere** (just need internet to sync)
- ✅ **Professional** (used by developers worldwide)
- ✅ **Backup** (your work is safe in the cloud)
- ✅ **Free**

### Cons:
- ⚠️ Small learning curve (but simple commands)
- ⚠️ Need internet to sync (can work offline, sync later)
- ⚠️ API keys must be added manually on each computer

### Cost: FREE

---

## Option 2: Docker Container 🐳

### What It Is
Docker packages your entire project into a "container" - like a mini computer that runs the same on any machine.

### How It Works
1. Create a Docker image (one time)
2. Copy image to any computer with Docker installed
3. Run container - everything works identically

### Setup Steps

**Create Dockerfile:**
```dockerfile
FROM python:3.12-slim

# Install uv and dependencies
RUN pip install uv

# Copy project
WORKDIR /app
COPY . /app

# Install dependencies
RUN uv venv .venv
RUN . .venv/bin/activate && uv pip install -r libs/agno/requirements.txt
RUN . .venv/bin/activate && uv pip install -e libs/agno[tests]

# Set environment variables (or pass at runtime)
ENV OPENAI_API_KEY=""

# Run command
CMD ["/bin/bash"]
```

**Build Image:**
```bash
docker build -t nursing-agents .
```

**Run on Any Computer:**
```bash
# Install Docker Desktop first (one-time)
# Download from docker.com

# Run your container
docker run -it \
  -e OPENAI_API_KEY='your-key' \
  -v $(pwd)/data:/app/data \
  nursing-agents \
  python3 run_nursing_project.py
```

### Pros:
- ✅ **Identical environment** everywhere
- ✅ **No dependency issues**
- ✅ **Professional approach**

### Cons:
- ⚠️ **Complex setup** (steeper learning curve)
- ⚠️ **Large files** (several GB)
- ⚠️ **Need Docker installed** on each computer
- ⚠️ **Overkill** for simple project

### Cost: FREE (Docker Desktop free for students)

### Recommendation: 
**Skip Docker** - it's more complex than you need. Use GitHub instead.

---

## Option 3: All-in-One Portable Package 📦

### What It Is
A single folder with everything pre-configured. Just copy, setup, and run.

### How It Works
1. Create a clean package with all files
2. Copy to USB drive or cloud storage
3. On any Mac: Extract, run setup script, start working

### Setup Steps

**Create Package (Desktop):**
```bash
cd /Users/hdz_agents/Projects

# Create clean package
mkdir nursing-agents-portable
cd nursing-agents-portable

# Copy essential files
cp ~/Projects/agno/*.py .
cp ~/Projects/agno/*.md .
cp ~/Projects/agno/*.sh .
cp -r ~/Projects/agno/libs .
cp -r ~/Projects/agno/scripts .

# Create setup script
cat > SETUP.sh << 'EOF'
#!/bin/bash
echo "Setting up Nursing Research Agents..."
./scripts/dev_setup.sh

echo ""
echo "Setup complete!"
echo "Create .env file with your API keys, then run:"
echo "./start_nursing_project.sh"
EOF
chmod +x SETUP.sh

# Create .env template
cat > .env.template << 'EOF'
# Copy this to .env and fill in your keys
OPENAI_API_KEY=your-openai-key-here
EXA_API_KEY=your-exa-key-here
SERP_API_KEY=your-serp-key-here
EOF

# Create README
cat > QUICK_START.md << 'EOF'
# Quick Start Guide

1. Run setup (first time only):
   ./SETUP.sh

2. Copy .env.template to .env:
   cp .env.template .env

3. Edit .env with your API keys:
   nano .env

4. Run the agents:
   ./start_nursing_project.sh
EOF

# Create zip
cd ..
zip -r nursing-agents-portable.zip nursing-agents-portable/
```

**Use on Laptop:**
```bash
# Copy nursing-agents-portable.zip to laptop (USB, AirDrop, email)

# Extract
unzip nursing-agents-portable.zip
cd nursing-agents-portable

# Setup
./SETUP.sh

# Add your API keys
cp .env.template .env
nano .env  # paste your keys

# Run
./start_nursing_project.sh
```

### Pros:
- ✅ **Simplest** to understand
- ✅ **No account needed**
- ✅ **Works offline**
- ✅ **Complete control**

### Cons:
- ⚠️ **Manual sync** (must remember to copy updated files)
- ⚠️ **No version history**
- ⚠️ **Large zip file** (~500MB+ with packages)
- ⚠️ **Easy to forget** to sync changes

### Cost: FREE

---

## Comparison Table

| Feature | GitHub (Private) | Docker | All-in-One |
|---------|-----------------|--------|------------|
| **Privacy** | ✅ 100% Private | ✅ Local | ✅ Local |
| **Setup Difficulty** | ⭐⭐ Easy | ⭐⭐⭐⭐⭐ Hard | ⭐ Very Easy |
| **Sync Method** | Automatic (git) | Manual copy | Manual copy |
| **Version History** | ✅ Yes | ❌ No | ❌ No |
| **Internet Required** | For sync only | No | No |
| **File Size** | Small (~1MB) | Large (~2GB) | Medium (~500MB) |
| **Professional** | ✅ Yes | ✅ Yes | ❌ Basic |
| **Backup** | ✅ Cloud | ❌ Manual | ❌ Manual |
| **Cost** | FREE | FREE | FREE |

---

## 🎯 Recommendation for Your Nursing Project

### Use: **Private GitHub** (Option 1) ⭐

**Why:**
1. **Privacy**: Nobody can see it until you want them to
2. **7-month project**: Easy to sync changes over time
3. **Safety**: Your work is backed up automatically
4. **Professional**: Good skill to learn for career
5. **Presentation day**: Can make public to share with instructors

### Keep as Backup: **All-in-One Package** (Option 3)

Create one zip file as backup:
- Store on USB drive
- Keep in cloud storage (Dropbox, iCloud)
- Use if GitHub has issues

### Skip: **Docker** (Option 2)

Too complex for this use case. Docker is great for professional deployment, but overkill for a student project.

---

## 🔒 Security Best Practices

### Never Commit API Keys to GitHub!

**Wrong:**
```python
# DON'T DO THIS in files you commit
api_key = "sk-proj-abc123..."  # ❌ VISIBLE ON GITHUB
```

**Right:**
```python
# DO THIS - read from environment or .env file
import os
api_key = os.getenv("OPENAI_API_KEY")  # ✅ SAFE
```

### .gitignore File

Always have this file to exclude sensitive data:
```
# .gitignore
.env
.venv/
tmp/
*.db
__pycache__/
*.pyc
.DS_Store
```

### Make Repository Private

When creating GitHub repo:
1. ✅ Check "Private" box
2. Don't add collaborators unless needed
3. Can switch to public later if you want

---

## 📅 Timeline for Your Project

### November 2025 (Setup)
- Create private GitHub repo
- Upload initial files
- Test on laptop

### Dec 2025 - Apr 2026 (Development)
- Work on desktop or laptop
- Commit changes regularly
- Pull latest before working

### May 2026 (Finalization)
- Finalize presentation
- Keep repo private

### June 2026 (Presentation Day)
- Present your work
- Optionally: Make repo public to share
- OR: Keep private, just show results

---

## 🆘 Troubleshooting

### "I forgot to push changes from desktop"
```bash
# On desktop
git add .
git commit -m "Latest changes"
git push
```

### "My laptop has old code"
```bash
# On laptop
git pull
```

### "I made changes on both computers (conflict)"
```bash
# Git will tell you there's a conflict
# Fix conflicts in files (git will mark them)
# Then commit the resolved version
```

### "I want to go back to yesterday's version"
```bash
# See all versions
git log

# Go back to specific version
git checkout COMMIT_HASH
```

### "I accidentally deleted files"
```bash
# Restore from GitHub
git checkout -- filename.py
```

---

## 💡 Quick Start Cheat Sheet

### GitHub Setup (One Time)
```bash
# On desktop
git init
git add *.py *.md *.sh
git commit -m "Initial setup"
git remote add origin https://github.com/YOU/nursing-agents.git
git push -u origin main
```

### Daily Use

**Before starting work:**
```bash
git pull  # Get latest changes
```

**After finishing work:**
```bash
git add .
git commit -m "What I changed"
git push
```

**On new computer:**
```bash
git clone https://github.com/YOU/nursing-agents.git
cd nursing-agents
./scripts/dev_setup.sh
cp .env.template .env  # Add your API keys
./start_nursing_project.sh
```

---

## 📚 Additional Resources

### Learn Git/GitHub
- GitHub Guides: https://guides.github.com/
- Git Basics: https://git-scm.com/book/en/v2
- GitHub Student: https://education.github.com/pack (free benefits!)

### Docker (if interested later)
- Docker Tutorial: https://docs.docker.com/get-started/
- Docker Desktop: https://www.docker.com/products/docker-desktop

---

## ✅ Final Recommendation

**For your 7-month nursing improvement project:**

1. **Primary Method**: Private GitHub repository
   - Safe, secure, professional
   - Easy to sync across computers
   - Backed up automatically

2. **Backup Method**: Create one zip file monthly
   - Store on USB drive
   - Emergency backup if GitHub issues

3. **Skip**: Docker (too complex for now)

**You're all set!** Your project is now portable and secure. 🎓

---

## Questions?

If you need help with:
- Setting up private GitHub repo
- Removing hardcoded API keys
- Creating portable package
- Anything else

Just ask! I'm here to help. 🏥

