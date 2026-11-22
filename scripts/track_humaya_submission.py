#!/usr/bin/env python3
"""
track_humaya_submission.py
Script pemantau otomatis status naskah Jurnal Humaya (OJS UT) via REST API & Telegram Bot.
Mendukung:
1. Mode CLI interaktif (tanpa argumen)
2. Mode Kirim Status Sekarang (--notify / -n)
3. Mode Auto / Cron Watchdog (--auto): hanya kirim pesan Telegram jika ada perubahan status/aktivitas baru dari editor.
"""

import sys
import os
import requests
import json
from datetime import datetime

ENV_PATH = "/root/journal/.env"
STATE_FILE = "/root/journal/data/humaya_submission_state.json"
SUBMISSION_ID = 16291

def load_env():
    env_vars = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

def send_telegram_alert(message_html):
    env_vars = load_env()
    bot_token = env_vars.get("TELEGRAM_BOT_TOKEN")
    chat_id = env_vars.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("[ERROR] TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID tidak ditemukan di .env")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"[ERROR] Gagal mengirim pesan Telegram: {e}")
        return False

def format_stage(stage_id):
    stages = {
        1: "1. Submission (Pemeriksaan Awal Editor / Desk Review)",
        3: "3. Review (Peer Review oleh Mitra Bestari)",
        4: "4. Copyediting (Penyuntingan Tata Letak & Bahasa)",
        5: "5. Production (Penerbitan / Galley Proofing)"
    }
    return stages.get(stage_id, f"Tahap {stage_id}")

def format_status(status_id, status_label):
    status_map = {
        1: "⏳ Mengantre (Queued in Editorial Workflow)",
        3: "🎉 Telah Diterbitkan (Published)",
        4: "❌ Ditolak (Declined)"
    }
    return status_map.get(status_id, status_label or str(status_id))

def get_submission_data(submission_id=SUBMISSION_ID):
    env_vars = load_env()
    token = env_vars.get("OJS_UT_API_TOKEN")
    base_url = "https://jurnal.ut.ac.id/index.php/humaya_fhisip/api/v1"

    if not token:
        print("[ERROR] OJS_UT_API_TOKEN tidak ditemukan di /root/journal/.env")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/submissions/{submission_id}"

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[ERROR] HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json()
    except Exception as e:
        print(f"[EXCEPTION] Gagal menghubungi OJS API: {str(e)}")
        return None

def build_status_message(data, alert_title=None, changes=None):
    sub_id = data.get("id", SUBMISSION_ID)
    stage_id = data.get("stageId")
    status = data.get("status")
    status_label = data.get("statusLabel")
    date_sub = data.get("dateSubmitted", "-")
    last_act = data.get("dateLastActivity", "-")
    url_dash = data.get("urlAuthorWorkflow", f"https://jurnal.ut.ac.id/index.php/humaya_fhisip/authorDashboard/submission/{sub_id}")
    
    stages = data.get("stages", [])
    review_rounds = data.get("reviewRounds", [])
    
    # Hitung queries aktif
    queries_count = 0
    for s in stages:
        if s.get("id") == stage_id:
            queries_count = len(s.get("queries", []))
            break

    header = alert_title if alert_title else "🏛️ <b>STATUS NASKAH JURNAL HUMAYA (UT)</b>"
    
    msg_lines = [
        f"{header}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "📄 <b>Judul:</b> Pertanggungjawaban Hukum Perdata atas Kegagalan Transaksi Elektronik Berbasis Agen Kecerdasan Buatan Otonom di Indonesia",
        f"🆔 <b>ID Pengajuan:</b> <code>#{sub_id}</code>",
        f"📌 <b>Tahap:</b> <b>{format_stage(stage_id)}</b>",
        f"📊 <b>Status:</b> {format_status(status, status_label)}",
        f"💬 <b>Diskusi Editor:</b> {queries_count} Utas Terbuka",
        f"👥 <b>Peer Review:</b> {len(review_rounds)} Putaran Berjalan",
        f"⏱️ <b>Aktivitas Terakhir:</b> {last_act} WIB",
        "━━━━━━━━━━━━━━━━━━━━━━",
    ]
    
    if changes:
        msg_lines.append("🔔 <b>DETAIL PERUBAHAN:</b>")
        for ch in changes:
            msg_lines.append(f"• {ch}")
        msg_lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        
    msg_lines.append(f"🔗 <a href='{url_dash}'>Buka Dashboard OJS Penulis</a>")
    return "\n".join(msg_lines)

