#!/usr/bin/env bash
# JCFAD - Daily Scientific Article Generator & Catch-up Runner
set -e

LOCK_FILE="/tmp/jcfad-auto-article.lock"
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ Proses auto-article lain sedang berjalan. Melewati proses ganda (Race-condition dicegah)." >> "/root/journal/logs/auto-article.log"
  exit 0
fi

TODAY=$(date '+%Y-%m-%d')
REGISTRY="/root/journal/scripts/published_topics.json"
LOG_FILE="/root/journal/logs/auto-article.log"
mkdir -p /root/journal/logs

# Cek apakah artikel dengan tanggal hari ini sudah ada dalam published_topics.json
if [ -f "$REGISTRY" ] && grep -q "\"date\": \"$TODAY\"" "$REGISTRY"; then
  echo "[$TODAY $(date '+%H:%M:%S')] Artikel riset untuk hari ini ($TODAY) sudah terbit. Melewati proses." >> "$LOG_FILE"
  exit 0
fi

echo "=================================================================" >> "$LOG_FILE"
echo "[$TODAY $(date '+%H:%M:%S')] Menjalankan Auto-Article Generator JCFAD..." >> "$LOG_FILE"
echo "=================================================================" >> "$LOG_FILE"

cd /root/journal
/usr/bin/node scripts/auto-article-groq.mjs >> "$LOG_FILE" 2>&1
/usr/local/bin/autopush "auto: artikel riset harian $TODAY" >> "$LOG_FILE" 2>&1

