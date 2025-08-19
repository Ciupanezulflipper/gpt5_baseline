#!/data/data/com.termux/files/usr/bin/bash
set -e
msg="${1:-update}"
git add -A
git commit -m "$msg" || echo "No changes to commit."
git push -u origin main
