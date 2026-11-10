#!/usr/bin/env node

/**
 * ==============================================================================
 * Self-Healing & Citation Integrity Engine for Regressed Subchapters
 * ==============================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// Load environment variables
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
      if (!process.env[key]) process.env[key] = val;
    }
  }
}

const GEMINI_KEYS = (process.env.GEMINI_API_KEYS || process.env.GEMINI_API_KEY || '')
  .split(',')
  .map(k => k.trim())
  .filter(Boolean);

let keyIdx = 0;
function getNextKey() {
  const k = GEMINI_KEYS[keyIdx];
  keyIdx = (keyIdx + 1) % GEMINI_KEYS.length;
  return k;
}

const GEMINI_MODELS = [
  'gemini-3.5-flash-lite',
  'gemini-3.1-flash-lite',
  'gemini-3.5-flash'
];

async function callGemini(systemPrompt, userPrompt) {
  for (let attempt = 0; attempt < 8; attempt++) {
    const key = getNextKey();
    const model = GEMINI_MODELS[attempt % GEMINI_MODELS.length];
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
      const payload = {
        contents: [{ role: 'user', parts: [{ text: `${systemPrompt}\n\n---\n\n${userPrompt}` }] }],
        generationConfig: { temperature: 0.7, maxOutputTokens: 8192 }
      };

      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.status === 429 || res.status === 503) {
        console.log(`⏳ Jeda sejenak (${model})...`);
        await new Promise(r => setTimeout(r, 10000));
        continue;
      }

      if (!res.ok) continue;

      const data = await res.json();
      const txt = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (txt && txt.trim().length > 500) return txt.trim();
    } catch (_) {
      await new Promise(r => setTimeout(r, 2000));
    }
  }
  return null;
}

const BOOK_SLUG = 'empati-sintetis-buku-cetak';
const CACHE_DIR = path.join(rootDir, 'books', 'cache', BOOK_SLUG);
const SUB1_DIR = path.join(CACHE_DIR, 'subchapters');
const SUB2_DIR = path.join(CACHE_DIR, 'subchapters_pass2');

async function healSubchapter(subFile) {
  const base = path.basename(subFile);
  const p1File = path.join(SUB1_DIR, base);
  const p2File = path.join(SUB2_DIR, base);

  const p1 = JSON.parse(fs.readFileSync(p1File, 'utf-8'));
  const p2 = JSON.parse(fs.readFileSync(p2File, 'utf-8'));

  if (p2.wordCount >= 2200) {
    console.log(`✅ [${base}] Sudah sangat tebal (${p2.wordCount} kata) — Melewati.`);
    return p2;
  }

  console.log(`\n🔧 [${base}] Memperbaiki & Memperluas: Pass1=${p1.wordCount} kata, Pass2=${p2.wordCount} kata...`);

  const system = `Anda adalah Ilham Pradani, penulis utama monograf ilmiah terkemuka berstandar Cambridge/Oxford University Press.
Tugas Anda adalah memperkaya naskah Sub-bab ${p1.code}: "${p1.title}" secara tuntas dan panjang.

SYARAT MUTLAK:
1. SUNTIKKAN SITASI AKADEMIK (Author, Year) PADA SETIAP PARAGRAF.
2. JAGA GAYA BAHASA RENYAH, MENGALIR, DAN MEMBUMI (fokus pada asas iktikad baik, asas konsensualisme, perlindungan martabat).
3. HINDARI DAFTAR POIN TEMPLATE KAKU. Gunakan esai naratif dialektis berbobot.
4. TARGET PANJANG: MINIMAL 2.500 - 3.500 KATA. Uraikan setiap sub-bagian (### ${p1.code}.1 sampai ### ${p1.code}.4) dengan fakta perkara nyata, doktrin hukum, dan dialektika mendalam.
5. Di akhir naskah tambahkan:
   #### Rujukan Terpilih Sub-bab ${p1.code} (minimal 8-10 sitasi ilmiah lengkap).`;

  const user = `Berikut naskah awal yang harus diperluas dan diperkaya:\n\n${p1.contentMarkdown}\n\nTuliskan naskah lengkap hasil pengayaan dan perluasannya sekarang (minimal 2.500 kata)!`;

  const enriched = await callGemini(system, user);
  if (enriched) {
    const wc = enriched.split(/\s+/).filter(Boolean).length;
    if (wc > p1.wordCount) {
      const res = { code: p1.code, title: p1.title, contentMarkdown: enriched, wordCount: wc };
      fs.writeFileSync(p2File, JSON.stringify(res, null, 2), 'utf-8');
      console.log(`   🎉 [${base}] BERHASIL DIPERKAYA: ${wc} kata!`);
      return res;
    }
  }

  // Jika gagal melebihi Pass 1, gunakan Pass 1 daripada membiarkan teks kerdil
  console.log(`   🛡️ Menggunakan Pass 1 (${p1.wordCount} kata) sebagai dasar yang aman.`);
  fs.writeFileSync(p2File, JSON.stringify(p1, null, 2), 'utf-8');
  return p1;
}

async function main() {
  console.log(`🚀 Memulai Pemulihan & Ekspansi 11 Sub-bab yang Terpotong...`);

  const blueprintPath = path.join(CACHE_DIR, 'blueprint.json');
  const blueprint = JSON.parse(fs.readFileSync(blueprintPath, 'utf-8'));

  for (const chMeta of blueprint.chapters) {
    const chNum = chMeta.number;
    const subResults = [];

    for (const subMeta of chMeta.subchapters) {
      const base = `ch${String(chNum).padStart(2, '0')}_sub${subMeta.code.replace('.', '_')}.json`;
      const subRes = await healSubchapter(base);
      subResults.push(subRes);
    }

    // Rajut kembali chapter
    const fullMarkdown = [
      `# Bab ${chNum}: ${chMeta.title}\n`,
      subResults.map(s => s.contentMarkdown).join('\n\n---\n\n')
    ].join('\n\n');

    const totalWords = subResults.reduce((acc, s) => acc + s.wordCount, 0);
    const finalChapterFile = path.join(CACHE_DIR, `chapter-${String(chNum).padStart(2, '0')}-final.json`);

    const finalData = {
      chapterNumber: chNum,
      chapterTitle: chMeta.title,
      version: 'ENRICHED_MAGNUM_OPUS_FINAL',
      contentMarkdown: fullMarkdown,
      wordCount: totalWords
    };

    fs.writeFileSync(finalChapterFile, JSON.stringify(finalData, null, 2), 'utf-8');
    console.log(`📚 Bab ${chNum} SELESAI: ${totalWords} Kata (~${Math.round(totalWords / 300)} Halaman ISO-B5)`);
  }

  // Kompilasi ulang Typst
  console.log(`\n📚 Mengompilasi Naskah Edisi Definitif ke PDF Typst ISO-B5...`);
  execSync(`python3 "${path.join(__dirname, 'compile-book-typst.py')}" "${BOOK_SLUG}"`, { stdio: 'inherit' });

  // Build & Deploy
  console.log(`\n🌐 Membangun Static Site Astro & Deploy ke Cloudflare Pages...`);
  execSync(`npm run build`, { stdio: 'inherit' });
  execSync(`npx wrangler pages deploy dist --project-name=jcfad-journal --branch=main`, { stdio: 'inherit' });

  console.log(`\n🏆 PROSES PEMULIHAN, KOMPILASI & DEPLOY SELESAI SEMPURNA!`);
}

main().catch(console.error);

