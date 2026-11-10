#!/usr/bin/env node

/**
 * ==============================================================================
 * PT CHAIN ASIA CONECT - Turbo Academic Book Translation & Amazon KDP Engine
 * ==============================================================================
 * Translates "Empati Sintetis / Manipulative Intelligence" (10 Chapters) to English
 * Target: Amazon KDP Print-Ready Paperback (7" × 10" Standard Scholarly Trim)
 * Features:
 *  - 4x Parallel Concurrency across Multi-Key Gemini Pool + Groq Turbo
 *  - Granular Sub-section Checkpointing (100% Resumable, Zero Data Loss)
 *  - Matches Cover Title: "Manipulative Intelligence: Reclaiming Your Consciousness in the Age of AI"
 * ==============================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// 1. Load environment
const envPath = path.join(rootDir, '.env');
const envVars = {};
if (fs.existsSync(envPath)) {
  const lines = fs.readFileSync(envPath, 'utf-8').split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
      const [k, ...v] = trimmed.split('=');
      envVars[k.trim()] = v.join('=').trim().replace(/^["']|["']$/g, '');
    }
  }
}

const rawGemini = envVars.GEMINI_API_KEYS || envVars.GEMINI_API_KEY || '';
const GEMINI_KEYS = rawGemini
  .split(',')
  .map(k => k.trim().replace(/^["']|["']$/g, ''))
  .filter(Boolean);

const GROQ_KEY = (envVars.GROQ_API_KEY || '').trim().replace(/^["']|["']$/g, '');

let geminiKeyIndex = 0;
function getNextGeminiKey() {
  const key = GEMINI_KEYS[geminiKeyIndex % GEMINI_KEYS.length];
  geminiKeyIndex++;
  return key;
}

const GEMINI_MODELS = [
  'gemini-3.5-flash',
  'gemini-3.5-flash-lite',
  'gemini-flash-latest'
];

const SRC_SLUG = 'empati-sintetis-buku-cetak';
const TGT_SLUG = 'synthetic-empathy-english-edition';

const SRC_DIR = path.join(rootDir, 'books', 'cache', SRC_SLUG);
const TGT_DIR = path.join(rootDir, 'books', 'cache', TGT_SLUG);
const SEC_CACHE_DIR = path.join(TGT_DIR, 'sections_cache');
const OUTPUT_DIR = path.join(rootDir, 'books', 'output');

fs.mkdirSync(SEC_CACHE_DIR, { recursive: true });
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

/**
 * High-Speed AI Caller with Gemini Multi-Key & Groq Parallel Support
 */
async function callAI(systemPrompt, userText, maxTokens = 8192, preferGroq = false) {
  for (let round = 0; round < 18; round++) {
    // Option A: If preferGroq is set on this worker thread, try Groq first for dual-provider parallelism
    if (preferGroq && GROQ_KEY && userText.length < 11000) {
      for (const groqModel of ['qwen/qwen3.8-27b', 'openai/gpt-oss-120b']) {
        try {
          const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            signal: AbortSignal.timeout(25000),
            headers: {
              'Authorization': `Bearer ${GROQ_KEY}`,
              'Content-Type': 'application/json',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'
            },
            body: JSON.stringify({
              model: groqModel,
              messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userText }
              ],
              temperature: 0.25,
              max_tokens: 4096
            })
          });
          if (res.ok) {
            const data = await res.json();
            const text = data.choices?.[0]?.message?.content;
            if (text && text.trim().length > 20) return text.trim();
          }
        } catch (_) {}
      }
    }

    // Option B: Try Gemini Pool
    for (let mIdx = 0; mIdx < GEMINI_MODELS.length; mIdx++) {
      const key = getNextGeminiKey();
      const model = GEMINI_MODELS[(round + mIdx) % GEMINI_MODELS.length];
      try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
        const payload = {
          contents: [
            {
              role: 'user',
              parts: [{ text: `${systemPrompt}\n\n[TEXT TO TRANSLATE]:\n${userText}` }]
            }
          ],
          generationConfig: {
            temperature: 0.25,
            maxOutputTokens: maxTokens
          }
        };

        const res = await fetch(url, {
          method: 'POST',
          signal: AbortSignal.timeout(30000),
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          const data = await res.json();
          const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
          if (text && text.trim().length > 20) {
            return text.trim();
          }
        }
      } catch (_) {}
    }

    // Option C: Fallback to Groq
    if (GROQ_KEY) {
      for (const groqModel of ['qwen/qwen3.8-27b', 'openai/gpt-oss-120b']) {
        try {
          const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            signal: AbortSignal.timeout(25000),
            headers: {
              'Authorization': `Bearer ${GROQ_KEY}`,
              'Content-Type': 'application/json',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'
            },
            body: JSON.stringify({
              model: groqModel,
              messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userText }
              ],
              temperature: 0.25,
              max_tokens: 4096
            })
          });
          if (res.ok) {
            const data = await res.json();
            const text = data.choices?.[0]?.message?.content;
            if (text && text.trim().length > 20) return text.trim();
          }
        } catch (_) {}
      }
    }

    await new Promise(r => setTimeout(r, 3000 + round * 2500));
  }

  throw new Error('All AI providers failed after retries.');
}

