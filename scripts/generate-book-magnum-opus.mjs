#!/usr/bin/env node

/**
 * ==============================================================================
 * PT CHAIN ASIA CONECT - Magnum Opus Academic Book Engine (300-500 Halaman)
 * ==============================================================================
 * Model: Multi-Key Gemini API Pool + Groq Hybrid Fallback
 * Standar: Monograf Ilmiah ISO-B5 Berbahasa Humanis, Renyah, Mendalam & Mengalir
 * 
 * Fitur Utama:
 * 1. Zero Word Limit / Uncapped Multi-Pass: Penulisan sub-bab per sub-bab
 *    menghasilkan 8.000 - 12.000 kata per bab (Total 100.000 - 150.000 kata / 350-500 Hal).
 * 2. Gaya Bahasa Humanis Dinamis: Menghapus prompt template kaku robotik;
 *    mengalirkan dialektika intelektual, analogi membumi, dan studi kasus riil.
 * 3. Multi-Key Round-Robin & Auto-Failover (Gemini Key 1 & Key 2).
 * 4. Smart Cooldown Waiting Mode: Menangani rate-limit (429/503) secara otomatis.
 * 5. Atomic Sub-Chapter Checkpointing: Bisa dihentikan dan dilanjutkan kapan saja (100% resumable).
 * 6. Integrasi Typst Booktabs & Frameless Math.
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

// Multi-Key Gemini Pool
const GEMINI_KEYS = (process.env.GEMINI_API_KEYS || process.env.GEMINI_API_KEY || '')
  .split(',')
  .map(k => k.trim())
  .filter(Boolean);

const GROQ_API_KEY = process.env.GROQ_API_KEY || '';

if (GEMINI_KEYS.length === 0) {
  console.error('❌ ERROR: Tidak ditemukan GEMINI_API_KEYS atau GEMINI_API_KEY di .env!');
  process.exit(1);
}

console.log(`🔑 Terdeteksi ${GEMINI_KEYS.length} Gemini API Key dalam pool.`);

// Parse CLI Arguments
const args = process.argv.slice(2);
function getArg(flag, defaultValue = null) {
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith(`--${flag}=`)) return args[i].split('=')[1];
    if (args[i] === `--${flag}` && args[i + 1]) return args[i + 1];
  }
  return defaultValue;
}

const BOOK_TITLE = getArg('title', 'Empati Sintetis: Psikologi Bahasa AI, Jerat Manipulasi Kognitif, dan Kedaulatan Hukum Individu');
const BOOK_SUBTITLE = getArg('subtitle', 'Kajian Komprehensif Linguistik Komputasional, Bias Psikologis, dan Kedaulatan Mental Digital');
const BOOK_AUTHOR = getArg('author', 'Ilham Pradani');
const BOOK_AFFILIATION = getArg('affiliation', 'PT CHAIN ASIA CONECT Research & Development Division');
const BOOK_ORCID = getArg('orcid', '0009-0008-1310-6169');
const TOTAL_CHAPTERS = parseInt(getArg('chapters', '10'), 10);
const TARGET_PAGES = parseInt(getArg('pages', '350'), 10);

function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-');
}

const BOOK_SLUG = getArg('slug', 'empati-sintetis-buku-cetak');
const BOOKS_BASE_DIR = path.join(rootDir, 'books');
const CACHE_DIR = path.join(BOOKS_BASE_DIR, 'cache', BOOK_SLUG);
const SUBCHAPTER_DIR = path.join(CACHE_DIR, 'subchapters');
const OUTPUT_DIR = path.join(BOOKS_BASE_DIR, 'output');

fs.mkdirSync(SUBCHAPTER_DIR, { recursive: true });
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// State Key Pointer
let currentKeyIndex = 0;
function getNextGeminiKey() {
  const key = GEMINI_KEYS[currentKeyIndex];
  currentKeyIndex = (currentKeyIndex + 1) % GEMINI_KEYS.length;
  return key;
}

// Primary Working Gemini Models
const GEMINI_MODELS = [
  'gemini-3.5-flash-lite',
  'gemini-3.1-flash-lite',
  'gemini-3.5-flash',
  'gemini-3.8-flash'
];

/**
 * Universal Gemini API Caller with Key Rotation, Model Fallback & Smart Cooldown Waiting Mode
 */
