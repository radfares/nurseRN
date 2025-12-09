#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C.UTF-8
OUT="repo_snapshot.json"
TMPDIR="$(mktemp -d)"
sanitize_key_re='s/sk-[A-Za-z0-9_\-]\{3,\}\*{0,}[A-Za-z0-9]\{0,\}/REDACTED_API_KEY/g'

# 1) repo tree (4 levels)
if command -v tree >/dev/null 2>&1; then
  tree -L 4 -a --noreport . > "$TMPDIR/tree.txt" 2>/dev/null || find . -maxdepth 4 -print > "$TMPDIR/tree.txt"
else
  find . -maxdepth 4 -print > "$TMPDIR/tree.txt"
fi

# 2) capture heads for interesting files and agent files (first 200 lines)
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
mkdir -p "$TMPDIR/heads"
for p in "${FILES_TO_CAPTURE[@]}"; do
  if [ -d "$p" ]; then
    find "$p" -maxdepth 1 -type f -print0 2>/dev/null | while IFS= read -r -d '' f; do
      key="$(echo "$f" | sed 's|^\./||; s|/|__|g')"
      head -n 200 "$f" 2>/dev/null | sed -E "$sanitize_key_re" > "$TMPDIR/heads/${key}.txt" || true
    done
  elif [ -f "$p" ]; then
    key="$(echo "$p" | sed 's|^\./||; s|/|__|g')"
    head -n 200 "$p" 2>/dev/null | sed -E "$sanitize_key_re" > "$TMPDIR/heads/${key}.txt" || true
  fi
done

# 3) capture last 200 lines of audit logs (sanitized)
mkdir -p "$TMPDIR/audit"
if [ -d ".claude/agent_audit_logs" ]; then
  for f in .claude/agent_audit_logs/*; do
    if [ -f "$f" ]; then
      tail -n 200 "$f" 2>/dev/null | sed -E "$sanitize_key_re" > "$TMPDIR/audit/$(basename "$f")"
    fi
  done
fi

# 4) sqlite schemas for .db files under tmp/ and data/
mkdir -p "$TMPDIR/dbs"
find tmp data -type f -name "*.db" 2>/dev/null | while read -r db; do
  out="$TMPDIR/dbs/$(echo "$db" | sed 's|/|__|g')__schema.sql"
  if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$db" .schema 2>/dev/null | sed -E "$sanitize_key_re" > "$out" || echo "-- cannot read schema for $db" > "$out"
  else
    echo "-- sqlite3 not available to read $db" > "$out"
  fi
done

# 5) compute sizes for files up to depth 4
find . -type f -maxdepth 4 -print0 2>/dev/null | xargs -0 stat -f "%N|%z" 2>/dev/null > "$TMPDIR/filesizes.txt" || true

# 6) assemble JSON manifest
python3 - <<PY > "$OUT"
import json, os, glob
tmp = os.path.abspath("$TMPDIR")
out = {}
out['root'] = os.getcwd()
tree_path = os.path.join(tmp, "tree.txt")
out['tree'] = open(tree_path,'r',encoding='utf-8',errors='ignore').read() if os.path.exists(tree_path) else ""
out['heads'] = {}
for fn in glob.glob(os.path.join(tmp, "heads", "*.txt")):
    key = os.path.basename(fn).replace(".txt","")
    try:
        out['heads'][key] = open(fn,'r',encoding='utf-8',errors='ignore').read()
    except:
        out['heads'][key] = ""
out['audit'] = {}
audit_dir = os.path.join(tmp, "audit")
if os.path.isdir(audit_dir):
    for fn in os.listdir(audit_dir):
        path = os.path.join(audit_dir, fn)
        try:
            out['audit'][fn] = open(path,'r',encoding='utf-8',errors='ignore').read()
        except:
            out['audit'][fn] = ""
out['db_schemas'] = {}
dbdir = os.path.join(tmp, "dbs")
if os.path.isdir(dbdir):
    for fn in os.listdir(dbdir):
        path = os.path.join(dbdir, fn)
        try:
            out['db_schemas'][fn] = open(path,'r',encoding='utf-8',errors='ignore').read()
        except:
            out['db_schemas'][fn] = ""
out['filesizes'] = {}
fsfile = os.path.join(tmp, "filesizes.txt")
if os.path.exists(fsfile):
    for line in open(fsfile,'r',encoding='utf-8',errors='ignore'):
        try:
            name,size = line.strip().split("|",1)
            out['filesizes'][name] = int(size)
        except:
            pass
print(json.dumps(out, indent=2))
PY

echo "WROTE $OUT"
ls -l "$OUT"
