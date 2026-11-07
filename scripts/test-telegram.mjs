#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// Load .env
const envPath = path.join(rootDir, '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  for (const line of envContent.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIdx = trimmed.indexOf('=');
    if (eqIdx !== -1) {
      const key = trimmed.slice(0, eqIdx).trim();
      const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, '');
      if (!process.env[key]) {
        process.env[key] = val;
      }
    }
  }
}

const TELEGRAM_BOT_TOKEN = process.argv[2] || process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.argv[3] || process.env.TELEGRAM_CHAT_ID;

if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
  console.error('❌ Gagal: TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID harus diisi.');
  console.log('Penggunaan:');
  console.log('  node scripts/test-telegram.mjs <BOT_TOKEN> <CHAT_ID>');
  console.log('atau isi variabel TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID di /root/chainasiaweb/.env');
  process.exit(1);
}

const nowWib = new Date().toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' });
const message = `🔔 <b>TEST KONEKSI TELEGRAM BOT PT CHAIN ASIA CONECT</b>
━━━━━━━━━━━━━━━━━━━━━━
✅ <b>Status:</b> Bot terhubung dan siap mengirimkan notifikasi publikasi artikel harian!
⏰ <b>Waktu Server:</b> ${nowWib} WIB
📡 <b>Endpoint:</b> <code>https://api.telegram.org/bot[TOKEN]/sendMessage</code>
━━━━━━━━━━━━━━━━━━━━━━
<i>Notifikasi publikasi artikel otomatis akan dikirim ke sini setiap jam 07:00 WIB.</i>`;

async function testTelegram() {
  console.log(`Menguji pengiriman pesan ke Telegram Chat ID: ${TELEGRAM_CHAT_ID}...`);
  try {
    const res = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: 'HTML'
      })
    });
    const result = await res.json();
    if (result.ok) {
      console.log('🎉 SUKSES! Pesan test berhasil diterima di Telegram.');
      console.log(`Detail Bot: @${result.result.from.username} (${result.result.from.first_name})`);
    } else {
      console.error('❌ Gagal mengirim ke Telegram:', result.description);
    }
  } catch (err) {
    console.error('💥 Error koneksi jaringan:', err.message);
  }
}

testTelegram();

