#!/bin/bash
# Publish one intel note: check it, build with every gate, deploy offrampt.net, commit, move main up.
#
#   tools/intel_publish.sh data/intel/notes/<YYYY-MM-DD>-<slug>.json
#
# Run from a checkout of the offrampt repository (the intel desk is a worktree of it on branch
# intel-desk). main follows by fast-forward; when main's checkout cannot move (someone is working
# in it), the note stays committed here, and every build keeps it anyway: intel.py reads the live
# notes.json back.
set -euo pipefail
cd "$(dirname "$0")/.."
f="${1:?a note file}"
export PYTHONUTF8=1

python3 tools/intel_check.py "$f"
./publish.sh || { echo "STOPPED: a gate in publish.sh"; exit 3; }
./deploy.sh

slug=$(python3 -c 'import json,re,sys;print(re.sub(r"^\d{4}-\d{2}-\d{2}-","",json.load(open(sys.argv[1]))["id"]))' "$f")
title=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["title_en"])' "$f")
git add data/intel docs
git commit -q -m "Intel: $title" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true

branch=$(git rev-parse --abbrev-ref HEAD)
main_dir=$(git worktree list --porcelain | python3 -c '
import sys
w = None
for ln in sys.stdin.read().splitlines():
    if ln.startswith("worktree "): w = ln[9:]
    if ln == "branch refs/heads/main": print(w); break')
moved="main not moved"
if [ "$branch" != "main" ] && [ -n "$main_dir" ]; then
  git -C "$main_dir" merge -q --ff-only "$branch" 2>/dev/null && moved="main moved to $branch"
fi

url="https://offrampt.net/intel/$slug/"
code=000
for i in $(seq 1 20); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$url")
  [ "$code" = "200" ] && break
  sleep 15
done
echo "$url → $code; $moved"
[ "$code" = "200" ]
