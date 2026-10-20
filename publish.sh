#!/bin/bash
# Build offrampt.net into docs/, checked.
#
#   ./publish.sh            # fetch what is stale, compute, chart, pages, into docs/
#   ./publish.sh --draw     # also redraw the pictures (build/img/*.jpg)
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1
SITE_URL="${SITE_URL:-https://offrampt.net}"

STYLE="$HOME/.claude/bin/stylecheck.py"
if [ -f "$STYLE" ]; then
  python3 "$STYLE" tools js data/research data/routes.json data/ramp.json README.md NOTICE.txt || { echo "REFUSED: style. See ~/.claude/STYLE.md"; exit 4; }
fi

python3 tools/fetch.py
python3 tools/compute.py || { echo "REFUSED: a computed check failed"; exit 5; }
if [ "${1:-}" = "--draw" ] || [ ! -f build/img/hero.jpg ]; then python3 tools/draw.py; else python3 tools/draw.py markets networks card card_th; fi
python3 tools/figures.py
SITE_URL="$SITE_URL" python3 tools/site.py
python3 tools/links.py --quiet || { echo "REFUSED: broken internal links"; exit 3; }
python3 tests/test_site.py || { echo "REFUSED: tests"; exit 6; }

if grep -rl "/Users/" build/site >/dev/null 2>&1; then
  echo "REFUSED: host paths found in build/site"; exit 2
fi

rm -rf docs
cp -R build/site docs
rm -f docs/.basepath
echo "docs/ ← $(find docs -name 'index.html' | wc -l | tr -d ' ') pages, $(du -sh docs | cut -f1)"