const ACADEMIC_SYSTEM_PROMPT = `You are an elite scholarly translator and bestselling non-fiction academic editor specializing in computational linguistics, cognitive psychology, AI ethics, and international comparative law.

Your task is to translate the provided Indonesian scholarly monograph text into sophisticated, gripping, highly fluent academic English suitable for an international readership on Amazon KDP and university presses.

STRICT TRANSLATION RULES:
1. STYLE & VOCABULARY: Maintain a compelling, authoritative, and lucid tone. Avoid robotic literal translations.
2. CITATIONS: Preserve ALL in-text academic citations exactly (e.g., Zuboff, 2019; Kahneman, 2011; Searle, 1980; Subekti, 2005; Weizenbaum, 1976).
3. COMPARATIVE LAW TERMINOLOGY:
   - "Hukum Perdata" -> "Civil Law"
   - "KUHPerdata" -> "Indonesian Civil Code (Burgerlijk Wetboek)"
   - "Cacat Kehendak" -> "Defects of Will / Vitiated Consent"
   - "Dwaling" -> "Mistake / Error (*dwaling*)"
   - "Bedrog" -> "Fraud / Deceit (*bedrog*)"
   - "Penyalahgunaan Keadaan" -> "Undue Influence (*misbruik van omstandigheden*)"
   - "Kedaulatan Kognitif / Kebebasan Kognitif" -> "Cognitive Liberty / Cognitive Sovereignty"
   - "UU PDP (UU No. 27/2022)" -> "Indonesian Personal Data Protection Act (Law No. 27/2022)"
4. TABLES: Translate all table headers and cells into English, strictly preserving Markdown table syntax (| Col 1 | Col 2 |).
5. MATH & CODE: Keep mathematical expressions ($ ... $) unchanged. Translate "Catatan Pemahaman Awam:" to "*Intuitive Conceptual Note:*".
6. FORMAT INTEGRITY: Keep all Markdown headers (#, ##, ###, ####) and bullet structures. Remove any square brackets around sub-heading titles (e.g., change "### 1.1.1 [Dimensi Genealogi]" to "### Genealogical and Epistemological Dimensions").
7. PURITY: Output ONLY the translated text. Never include greetings or meta-commentary.`;

const ENGLISH_CHAPTER_TITLES = [
  "Anatomy of Synthetic Empathy and the Genealogy of Algorithmic Language",
  "The Psychology of AI Language and the Exploitation of Parasocial Bonds",
  "Affective Framing Manipulation and Subliminal Behavioral Engineering",
  "Defects of Will in Civil Law: Mistake, Fraud, and Undue Influence",
  "Civil Liability and Algorithmic Product Liability",
  "Global Regulatory Frameworks: The EU AI Act, GDPR, and Comparative Data Sovereignty",
  "Cognitive Liberty as an Emerging Fundamental Human Right",
  "Methodologies for Forensic Linguistic Auditing of Conversational AI",
  "Empirical Case Studies: Real-World Manifestations of Affective Exploitation",
  "Toward an Ethical AI Ecosystem: Legal Reconstruction and Humane Architectural Design"
];

async function ensureBlueprint() {
  const tgtBpPath = path.join(TGT_DIR, 'blueprint.json');
  const srcBpPath = path.join(SRC_DIR, 'blueprint.json');
  const srcBp = JSON.parse(fs.readFileSync(srcBpPath, 'utf-8'));

  let prefaceEn = '';
  if (fs.existsSync(tgtBpPath)) {
    const existing = JSON.parse(fs.readFileSync(tgtBpPath, 'utf-8'));
    prefaceEn = existing.preface || '';
  }
  if (!prefaceEn) {
    console.log('📘 Translating Preface...');
    prefaceEn = await callAI(ACADEMIC_SYSTEM_PROMPT, srcBp.preface);
  }

  const tgtBp = {
    title: "Manipulative Intelligence: Reclaiming Your Consciousness in the Age of AI",
    subtitle: "Synthetic Empathy, the Psychology of AI Language, Cognitive Manipulation Loops, and Individual Legal Sovereignty",
    shortTitle: "Manipulative Intelligence",
    author: "Ilham Pradani",
    orcid: "0009-0008-1310-6169",
    affiliation: "PT CHAIN ASIA CONECT Research & Development Division",
    imprintPublisher: "PT CHAIN ASIA CONECT Scholarly Publishing Series",
    imprintPlace: "Jakarta & Krui, Indonesia",
    license: "Creative Commons Attribution 4.0 International (CC BY 4.0)",
    trimSize: "7\" × 10\" (Standard Amazon KDP Scholarly Trim)",
    edition: "First International Edition (Print-Ready Paperback)",
    year: "2026",
    preface: prefaceEn,
    chapters: srcBp.chapters.map((ch, idx) => ({
      number: ch.number,
      title: ENGLISH_CHAPTER_TITLES[idx] || ch.title,
      coreThesis: ch.coreThesis,
      subchapters: ch.subchapters || []
    }))
  };

  fs.writeFileSync(tgtBpPath, JSON.stringify(tgtBp, null, 2), 'utf-8');
  return tgtBp;
}

