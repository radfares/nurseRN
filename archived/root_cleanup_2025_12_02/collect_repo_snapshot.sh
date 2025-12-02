#!/usr/bin/env bash
set -euo pipefail
OUT="repo_snapshot.json"
TMPDIR="$(mktemp -d)"
sanitize_key_re='s/sk-[A-Za-z0-9_\-]\{3,\}\*{0,}[A-Za-z0-9]\{0,\}/REDACTED_API_KEY/g'

# 1) repo tree (4 levels)
echo "Collecting tree..."
tree -L 4 -a --noreport . > "$TMPDIR/tree.txt" 2>/dev/null || (find . -maxdepth 4 -print > "$TMPDIR/tree.txt")

# 2) top-level files of interest
FILES_TO_CAPTURE=(
  "agents"
  "libs"
  ".claude/agent_audit_logs"
  "tmp"
  "data"
  "requirements.txt"
  "pyproject.toml"
  "setup.py"
  "start_nursing_project.sh"
  "scripts"
)

# 3) capture file heads for agent and config files
echo "Capturing file heads..."
declare -A heads
for p in "${FILES_TO_CAPTURE[@]}"; do
  if [ -d "$p" ]; then
    # list files in dir (top-level)
    find "$p" -maxdepth 1 -type f -print 2>/dev/null | while read -r f; do
      key="$(echo "$f" | sed 's|^\./||; s|/|__|g')"
      head -n 200 "$f" 2>/dev/null | sed -E "$sanitize_key_re" > "$TMPDIR/head_${key}.txt" || true
    done
  elif [ -f "$p" ]; then
    key="$(echo "$p" | sed 's|^\./||; s|/|__|g')"
    head -n 200 "$p" 2>/dev/null | sed -E "$sanitize_key_re" > "$TMPDIR/head_${key}.txt" || true
  fi
done

# 4) capture last 200 lines of audit logs (sanitized)
echo "Capturing audit logs..."
if [ -d ".claude/agent_audit_logs" ]; then
  mkdir -p "$TMPDIR/audit"
  for f in .claude/agent_audit_logs/*.jsonl .claude/agent_audit_logs/*.log 2>/dev/null; do
    [ -e "$f" ] || continue
    tail -n 200 "$f" 2>/dev/null | sed -E "$sanitize_key_re" > "$TMPDIR/audit/$(basename "$f")"
  done
fi

# 5) sqlite schemas for .db files under tmp/ and data/
echo "Capturing sqlite schemas..."
mkdir -p "$TMPDIR/dbs"
find tmp data -type f -name "*.db" 2>/dev/null | while read -r db; do
  out="$TMPDIR/dbs/$(echo "$db" | sed 's|/|__|g')__schema.sql"
  sqlite3 "$db" .schema 2>/dev/null | sed -E "$sanitize_key_re" > "$out" || echo "-- cannot read schema for $db" > "$out"
done

# 6) compute checksums and sizes for all files (top-level)
echo "Computing checksums..."
find . -type f -maxdepth 4 -print0 2>/dev/null | xargs -0 stat -f "%N|%z" 2>/dev/null > "$TMPDIR/filesizes.txt" || true

# 7) assemble JSON manifest
echo "Assembling JSON..."
python3 - <<'PY'
import json, os, glob, sys
root = os.getcwd()
out = {}
out['root'] = root
out['tree'] = open(os.path.join("$TMPDIR","tree.txt")).read() if os.path.exists(os.path.join("$TMPDIR","tree.txt")) else ""
out['heads'] = {}
for fn in glob.glob(os.path.join("$TMPDIR","head_*.txt")):
    key = os.path.basename(fn).replace("head_","").replace(".txt","")
    out['heads'][key] = open(fn,'r',encoding='utf-8',errors='ignore').read()
out['audit'] = {}
audit_dir = os.path.join("$TMPDIR","audit")
if os.path.isdir(audit_dir):
    for fn in os.listdir(audit_dir):
        out['audit'][fn] = open(os.path.join(audit_dir,fn),'r',encoding='utf-8',errors='ignore').read()
out['db_schemas'] = {}
dbdir = os.path.join("$TMPDIR","dbs")
if os.path.isdir(dbdir):
    for fn in os.listdir(dbdir):
        out['db_schemas'][fn] = open(os.path.join(dbdir,fn),'r',encoding='utf-8',errors='ignore').read()
out['filesizes'] = {}
fsfile = os.path.join("$TMPDIR","filesizes.txt")
if os.path.exists(fsfile):
    for line in open(fsfile):
        try:
            name,size = line.strip().split("|",1)
            out['filesizes'][name] = int(size)
        except:
            pass
print(json.dumps(out, indent=2))
PY > "$OUT"

echo "WROTE $OUT"
ls -l "$OUT"
