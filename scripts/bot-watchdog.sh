#!/usr/bin/env bash

# PT CHAIN ASIA CONECT - Telegram Bot Process Watchdog
LOG_FILE="/root/chainasiaweb/logs/telegram-bot.log"
PID_FILE="/root/chainasiaweb/logs/telegram-bot.pid"

mkdir -p /root/chainasiaweb/logs

# Cek apakah proses node scripts/telegram-server-bot.mjs sedang berjalan
if ! pgrep -f "telegram-server-bot.mjs" > /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Telegram server bot tidak berjalan. Menyalakan bot..." >> "$LOG_FILE"
    nohup /usr/local/bin/node /root/chainasiaweb/scripts/telegram-server-bot.mjs >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
fi
