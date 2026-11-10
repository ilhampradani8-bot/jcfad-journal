#!/usr/bin/env node

/**
 * ==============================================================================
 * PT CHAIN ASIA CONECT - Academic Book Enrichment & Citation Engine (Pass 2)
 * ==============================================================================
 * Target: Memperkaya 10 Bab Buku Monograf Menjadi 350 - 450+ Halaman ISO-B5
 * Fitur:
 * 1. Injeksi Sitasi Ilmiah Primer Per Paragraf (Weizenbaum, Searle, Husserl, Buber,
 *    Kahneman, Zuboff, Farahany, Calo, Thaler, KUHPerdata, EU AI Act, UU PDP).
 * 2. Bahasa Tetap Luwes, Renyah, Mengalir & Membumi untuk Semua Orang.
 * 3. Pendalaman Asas Hukum (Iktikad Baik, Konsensualisme, Cacat Kehendak, Martabat).
 * 4. Penambahan Daftar Pustaka Lengkap Per Bab (Complete Academic Bibliography).
 * 5. Kompilasi Typst ISO-B5 Siap Cetak (Target 350-450 Hal) & Auto-Deploy.
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

if (GEMINI_KEYS.length === 0) {
  console.error('❌ ERROR: GEMINI_API_KEYS tidak ditemukan!');
  process.exit(1);
}

let keyIdx = 0;
function getNextKey() {
  const k = GEMINI_KEYS[keyIdx];
  keyIdx = (keyIdx + 1) % GEMINI_KEYS.length;
  return k;
}

const GEMINI_MODELS = [
  'gemini-3.5-flash-lite',
  'gemini-3.1-flash-lite',
  'gemini-3.5-flash',
  'gemini-3.8-flash'
];

async function callGemini(systemPrompt, userPrompt, temperature = 0.7, maxTokens = 8192) {
  let attempts = 0;
  const maxAttempts = GEMINI_KEYS.length * GEMINI_MODELS.length * 2;

  while (attempts < maxAttempts) {
    const key = getNextKey();
    const model = GEMINI_MODELS[attempts % GEMINI_MODELS.length];

    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
      const payload = {
        contents: [{ role: 'user', parts: [{ text: `${systemPrompt}\n\n---\n\n${userPrompt}` }] }],
        generationConfig: { temperature, maxOutputTokens: maxTokens }
      };

      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.status === 429 || res.status === 503) {
        attempts++;
        if (attempts % GEMINI_KEYS.length === 0) {
          console.log(`⏳ [Cooldown Mode] Istirahat sejenak 25 detik...`);
          await new Promise(r => setTimeout(r, 25000));
        } else {
          await new Promise(r => setTimeout(r, 2000));
        }
        continue;
      }

      if (!res.ok) {
        attempts++;
        await new Promise(r => setTimeout(r, 2000));
        continue;
      }

      const data = await res.json();
      const txt = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (txt && txt.trim().length > 0) return txt.trim();

      attempts++;
    } catch (e) {
      attempts++;
      await new Promise(r => setTimeout(r, 2500));
    }
  }

  throw new Error('Gagal memanggil Gemini setelah semua percobaan.');
}

const BOOK_SLUG = 'empati-sintetis-buku-cetak';
const CACHE_DIR = path.join(rootDir, 'books', 'cache', BOOK_SLUG);
const SUBCHAPTER_DIR = path.join(CACHE_DIR, 'subchapters');
const ENRICHED_SUB_DIR = path.join(CACHE_DIR, 'subchapters_pass2');
fs.mkdirSync(ENRICHED_SUB_DIR, { recursive: true });

async function enrichSubchapter(chNum, subCode, subTitle, originalMarkdown) {
  const enrichedFile = path.join(ENRICHED_SUB_DIR, `ch${String(chNum).padStart(2, '0')}_sub${subCode.replace('.', '_')}.json`);
  if (fs.existsSync(enrichedFile)) {
    const existing = JSON.parse(fs.readFileSync(enrichedFile, 'utf-8'));
    if (existing.wordCount >= 2800) {
      console.log(`   ⏩ [Sub-bab ${subCode}] Sudah diperkaya (${existing.wordCount} kata) — Melewati.`);
      return existing;
    }
  }

  console.log(`   ✍️ [Sub-bab ${subCode}] Menyuntikkan Sitasi Ilmiah & Memperkaya Naskah (Target: 2.800 - 3.800 Kata)...`);

  const system = `Anda adalah Ilham Pradani, penulis utama monograf ilmiah terkemuka berstandar Cambridge/Oxford University Press.
Tugas Anda adalah melakukan PENGAYAAN ILMIAH TINGKAT TINGGI (Pass 2) pada naskah Sub-bab ${subCode}: "${subTitle}".

PEDOMAN MUTLAK PENGAYAAN:
1. SUNTIKKAN SITASI AKADEMIK RESMI PADA SETIAP PARAGRAF:
   - Sematkan sitasi dalam teks format (Author, Year) atau (Pasal X KUHPerdata / Regulasi Y) pada setiap gagasan teoretis, klaim psikologis, dan argumentasi yuridis.
   - Gunakan referensi ilmiah otoritatif dunia yang relevan:
     * Epistemologi & AI: Joseph Weizenbaum (1976), John Searle (1980), Alan Turing (1950), Luciano Floridi (2013), Norbert Wiener (1950), Hubert Dreyfus (1972).
     * Fenomenologi & Etika: Edmund Husserl (1913), Martin Buber (1923), Emmanuel Levinas (1961), Hans Jonas (1979).
     * Psikologi Kognitif & Perilaku: Daniel Kahneman & Amos Tversky (1979, 1984, 2011), John Bowlby (1969), Richard Thaler & Cass Sunstein (2008), Byron Reeves & Clifford Nass (1996), Shoshana Zuboff (2019), Nita Farahany (2023).
     * Hukum & Regulasi: Ryan Calo (2014), Mireille Hildebrandt (2015), KUHPerdata (Pasal 1320, 1321, 1328, 1338, 1365), EU AI Act (Regulation 2024/1689), UU PDP No. 27/2022.
2. GAYA BAHASA RENYAH, MENGALIR & RAMAH UNTUK SEMUA ORANG:
   - Bahasa harus mengalir anggun, membumi, dan tidak kaku (menghindari kesan terjemahan mesin).
   - Fokus pada ASAS HUKUM (Asas Iktikad Baik, Asas Konsensualisme, Perlindungan Martabat Manusia, Larangan Penyalahgunaan Keadaan).
   - Jangan gunakan daftar poin template kaku ('1. **X** - Y'). Gunakan esai naratif dialektis yang kaya analogi hidup.
3. KETUNTASAN & PANJANG NASKAH:
   - Pertahankan 4 sub-bagian hierarkis (### ${subCode}.1 sampai ### ${subCode}.4).
   - Perluas setiap sub-bagian dengan fakta, dialektika mendalam, dan telaah preseden empiris (target panjang sub-bab: 2.800 – 3.800 kata).
   - Di akhir naskah sub-bab, tambahkan daftar pustaka rujukan pilihan:
     #### Rujukan Terpilih Sub-bab ${subCode} (minimal 8-12 entri sitasi lengkap berstandar APA/Chicago).`;

  const user = `Berikut naskah awal Sub-bab ${subCode} yang perlu diperkaya dengan sitasi di setiap paragraf dan diperluas pembahasannya:\n\n${originalMarkdown}\n\nTuliskan versi pengayaan penuhnya sekarang!`;

  const enrichedMarkdown = await callGemini(system, user, 0.7, 8192);
  const wordCount = enrichedMarkdown.split(/\s+/).filter(Boolean).length;

  const result = {
    code: subCode,
    title: subTitle,
    contentMarkdown: enrichedMarkdown,
    wordCount: wordCount
  };

  fs.writeFileSync(enrichedFile, JSON.stringify(result, null, 2), 'utf-8');
  console.log(`   ✅ [Sub-bab ${subCode}] Sukses diperkaya: ${wordCount} kata!`);
  return result;
}

async function main() {
  console.log(`\n🚀 Memulai Engine Pengayaan Sitasi & Perluasan Naskah Monograf (Pass 2)`);
  console.log(`   Target Skala: 350 - 450+ Halaman Cetak ISO-B5`);

  const blueprintPath = path.join(CACHE_DIR, 'blueprint.json');
  const blueprint = JSON.parse(fs.readFileSync(blueprintPath, 'utf-8'));

  for (const chMeta of blueprint.chapters) {
    const chNum = chMeta.number;
    console.log(`\n═════════════════════════════════════════════════════════════════════════`);
    console.log(`📖 [Bab ${chNum}/10] Mengolah & Memperkaya: "${chMeta.title}"`);
    console.log(`═════════════════════════════════════════════════════════════════════════`);

    const subResults = [];
    for (const subMeta of chMeta.subchapters) {
      const origSubFile = path.join(SUBCHAPTER_DIR, `ch${String(chNum).padStart(2, '0')}_sub${subMeta.code.replace('.', '_')}.json`);
      let origContent = '';
      if (fs.existsSync(origSubFile)) {
        origContent = JSON.parse(fs.readFileSync(origSubFile, 'utf-8')).contentMarkdown;
      }
      const enriched = await enrichSubchapter(chNum, subMeta.code, subMeta.title, origContent);
      subResults.push(enriched);
    }

    // Rajut kembali bab final
    const fullMarkdown = [
      `# Bab ${chNum}: ${chMeta.title}\n`,
      subResults.map(s => s.contentMarkdown).join('\n\n---\n\n')
    ].join('\n\n');

    const totalWords = subResults.reduce((acc, s) => acc + s.wordCount, 0);
    const finalChapterFile = path.join(CACHE_DIR, `chapter-${String(chNum).padStart(2, '0')}-final.json`);

    const finalData = {
      chapterNumber: chNum,
      chapterTitle: chMeta.title,
      version: 'ENRICHED_MAGNUM_OPUS_EDITION',
      contentMarkdown: fullMarkdown,
      wordCount: totalWords
    };

    fs.writeFileSync(finalChapterFile, JSON.stringify(finalData, null, 2), 'utf-8');
    console.log(`🎉 [Bab ${chNum}] SELESAI DIPERKAYA: ${totalWords} Kata (~${Math.round(totalWords / 300)} Halaman ISO-B5)!`);
  }

  // Kompilasi ulang Typst
  console.log(`\n📚 Mengompilasi Naskah Edisi Definitif ke PDF Typst ISO-B5...`);
  execSync(`python3 "${path.join(__dirname, 'compile-book-typst.py')}" "${BOOK_SLUG}"`, { stdio: 'inherit' });

  // Build & Deploy
  console.log(`\n🌐 Membangun Static Site Astro & Deploy ke Cloudflare Pages...`);
  execSync(`npm run build`, { stdio: 'inherit' });
  execSync(`npx wrangler pages deploy dist --project-name=jcfad-journal --branch=main`, { stdio: 'inherit' });

  console.log(`\n🏆 PROSES REVISI & DEPLOY BUKU DEFINITIF SELESAI SEMPURNA!`);
}

main().catch(e => {
  console.error('Fatal error:', e);
  process.exit(1);
});

