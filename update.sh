#!/data/data/com.termux/files/usr/bin/bash
set -e
branch="${1:-main}"

echo "[*] git pull --rebase origin $branch"
git pull --rebase origin "$branch" || true

echo "[*] git add -A"
git add -A

msg="chore: update $(date -u +'%Y-%m-%d %H:%MZ')"
echo "[*] git commit -m \"$msg\" (may say 'no changes')"
git commit -m "$msg" || echo "No changes to commit."

echo "[*] git push -u origin $branch"
git push -u origin "$branch"
