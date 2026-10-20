#!/bin/bash
# Put docs/ on offrampt.net (Cloudflare Pages project "offrampt"). Roll back from the
# Pages dashboard's deployment list, or redeploy an older docs/.
set -euo pipefail
cd "$(dirname "$0")"
[ -f docs/index.html ] || { echo "no docs/ — run ./publish.sh first"; exit 1; }
if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  CLOUDFLARE_API_TOKEN=$(python3 -c 'import json,pathlib;print(json.load(open(pathlib.Path.home()/".config/nanobotco/keys.json"))["cloudflare"]["api_token"])')
  export CLOUDFLARE_API_TOKEN
fi
n=$(find docs -type f | wc -l | tr -d ' ')
echo "→ offrampt: $n files"
CI=1 npx wrangler pages deploy docs --project-name offrampt --branch main --commit-dirty=true
