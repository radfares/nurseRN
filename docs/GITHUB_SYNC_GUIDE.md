# GitHub Sync Cheat Sheet
## For nurseRN Project - Mac ↔️ Mac Mini

---

## 🟢 When You START Working

```bash
cd /Users/hdz/nurseRN
git pull
```

> Pulls latest changes from GitHub before you begin working

---

## 🔴 When You FINISH Working

```bash
cd /Users/hdz/nurseRN

# Save everything
git add .

# Write what you did
git commit -m "describe what you changed"

# Push to GitHub
git push
```

> Saves your work locally and syncs to GitHub

---

## ⚙️ One-Time Setup on Mac Mini

```bash
# Clone the repository (only do this ONCE)
cd ~
git clone https://github.com/radfares/nurseRN.git
cd nurseRN

# Copy your .env file from Mac to Mac mini
# (manually transfer your .env file with API keys)

# Install dependencies
./setup_venv.sh
```

---

## 🚨 Quick Troubleshooting

**"Conflict" error when pulling?**
```bash
git stash       # Save your changes temporarily
git pull        # Pull latest
git stash pop   # Restore your changes
```

**"Failed to push" error?**
```bash
git pull        # Pull first
git push        # Then push
```

**Forgot what you changed?**
```bash
git status      # See modified files
git diff        # See exact changes
```

---

## ✅ That's It!

Just remember:
- **START**: `git pull`
- **FINISH**: `git add . → git commit -m "message" → git push`