/**
 * Translate a single Chapter using Parallel Worker Pool (Concurrency = 4)
 */
async function translateChapter(chNumber) {
  const chNumStr = String(chNumber).padStart(2, '0');
  const tgtFilePath = path.join(TGT_DIR, `chapter-${chNumStr}-final.json`);

  if (fs.existsSync(tgtFilePath)) {
    const existing = JSON.parse(fs.readFileSync(tgtFilePath, 'utf-8'));
    if (existing.contentMarkdown && existing.contentMarkdown.length > 5000) {
      console.log(`⏩ Chapter ${chNumber} already complete (${existing.wordCount} words).`);
      return existing;
    }
  }

  const srcFilePath = path.join(SRC_DIR, `chapter-${chNumStr}-final.json`);
  const srcData = JSON.parse(fs.readFileSync(srcFilePath, 'utf-8'));
  const rawContent = srcData.contentMarkdown;

  // Split by ## or ### headings
  const rawSections = rawContent.split(/(?=\n#{2,3}\s+)/).map(s => s.trim()).filter(Boolean);
  const translatedSections = new Array(rawSections.length);

  console.log(`\n📖 Translating Chapter ${chNumber} (${rawSections.length} sections) with 4x Parallel Workers...`);

  // Queue of section indices
  const queue = [];
  for (let i = 0; i < rawSections.length; i++) {
    const secCacheFile = path.join(SEC_CACHE_DIR, `ch${chNumStr}_sec${String(i).padStart(2, '0')}.json`);
    if (fs.existsSync(secCacheFile)) {
      const cached = JSON.parse(fs.readFileSync(secCacheFile, 'utf-8'));
      translatedSections[i] = cached.text;
    } else {
      queue.push(i);
    }
  }

  console.log(`   Cached: ${rawSections.length - queue.length}/${rawSections.length} | Remaining: ${queue.length}`);

  const CONCURRENCY = 3;
  async function worker(workerId) {
    while (queue.length > 0) {
      const sIdx = queue.shift();
      if (sIdx === undefined) break;

      const secText = rawSections[sIdx];
      const secCacheFile = path.join(SEC_CACHE_DIR, `ch${chNumStr}_sec${String(sIdx).padStart(2, '0')}.json`);
      const firstLine = secText.split('\n')[0].slice(0, 55);

      console.log(`   [W${workerId} | Ch ${chNumber} Sec ${sIdx + 1}/${rawSections.length}] "${firstLine}"...`);

      const preferGroq = (workerId % 2 === 0);
      const translated = await callAI(ACADEMIC_SYSTEM_PROMPT, secText, 8192, preferGroq);

      fs.writeFileSync(secCacheFile, JSON.stringify({ ch: chNumber, sec: sIdx, text: translated }, null, 2), 'utf-8');
      translatedSections[sIdx] = translated;
    }
  }

  const workers = [];
  for (let w = 1; w <= CONCURRENCY; w++) {
    workers.push(worker(w));
  }
  await Promise.all(workers);

  const fullMarkdownEn = translatedSections.join('\n\n');
  const words = fullMarkdownEn.split(/\s+/).filter(Boolean).length;
  const enTitle = ENGLISH_CHAPTER_TITLES[chNumber - 1] || srcData.chapterTitle;

  const result = {
    chapterNumber: chNumber,
    chapterTitle: enTitle,
    contentMarkdown: fullMarkdownEn,
    wordCount: words,
    translatedAt: new Date().toISOString()
  };

  fs.writeFileSync(tgtFilePath, JSON.stringify(result, null, 2), 'utf-8');
  console.log(`✅ Chapter ${chNumber} DONE! (${words} words)`);
  return result;
}

async function main() {
  const tStart = Date.now();
  console.log('==============================================================================');
  console.log('🚀 TURBO ENGLISH TRANSLATION ENGINE (4x CONCURRENT WORKERS)');
  console.log('==============================================================================');

  const blueprint = await ensureBlueprint();

  const chapters = [];
  for (let ch = 1; ch <= 10; ch++) {
    const chData = await translateChapter(ch);
    if (chData) chapters.push(chData);
  }

  const bundlePath = path.join(TGT_DIR, 'book_bundle.json');
  fs.writeFileSync(bundlePath, JSON.stringify({ blueprint, chapters }, null, 2), 'utf-8');

  console.log('\n📐 Compiling Amazon KDP 7" × 10" Print-Ready PDF...');
  execSync(`python3 /root/journal/scripts/compile-kdp-typst.py`, { stdio: 'inherit' });

  const elapsedMin = ((Date.now() - tStart) / 60000).toFixed(1);
  console.log(`\n🎉 ALL 10 CHAPTERS TRANSLATED & COMPILED IN ${elapsedMin} MINUTES!`);
}

main().catch(err => {
  console.error('❌ Fatal error:', err);
  process.exit(1);
});