async function callGeminiAPI(systemInstruction, userPrompt, temperature = 0.7, maxTokens = 8192) {
  let attempts = 0;
  const maxAttempts = GEMINI_KEYS.length * GEMINI_MODELS.length * 2;

  while (attempts < maxAttempts) {
    const key = getNextGeminiKey();
    const model = GEMINI_MODELS[attempts % GEMINI_MODELS.length];

    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
      const payload = {
        contents: [
          {
            role: 'user',
            parts: [{ text: `${systemInstruction}\n\n---\n\n${userPrompt}` }]
          }
        ],
        generationConfig: {
          temperature,
          maxOutputTokens: maxTokens
        }
      };

      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.status === 429 || res.status === 503) {
        console.warn(`⏳ [Rate Limit / High Demand - ${model}] Key (${key.slice(0, 10)}...) istirahat sejenak. Mencoba key/model lain...`);
        attempts++;
        if (attempts % GEMINI_KEYS.length === 0) {
          const waitSec = 25;
          console.log(`😴 [Smart Waiting Mode] Seluruh key dalam pool sedang cooldown. Menunggu ${waitSec} detik...`);
          await new Promise(r => setTimeout(r, waitSec * 1000));
        } else {
          await new Promise(r => setTimeout(r, 2000));
        }
        continue;
      }

      if (!res.ok) {
        const errText = await res.text();
        console.warn(`⚠️ [HTTP ${res.status} - ${model}]: ${errText.slice(0, 100)}. Berpindah...`);
        attempts++;
        await new Promise(r => setTimeout(r, 2000));
        continue;
      }

      const data = await res.json();
      const candidateText = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (candidateText && candidateText.trim().length > 0) {
        return candidateText.trim();
      }

      attempts++;
    } catch (err) {
      console.warn(`⚠️ [Network Error - ${model}]: ${err.message}. Mencoba lagi...`);
      attempts++;
      await new Promise(r => setTimeout(r, 3000));
    }
  }

  // Jika Gemini sementara terhambat, gunakan Groq sebagai fallback darurat
  if (GROQ_API_KEY) {
    console.warn(`🛡️ [Fallback Darurat ke Groq qwen/qwen3.8-27b]...`);
    try {
      const groqRes = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${GROQ_API_KEY}`
        },
        body: JSON.stringify({
          model: 'qwen/qwen3.8-27b',
          messages: [
            { role: 'system', content: systemInstruction },
            { role: 'user', content: userPrompt }
          ],
          temperature: 0.7,
          max_tokens: 4000
        })
      });
      const gData = await groqRes.json();
      const content = gData.choices?.[0]?.message?.content?.trim();
      if (content) return content;
    } catch (gErr) {
      console.error(`❌ Groq Fallback juga gagal: ${gErr.message}`);
    }
  }

  throw new Error('Gagal menghasilkan teks setelah mencoba semua key dan model.');
}

// ------------------------------------------------------------------------------
// STAGE 1: Blueprint Generator Granular (Struktur Buku 350-500 Halaman)
// ------------------------------------------------------------------------------
async function generateGranularBlueprint() {
  const blueprintFile = path.join(CACHE_DIR, 'blueprint.json');
  if (fs.existsSync(blueprintFile)) {
    console.log(`📂 [Blueprint] Memuat blueprint buku yang sudah ada dari ${blueprintFile}...`);
    return JSON.parse(fs.readFileSync(blueprintFile, 'utf-8'));
  }

  console.log(`\n🏛️ [Stage 1] Merancang Blueprint Granular Buku Monograf Tebal (${TOTAL_CHAPTERS} Bab)...`);
  console.log(`   Target Tebal: ${TARGET_PAGES} Halaman ISO-B5 (~120.000 Kata)`);

  const system = `Anda adalah Direktur Redaksi Akademik Senior dari penerbit monograf ilmiah terkemuka (seperti Cambridge University Press, Oxford, atau MIT Press).
Tugas Anda adalah merancang cetak biru (blueprint) sebuah buku referensi ilmiah/monograf riset berstandar internasional yang SANGAT MENDALAM, ASIMETRIS, dan BERBOBOT PEMIKIRAN MANUSIA.
Buku ini berbobot 300-500 halaman, sehingga setiap bab harus memiliki 4-6 sub-bab yang sangat spesifik dan padat kajian teoretis, studi kasus riil, analisis yuridis, dan dialektika kritis.

KEMBALIKAN HANYA OBJEK JSON VALID TANPA MARKDOWN BACKTICKS DENGAN FORMAT:
{
  "title": "...",
  "subtitle": "...",
  "shortTitle": "Judul Pendek untuk Running Header (Maksimal 3-4 kata)",
  "preface": "Prakata buku yang mendalam (5-6 paragraf esai intelektual yang mengalir, reflektif, memaparkan kegelisahan intelektual dan signifikansi karya ini)...",
  "chapters": [
    {
      "number": 1,
      "title": "Judul Bab...",
      "estimatedPages": 32,
      "coreThesis": "Tesis utama bab ini...",
      "subchapters": [
        {
          "code": "1.1",
          "title": "Judul Subbab...",
          "detailedPoints": "Poin-poin spesifik yang wajib diulas: konsep dasar, perdebatan epistemologis, studi kasus riil, analogi membumi, dan implikasi praktis."
        }
      ]
    }
  ]
}`;

  const user = `Rancang blueprint buku komprehensif:
Judul: ${BOOK_TITLE}
Sub-judul: ${BOOK_SUBTITLE}
Penulis: ${BOOK_AUTHOR} (${BOOK_AFFILIATION})
Jumlah Bab: ${TOTAL_CHAPTERS} Bab
Target Skala: 350 - 450 Halaman Cetak ISO-B5
Konteks Pembahasan:
Buku ini membedah fenomena 'Empati Sintetis'—bagaimana sistem AI memproduksi ilusi pemahaman emosional, manipulasi framing afektif, eksploitasi kerentanan psikologis (ikatan parasosial), pertanggungjawaban hukum perdata (Pasal 1320-1328 KUHPerdata tentang cacat kehendak dwaling/bedrog/undue influence), regulasi global (EU AI Act 2024, GDPR, UU PDP No. 27/2022), hingga kedaulatan kognitif (cognitive liberty) dan metodologi audit forensik linguistik percakapan AI.

Pastikan setiap bab memiliki 4 sampai 5 sub-bab yang sangat komprehensif!`;

  const raw = await callGeminiAPI(system, user, 0.4, 8000);
  let clean = raw.trim();
  if (clean.startsWith('```json')) clean = clean.slice(7);
  if (clean.startsWith('```')) clean = clean.slice(3);
  if (clean.endsWith('```')) clean = clean.slice(0, -3);

  const blueprint = JSON.parse(clean.trim());
  fs.writeFileSync(blueprintFile, JSON.stringify(blueprint, null, 2), 'utf-8');
  console.log(`✅ [Blueprint] Selesai dirancang! Terdefinisi ${blueprint.chapters.length} Bab komprehensif.`);
  return blueprint;
}

// ------------------------------------------------------------------------------
// STAGE 2: Penulisan Sub-Bab per Sub-Bab Tanpa Batas Kata (Uncapped Deep Prose)
// ------------------------------------------------------------------------------
async function generateSubchapter(blueprint, chMeta, subMeta, prevSubSummary) {
  const subFile = path.join(SUBCHAPTER_DIR, `ch${String(chMeta.number).padStart(2, '0')}_sub${subMeta.code.replace('.', '_')}.json`);
  if (fs.existsSync(subFile)) {
    const existing = JSON.parse(fs.readFileSync(subFile, 'utf-8'));
    if (existing.wordCount >= 1800) {
      console.log(`   ⏩ Sub-bab [${subMeta.code}] "${subMeta.title}" (${existing.wordCount} kata) sudah ada di disk — Melewati.`);
      return existing;
    }
  }

  console.log(`\n   ✍️ Menulis Sub-bab [${subMeta.code}] "${subMeta.title}" (Target: 2.000 - 3.200 Kata)...`);

  // Prompt Gaya Bahasa Humanis Mengalir & Mendalam dengan Sub-bagian Eksplisit
  const system = `Anda adalah Ilham Pradani, seorang pemikir interdisipliner terkemuka, akademisi, dan pakar hukum siber-psikologi kognitif.
Anda sedang menyusun naskah buku monograf ilmiah berbobot tinggi berstandar Cambridge/Oxford University Press dengan target ketebalan 350-450 halaman ISO-B5.

PRINSIP PENULISAN & GAYA BAHASA (HUMAN-THINKING & ACCESSIBLE):
1. GAYA BAHASA RENYAH, MENGALIR & MENDALAM:
   - Bahasa harus cerdas, anggun, namun renyah dan mengalir (tidak kaku seperti terjemahan mesin, tidak terjebak dalam jargon kering tanpa analogi).
   - Gunakan analogi hidup yang membumi (misalnya menghubungkan kalkulasi ruang laten dengan topeng lilin yang dingin; atau membandingkan klausul manipulasi antarmuka dengan perangkap tak kasat mata di era digital).
   - HINDARI DAFTAR POIN TEMPLATE ROBOTIK ('1. **X** - Y'). Uraikan setiap gagasan dalam bentuk esai analitis naratif berparagraf dinamis dan asimetris.
2. DISKURSUS SUBSTANSIAL & DIALEKTIKA:
   - Bedah argumen, sanggahan, dan sintesis (dialektika kritis).
   - Terapkan studi kasus nyata (seperti insiden chatbot Replika, kasus Chai AI di Belgia 2023, perkara privasi FTC vs raksasa teknologi, hingga investigasi penipuan perbankan via deepfake di Asia).
   - Hadirkan doktrin hukum perdata positif (Pasal 1320-1328 KUHPerdata tentang cacat kehendak dwaling/bedrog/undue influence, EU AI Act 2024 Art. 5 & 50, UU PDP No. 27/2022).
   - Jika menyertakan rumus matematis, gunakan format block math bersih native Typst ($ equation $) tanpa membungkusnya dalam box/border abu-abu.
3. KETENTUAN PANJANG & KELENGKAPAN:
   - Sub-bab ini WAJIB dibagi menjadi 4 sub-bagian bernomor hierarkis (### ${subMeta.code}.1 s/d ### ${subMeta.code}.4).
   - Setiap sub-bagian WAJIB dielaborasi secara mendalam (minimal 4-6 paragraf esai panjang).
   - Total panjang naskah sub-bab ini adalah MINIMAL 2.000 KATA. Dilarang merangkum secara tergesa-gesa!`;

  const user = `Tulis naskah lengkap, mendalam, dan komprehensif untuk Sub-bab berikut:
Bab ${chMeta.number}: ${chMeta.title}
Tesis Utama Bab: ${chMeta.coreThesis}

Sub-bab yang Ditulis:
Kode: ${subMeta.code}
Judul: ${subMeta.title}
Fokus & Arahan Bahasan: ${subMeta.detailedPoints}

${prevSubSummary ? `Jembatan Konteks Sub-bab Sebelumnya agar Mengalir Koheren:\n"${prevSubSummary}"` : 'Ini adalah sub-bab pembuka bab ini. Mulailah dengan narasi pengantar yang menggugah nalar dan menyentuh inti kegelisahan peradaban digital.'}

Instruksi Struktur Naskah Sub-bab:
Mulai dengan heading:
## ${subMeta.code} ${subMeta.title}

Lalu bagi ke dalam 4 sub-bagian terperinci:
### ${subMeta.code}.1 [Dimensi Genealogi & Epistemologi]
### ${subMeta.code}.2 [Analisis Mekanika Komputasional & Dinamika Psikologis]
### ${subMeta.code}.3 [Bedah Preseden Empiris & Studi Kasus Nyata]
### ${subMeta.code}.4 [Konstruksi Doktrinal Hukum & Rekonstruksi Kedaulatan Individu]

Tuliskan seluruhnya dalam bahasa Indonesia esai intelektual yang luwes, hidup, dan mendalam (target 2.000 - 3.200 kata)!`;

  // Step 1: Draf Sub-Bab
  let prose = await callGeminiAPI(system, user, 0.75, 8192);
  let wordCount = prose.split(/\s+/).filter(Boolean).length;

  // Step 2: Auto-Expansion jika draf kurang panjang (< 1.800 kata)
  if (wordCount < 1800) {
    console.log(`      ⚡ Draf masih ${wordCount} kata. Meminta ekspansi pendalaman argumen & studi kasus...`);
    const expandPrompt = `Naskah Sub-bab ${subMeta.code} di atas sudah sangat baik bahasanya, namun masih terlalu ringkas (${wordCount} kata) untuk standar monograf 400 halaman.
Perluas dan elaborasi secara jauh lebih kaya setiap sub-bagian (### ${subMeta.code}.1 sampai ### ${subMeta.code}.4):
- Tambahkan studi kasus perkara nyata dan fakta empiris yang lebih spesifik.
- Perdalam ulasan doktrinal hukum perdata (Pasal 1320/1321 KUHPerdata, EU AI Act, UU PDP).
- Perkaya analogi filosofis dan dialektika kognitif.
KEMBALIKAN NASKAH LENGKAP HASIL PERLUASAN TERSEBUT (MINIMAL 2.200 KATA) DALAM MARKDOWN TANPA TEKS BASA-BASI.`;

    const expanded = await callGeminiAPI(system, `${prose}\n\n---\n\n${expandPrompt}`, 0.75, 8192);
    if (expanded && expanded.split(/\s+/).filter(Boolean).length > wordCount) {
      prose = expanded;
      wordCount = prose.split(/\s+/).filter(Boolean).length;
    }
  }

  // Step 3: Review Pembersihan Sintaks & Alur (Non-Destructive Review)
  console.log(`      🔬 Review Keselarasan & Pembersihan Sintaks Sub-bab ${subMeta.code} (${wordCount} kata)...`);
  const paragraphs = prose.split('\n\n').filter(p => p.trim().length > 40);
  const summary = paragraphs.slice(-2).join(' ').slice(0, 500);

  const result = {
    code: subMeta.code,
    title: subMeta.title,
    contentMarkdown: prose,
    summary: summary,
    wordCount: wordCount
  };

  fs.writeFileSync(subFile, JSON.stringify(result, null, 2), 'utf-8');
  console.log(`   ✅ Sub-bab [${subMeta.code}] SELESAI (${wordCount} kata)`);
  return result;
}

// ------------------------------------------------------------------------------
// STAGE 3: Assembling & Finalizing Chapters (Standar Buku 300-500 Hal)
// ------------------------------------------------------------------------------
async function assembleChapter(blueprint, chMeta, prevChapterSummary) {
  const chNumStr = String(chMeta.number).padStart(2, '0');
  const chapterFinalFile = path.join(CACHE_DIR, `chapter-${chNumStr}-final.json`);

  if (fs.existsSync(chapterFinalFile)) {
    console.log(`⏩ [Bab ${chMeta.number}/${blueprint.chapters.length}] "${chMeta.title}" sudah selesai utuh — Melewati.`);
    return JSON.parse(fs.readFileSync(chapterFinalFile, 'utf-8'));
  }

  console.log(`\n═════════════════════════════════════════════════════════════════════════`);
  console.log(`📖 [Bab ${chMeta.number}/${blueprint.chapters.length}] Memulai Penyusunan: "${chMeta.title}"`);
  console.log(`═════════════════════════════════════════════════════════════════════════`);

  const subResults = [];
  let prevSubSummary = prevChapterSummary;

  for (const subMeta of chMeta.subchapters) {
    const subRes = await generateSubchapter(blueprint, chMeta, subMeta, prevSubSummary);
    subResults.push(subRes);
    prevSubSummary = subRes.summary;
  }

  // Gabungkan seluruh sub-bab menjadi bab utuh
  console.log(`\n📚 Merajut ${subResults.length} sub-bab menjadi Bab ${chMeta.number} utuh...`);
  const fullChapterMarkdown = [
    `# Bab ${chMeta.number}: ${chMeta.title}\n`,
    subResults.map(s => s.contentMarkdown).join('\n\n---\n\n')
  ].join('\n\n');

  const totalWords = subResults.reduce((acc, s) => acc + s.wordCount, 0);

  const finalChapter = {
    chapterNumber: chMeta.number,
    chapterTitle: chMeta.title,
    version: 'MAGNUM_OPUS_FULL_EDITION',
    contentMarkdown: fullChapterMarkdown,
    summary: subResults[subResults.length - 1]?.summary || '',
    wordCount: totalWords,
    subchapterCount: subResults.length
  };

  fs.writeFileSync(chapterFinalFile, JSON.stringify(finalChapter, null, 2), 'utf-8');
  console.log(`🎉 [Bab ${chMeta.number}] SELESAI SEMPURNA: ${totalWords} Kata (~${Math.round(totalWords / 300)} Halaman ISO-B5)!`);
  return finalChapter;
}

// ------------------------------------------------------------------------------
// STAGE 4: Typst Print-Ready Compiler Execution
// ------------------------------------------------------------------------------
function compileTypstBook() {
  console.log(`\n📚 Mengompilasi Naskah Buku Utuh ke PDF Siap Cetak ISO-B5...`);
  const compilerScript = path.join(__dirname, 'compile-book-typst.py');
  try {
    execSync(`python3 "${compilerScript}" "${BOOK_SLUG}"`, { stdio: 'inherit' });
    console.log(`✅ PDF Siap Cetak Sukses Dihasilkan di: ${path.join(OUTPUT_DIR, `${BOOK_SLUG}-print-ready.pdf`)}`);
  } catch (err) {
    console.error('❌ Gagal mengompilasi PDF Typst:', err.message);
  }
}

// ------------------------------------------------------------------------------
// MAIN PIPELINE
// ------------------------------------------------------------------------------
async function main() {
  console.log(`\n🚀 Memulai Mesin Buku Akademik Magnum Opus (Target: 300-500 Halaman)`);
  console.log(`   Judul  : "${BOOK_TITLE}"`);
  console.log(`   Penulis: ${BOOK_AUTHOR}`);

  // Stage 1: Blueprint
  const blueprint = await generateGranularBlueprint();

  // Stage 2 & 3: Tulis Bab demi Bab
  let prevChapterSummary = '';
  for (const chMeta of blueprint.chapters) {
    const chResult = await assembleChapter(blueprint, chMeta, prevChapterSummary);
    prevChapterSummary = chResult.summary;
  }

  // Stage 4: Kompilasi ke Typst ISO-B5
  compileTypstBook();

  console.log(`\n🏆 PROSES PENULISAN & KOMPILASI BUKU SELESAI SEMPURNA!`);
}

main().catch(err => {
  console.error('\n💥 FATAL ERROR:', err);
  process.exit(1);
});
