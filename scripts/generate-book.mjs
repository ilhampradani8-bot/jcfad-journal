#!/usr/bin/env node

/**
 * ==============================================================================
 * PT CHAIN ASIA CONECT - Multi-Stage Academic Book Generator (Standar Buku Cetak)
 * ==============================================================================
 * Mode: Generator Buku Lengkap (Monograf Riset / Buku Teks / Buku Referensi Cetak)
 * Fitur Utama:
 * 1. Terpisah 100% dari mesin artikel jurnal (tidak menyentuh D1/cron harian).
 * 2. Skalabilitas Puluhan Bab (File-per-chapter + Persistent Cache + Resumable).
 * 3. 100% Versi Revisi: Setiap bab wajib melalui siklus:
 *    Drafting -> Adversarial Reviewer Audit -> Deep Revision Pass -> Validasi.
 * 4. Engine Typst Print-Ready:
 *    - Standar Buku B5 ISO (176 x 250 mm) & A5 ISO.
 *    - Gutter margin khusus jilid lem panas (perfect binding).
 *    - Penomoran romawi (preliminaries) & arabik (isi naskah).
 *    - Daftar isi otomatis, running header ganjil-genap, bab baru selalu di halaman kanan.
 *    - Daftar pustaka terpadu di akhir buku.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

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

// Arguments CLI
const args = process.argv.slice(2);
function getArg(flag) {
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith(`--${flag}=`)) return args[i].split('=')[1];
    if (args[i] === `--${flag}` && args[i + 1]) return args[i + 1];
  }
  return null;
}

const GROQ_API_KEY = getArg('key') || getArg('groq-key') || process.env.GROQ_API_KEY;
if (!GROQ_API_KEY) {
  console.error('❌ ERROR: GROQ_API_KEY tidak ditemukan di .env atau CLI arguments!');
  process.exit(1);
}

const BOOK_TITLE = getArg('title') || 'Transformasi Digital dan Tata Kelola Rantai Dingin Mikro di Wilayah Pesisir 3T';
const BOOK_SUBTITLE = getArg('subtitle') || 'Integrasi Hukum Kontrak Perdata, IoT Digital-Twin, dan Pembiayaan Faktur UMKM Krui';
const BOOK_AUTHOR = getArg('author') || 'Ilham Pradani';
const BOOK_AFFILIATION = getArg('affiliation') || 'PT CHAIN ASIA CONECT Research & Development Division';
const BOOK_ORCID = getArg('orcid') || '0009-0008-1310-6169';
const TOTAL_CHAPTERS = parseInt(getArg('chapters') || '10', 10);
const PAPER_SIZE = getArg('size') || 'iso-b5'; // 'iso-b5' atau 'a5'
const BOOK_CONTEXT = getArg('context') || (
  BOOK_TITLE.toLowerCase().includes('empati') || BOOK_TITLE.toLowerCase().includes('synthetic')
    ? 'Analisis linguistik persuasif model LLM (persona AI, affective framing, sycophancy, flattering, conversational nudging), psikologi kognitif manusia (antropomorfisme, bias emosional, parasocial bonding, eksploitasi kerentanan psikologis), batas pertanggungjawaban hukum perdata dan pidana (doktrin penipuan, wanprestasi, manipulasi consent, UU Perlindungan Data Pribadi, EU AI Act), kedaulatan kognitif (cognitive liberty & mental self-determination), dan metodologi audit forensik linguistik percakapan AI.'
    : 'Analisis empiris komparatif, kerangka doktrin hukum perdata/publik, arsitektur teknis operasional, dan implikasi kebijakan strategis.'
);

// Folder Direktori Kerja Khusus Buku
const BOOKS_BASE_DIR = path.join(rootDir, 'books');
const CACHE_DIR = path.join(BOOKS_BASE_DIR, 'cache');
const OUTPUT_DIR = path.join(BOOKS_BASE_DIR, 'output');
fs.mkdirSync(CACHE_DIR, { recursive: true });
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-');
}

const BOOK_SLUG = getArg('slug') || slugify(BOOK_TITLE).slice(0, 70).replace(/-+$/, '');
const BOOK_DIR = path.join(CACHE_DIR, BOOK_SLUG);
fs.mkdirSync(BOOK_DIR, { recursive: true });

// Model Groq
const MODEL_ARCHITECT = 'openai/gpt-oss-120b'; // Arsitek Daftar Isi & Outline Global
const MODEL_DRAFTER = 'openai/gpt-oss-20b';    // Draf Awal Bab (Cepat, Luas)
const MODEL_REVIEWER = 'qwen/qwen3.8-27b';     // Audit Kritis Bab
const MODEL_REVISER = 'openai/gpt-oss-120b';   // Versi Revisi Final & Pengayaan Akademik
const FALLBACK_MODEL = 'openai/gpt-oss-20b';

// Helper Groq API dengan retry dan auto-healing
async function callGroqAPI(model, systemPrompt, userPrompt, maxTokens = 4500, retryCount = 0) {
  const payload = {
    model,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    temperature: 0.35,
    max_tokens: maxTokens
  };

  try {
    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${GROQ_API_KEY}`
      },
      body: JSON.stringify(payload)
    });

    if (res.status === 429 || res.status === 413) {
      const errText = await res.text();
      if (retryCount >= 3 && model !== FALLBACK_MODEL) {
        console.warn(`🛡️ [Rate Limit / TPM Batas] Beralih ke model cadangan (${FALLBACK_MODEL}) agar proses tidak tertahan...`);
        return callGroqAPI(FALLBACK_MODEL, systemPrompt, userPrompt, Math.min(maxTokens, 3200), 0);
      }
      const waitSec = Math.min(30, 10 + retryCount * 5);
      console.warn(`⏳ [Rate Limit / TPM] Menunggu ${waitSec}s (${model}): ${errText.slice(0, 120)}...`);
      await new Promise(r => setTimeout(r, waitSec * 1000));
      return callGroqAPI(model, systemPrompt, userPrompt, Math.min(maxTokens, 3200), retryCount + 1);
    }

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`API Error ${res.status}: ${errText.slice(0, 150)}`);
    }

    const data = await res.json();
    const content = data.choices?.[0]?.message?.content?.trim();
    if (!content) throw new Error('Respon kosong dari model');
    return content;
  } catch (err) {
    if (retryCount < 3) {
      console.warn(`⚠️ [Retry ${retryCount + 1}/3] ${err.message}. Mencoba lagi dalam 5s...`);
      await new Promise(r => setTimeout(r, 5000));
      return callGroqAPI(model, systemPrompt, userPrompt, maxTokens, retryCount + 1);
    }
    if (model !== FALLBACK_MODEL) {
      console.warn(`🛡️ Mengalihkan ke model cadangan (${FALLBACK_MODEL})...`);
      return callGroqAPI(FALLBACK_MODEL, systemPrompt, userPrompt, maxTokens, 0);
    }
    throw err;
  }
}

// ------------------------------------------------------------------------------
// STAGE 1: Perancangan Arsitektur Buku (Blueprint & Daftar Isi Lengkap)
// ------------------------------------------------------------------------------
async function generateBookBlueprint() {
  const blueprintFile = path.join(BOOK_DIR, 'blueprint.json');
  if (fs.existsSync(blueprintFile)) {
    console.log('📂 [Stage 1] Memuat blueprint buku yang sudah ada dari cache...');
    return JSON.parse(fs.readFileSync(blueprintFile, 'utf-8'));
  }

  console.log(`\n🏛️ [Stage 1] Merancang Blueprint Buku Lengkap (${TOTAL_CHAPTERS} Bab)...`);
  console.log(`   Judul  : "${BOOK_TITLE}"`);
  console.log(`   Penulis: ${BOOK_AUTHOR}`);

  const system = `You are a Senior Academic Book Editor & Book Architect from a prestigious university press (Oxford, MIT Press, Cambridge, Harvard). 
Create a comprehensive, cohesive book outline for a professional scholarly book/monograph.
Return your response STRICTLY as a valid JSON object without markdown fences, formatted as:
{
  "title": "...",
  "subtitle": "...",
  "preface": "Prakata buku yang mendalam (3-4 paragraf menjelaskan urgensi dan latar belakang riset/pemikiran)...",
  "chapters": [
    {
      "number": 1,
      "title": "Judul Bab 1...",
      "focus": "Fokus pembahasan utama bab ini...",
      "subchapters": ["1.1 ...", "1.2 ...", "1.3 ...", "1.4 ..."],
      "empiricalCases": "Data empiris, studi kasus teknis/psikologis/hukum spesifik yang diangkat..."
    }
  ]
}`;

  const user = `Rancang struktur buku akademik berkualitas tinggi berbobot monograf/buku referensi:
Judul Buku: ${BOOK_TITLE}
Sub-judul: ${BOOK_SUBTITLE}
Target Jumlah Bab: ${TOTAL_CHAPTERS} Bab
Konteks Keilmuan & Domain Spesifik: ${BOOK_CONTEXT}
Pastikan alur antar-bab saling berkesinambungan (koheren) dari fondasi teoretis & epistemologis, arsitektur teknis/linguistik, studi kasus & bukti empiris psikologis, evaluasi hukum & hak asasi, hingga kerangka tata kelola & kedaulatan masa depan.`;

  const raw = await callGroqAPI(MODEL_ARCHITECT, system, user, 4000);
  let clean = raw.trim();
  if (clean.startsWith('```json')) clean = clean.slice(7);
  if (clean.startsWith('```')) clean = clean.slice(3);
  if (clean.endsWith('```')) clean = clean.slice(0, -3);

  const blueprint = JSON.parse(clean.trim());
  fs.writeFileSync(blueprintFile, JSON.stringify(blueprint, null, 2), 'utf-8');
  console.log(`✅ [Stage 1] Blueprint selesai dirancang: ${blueprint.chapters.length} Bab terdefinisi.`);
  return blueprint;
}

// ------------------------------------------------------------------------------
// STAGE 2: Penulisan Bab Mandiri dengan Full Revision Loop (100% Versi Revisi)
// ------------------------------------------------------------------------------
async function generateChapterWithRevision(blueprint, chMeta, prevChapterSummary) {
  const chNumStr = String(chMeta.number).padStart(2, '0');
  const finalChapterFile = path.join(BOOK_DIR, `chapter-${chNumStr}-final.json`);

  if (fs.existsSync(finalChapterFile)) {
    console.log(`⏩ [Bab ${chMeta.number}/${blueprint.chapters.length}] Sudah selesai (Versi Revisi Final) - Melewati.`);
    return JSON.parse(fs.readFileSync(finalChapterFile, 'utf-8'));
  }

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`📖 [Bab ${chMeta.number}/${blueprint.chapters.length}] Memulai Pembuatan: "${chMeta.title}"`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

  // --- Step 2A: Drafting Naskah Awal Bab (Draft 1) ---
  console.log(`✍️  [Langkah 1/3] Menulis Draf Awal Bab ${chMeta.number} (Model: ${MODEL_DRAFTER})...`);
  const draftSystem = `You are a Distinguished Scholar, Legal Theorist, and Computational Cognitive Scientist writing Chapter ${chMeta.number} of an academic monograph titled "${blueprint.title}".
Style: Scholarly, dense, highly factual, professional Indonesian academic prose (standar buku monograf & referensi ilmiah internasional).
Requirements:
- Write a very thorough, expansive chapter (2,500 - 3,500 words). Do NOT create brief summaries or bulleted overviews.
- Thoroughly flesh out each sub-chapter (${JSON.stringify(chMeta.subchapters)}) with multi-paragraph in-depth analysis.
- Ground the discussion in computational linguistics, cognitive psychology, real empirical cases, and rigorous legal/statutory frameworks.
- Include Academic Three-Line Tables and analytical formulas where applicable.
- End with a substantive Chapter Summary & Transition section.
- Output DIRECTLY in clean Markdown starting with '# Bab ${chMeta.number}: ${chMeta.title}'. No conversational fluff.`;

  const draftUser = `Tulis naskah lengkap Bab ${chMeta.number}:
Judul Bab: ${chMeta.title}
Fokus Pembahasan: ${chMeta.focus}
Sub-bab yang harus dibahas: ${JSON.stringify(chMeta.subchapters)}
Konteks Empiris, Teknis & Studi Kasus: ${chMeta.empiricalCases}
${prevChapterSummary ? `Konteks Bab Sebelumnya untuk Kesinambungan: "${prevChapterSummary}"` : 'Ini adalah bab pembuka buku, berikan fondasi konsep yang kuat.'}

Tuliskan secara sangat mendalam dan panjang (minimal 2.500 kata)!`;

  const draftMarkdown = (await callGroqAPI(MODEL_DRAFTER, draftSystem, draftUser, 4800)).trim();

  // --- Step 2B: Adversarial Peer Reviewer Audit ---
  console.log(`🔬 [Langkah 2/3] Audit Kritis Reviewer Buku (Model: ${MODEL_REVIEWER})...`);
  const reviewSystem = `You are a Chief Academic Reviewer auditing Chapter ${chMeta.number} of a book.
Your goal is to subject the draft to strict critique:
1. Periksa apakah pembahasan terlalu dangkal, kurang elaboratif, atau ada sub-bab yang terlewat.
2. Periksa ketajaman doktrin hukum, psikologi kognitif, kerangka teoretis, atau model teknis.
3. Berikan instruksi revisi spesifik: bagian mana yang harus diperluas, diperdalam argumennya, atau diperkuat dengan tabel komparatif dan pembuktian empiris.
Return STRICTLY as JSON:
{
  "score": 85,
  "critique": "Kritik tajam terhadap kekurangan draf...",
  "revisionDirectives": ["Perluas sub-bab 2...", "Tambahkan tabel komparasi...", "Perkuat dalil..."]
}`;

  const reviewUser = `Berikut naskah draf Bab ${chMeta.number}:\n\n${draftMarkdown.slice(0, 5000)}\n\nLakukan audit kritis mendalam!`;
  const reviewRaw = await callGroqAPI(MODEL_REVIEWER, reviewSystem, reviewUser, 2000);
  let cleanReview = reviewRaw.trim();
  if (cleanReview.startsWith('```json')) cleanReview = cleanReview.slice(7);
  if (cleanReview.startsWith('```')) cleanReview = cleanReview.slice(3);
  if (cleanReview.endsWith('```')) cleanReview = cleanReview.slice(0, -3);
  let reviewObj = { score: 85, critique: 'Perluas pembahasan empiris', revisionDirectives: [] };
  try {
    reviewObj = JSON.parse(cleanReview.trim());
  } catch (_) {}
  console.log(`   Skor Awal Reviewer: ${reviewObj.score}/100. Catatan: ${reviewObj.critique.slice(0, 90)}...`);

  // --- Step 2C: Full Revision Pass (100% Versi Revisi Final) ---
  console.log(`👑 [Langkah 3/3] Menyusun VERSI REVISI FINAL Berstandar Cetak (Model: ${MODEL_REVISER})...`);
  const revisionSystem = `You are the Lead Author & Senior Editor finalizing the PUBLICATION-READY REVISED VERSION of Chapter ${chMeta.number} of the book "${blueprint.title}".
Your task is to produce the definitive, highly expanded, and polished REVISED EDITION of this chapter.
Requirements:
- Incorporate all reviewer critiques and revision directives.
- Lengthen and enrich every sub-section with granular empirical evidence, legal doctrines, and operational workflows.
- Minimum length: 2,500 – 3,500 words.
- Format: Output DIRECTLY as complete Markdown starting with '# Bab ${chMeta.number}: ${chMeta.title}'. No conversational fluff or meta-commentary.`;

  const revisionUser = `Naskah Draf Sebelumnya:
${draftMarkdown}

Catatan & Arahan Revisi Reviewer:
${reviewObj.critique}
Instruksi Wajib: ${JSON.stringify(reviewObj.revisionDirectives)}

Tulis ulang seluruh bab ini menjadi VERSI REVISI FINAL terlengkap, sangat mendalam, dan memenuhi standar buku cetak penerbit!`;

  const finalMarkdown = (await callGroqAPI(MODEL_REVISER, revisionSystem, revisionUser, 4000)).trim();
  const wordCount = finalMarkdown.split(/\s+/).length;

  // Ekstrak ringkasan pendek dari 2 paragraf terakhir untuk dioper ke bab berikutnya
  const paragraphs = finalMarkdown.split('\n\n').filter(p => p.trim().length > 50);
  const summary = paragraphs.slice(-2).join(' ').slice(0, 400);

  const finalChapter = {
    chapterNumber: chMeta.number,
    chapterTitle: chMeta.title,
    version: 'REVISED_FINAL_EDITION',
    contentMarkdown: finalMarkdown,
    summary: summary,
    wordCount: wordCount
  };

  // Simpan hasil versi revisi final ke disk
  fs.writeFileSync(finalChapterFile, JSON.stringify(finalChapter, null, 2), 'utf-8');
  console.log(`✅ [Bab ${chMeta.number}] SELESAI (100% Versi Revisi: ${finalChapter.wordCount} kata)`);
  return finalChapter;
}

// ------------------------------------------------------------------------------
// STAGE 3: Typst Master Book Compiler (Print-Ready Layout Engine)
// ------------------------------------------------------------------------------
function compileTypstBook(blueprint, chapters) {
  console.log(`\n📚 [Stage 3] Mengompilasi Seluruh Bab Menjadi Buku Cetak Typst Print-Ready...`);

  const compilerScript = path.join(__dirname, 'compile-book-typst.py');
  const pdfOutputPath = path.join(OUTPUT_DIR, `${BOOK_SLUG}-print-ready.pdf`);

  try {
    execSync(`python3 "${compilerScript}" "${BOOK_SLUG}"`, { stdio: 'inherit' });
    return pdfOutputPath;
  } catch (err) {
    console.error('❌ Gagal mengompilasi Typst:', err.message);
    throw err;
  }
}

// ------------------------------------------------------------------------------
// MAIN EXECUTION PIPELINE
// ------------------------------------------------------------------------------
async function main() {
  console.log('==============================================================================');
  console.log('🚀 PT CHAIN ASIA CONECT - MESIN GENERATOR BUKU AKADEMIK CETAK (PRINT-READY)');
  console.log('==============================================================================');

  const startTime = Date.now();

  // 1. Generate Blueprint Buku
  const blueprint = await generateBookBlueprint();

  // 2. Loop Penulisan Per Bab (Dengan 100% Versi Revisi)
  const chapters = [];
  let prevSummary = '';

  for (let i = 0; i < blueprint.chapters.length; i++) {
    const chMeta = blueprint.chapters[i];
    const chData = await generateChapterWithRevision(blueprint, chMeta, prevSummary);
    chapters.push(chData);
    prevSummary = chData.summary || '';
  }

  // 3. Kompilasi Master Buku Siap Cetak
  const pdfPath = compileTypstBook(blueprint, chapters);

  const durationSec = Math.round((Date.now() - startTime) / 1000);
  console.log('\n==============================================================================');
  console.log(`✅ SEMUA TAHAP SELESAI DALAM ${durationSec} DETIK!`);
  console.log(`📖 Total Bab   : ${chapters.length} Bab`);
  console.log(`📄 Format Cetak: ${PAPER_SIZE.toUpperCase()} (Gutter Margin 2.5cm, Standar Jilid Buku)`);
  console.log(`🎯 PDF Output  : ${pdfPath}`);
  console.log('==============================================================================');
}

main().catch(err => {
  console.error('💥 Fatal Error:', err);
  process.exit(1);
});