def load_cached_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cached_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def run():
    args = sys.argv[1:]
    is_auto = "--auto" in args or "--cron" in args
    is_force_notify = "--notify" in args or "-n" in args or "--send-now" in args

    data = get_submission_data(SUBMISSION_ID)
    if not data:
        sys.exit(1)

    stage_id = data.get("stageId")
    status = data.get("status")
    last_act = data.get("dateLastActivity")
    review_rounds_count = len(data.get("reviewRounds", []))
    
    stages = data.get("stages", [])
    queries_count = 0
    for s in stages:
        if s.get("id") == stage_id:
            queries_count = len(s.get("queries", []))
            break

    current_state = {
        "stageId": stage_id,
        "status": status,
        "dateLastActivity": last_act,
        "reviewRoundsCount": review_rounds_count,
        "queriesCount": queries_count,
        "checkedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    prev_state = load_cached_state()

    # Periksa perubahan jika auto
    changes = []
    if prev_state:
        if prev_state.get("stageId") != stage_id:
            changes.append(f"Perubahan Tahap: <b>{format_stage(prev_state.get('stageId'))}</b> ➔ <b>{format_stage(stage_id)}</b>")
        if prev_state.get("status") != status:
            changes.append(f"Perubahan Status: <b>{prev_state.get('status')}</b> ➔ <b>{status}</b>")
        if prev_state.get("queriesCount") != queries_count:
            diff = queries_count - prev_state.get("queriesCount", 0)
            if diff > 0:
                changes.append(f"Pesan/Diskusi Baru: <b>+{diff} utas pesan masuk dari Editor!</b>")
            else:
                changes.append(f"Diskusi Berubah: Total {queries_count} utas")
        if prev_state.get("reviewRoundsCount") != review_rounds_count:
            changes.append(f"Status Review: Memasuki Putaran Ke-{review_rounds_count}")
        if prev_state.get("dateLastActivity") != last_act and not changes:
            changes.append(f"Editor baru saja memperbarui naskah/aktivitas pada {last_act} WIB")

    if is_auto:
        if changes:
            print(f"[WATCHDOG] Terdeteksi {len(changes)} perubahan. Mengirim alert Telegram...")
            msg = build_status_message(data, alert_title="🚨 <b>UPDATE EDITORIAL JURNAL HUMAYA!</b>", changes=changes)
            send_telegram_alert(msg)
            save_cached_state(current_state)
        else:
            print(f"[WATCHDOG] Tidak ada perubahan status. Status tetap: {format_stage(stage_id)} ({last_act}).")
            save_cached_state(current_state)
    elif is_force_notify:
        print("[NOTIFY] Mengirim laporan status terkini ke Telegram...")
        msg = build_status_message(data, alert_title="📱 <b>STATUS TERKINI NASKAH JURNAL HUMAYA</b>")
        success = send_telegram_alert(msg)
        save_cached_state(current_state)
        if success:
            print(" Berhasil terkirim ke Telegram!")
        else:
            print("❌ Gagal mengirim ke Telegram.")
    else:
        # CLI printout
        print("=" * 70)
        print("  STATUS PENGAJUAN JURNAL HUMAYA (UNIVERSITAS TERBUKA)")
        print("=" * 70)
        print(f"ID Naskah       : {SUBMISSION_ID}")
        print(f"Status Naskah   : {format_status(status, data.get('statusLabel'))}")
        print(f"Tahap Saat Ini  : {format_stage(stage_id)}")
        print(f"Aktivitas Terakhir: {last_act} WIB")
        print(f"Diskusi Editor  : {queries_count} Utas Terbuka")
        print(f"Tautan Dashboard: {data.get('urlAuthorWorkflow')}")
        print("=" * 70)
        save_cached_state(current_state)

if __name__ == "__main__":
    run()
