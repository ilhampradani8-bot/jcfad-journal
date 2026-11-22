/**
 * scripts/dna-writer-guide.mjs
 * ============================================================================
 * MODUL PANDUAN DNA PENULIS ILHAM PRADANI (NODE.JS / ESM)
 * Standar Penulisan Humanis Dinamis, Asimetri Paragraf Alami, & Anti-Klise AI
 * Sumber Referensi: DNA_WRITING_STYLE_ILHAM_PRADANI.md
 * ============================================================================
 */

export const BANNED_AI_CLICHES = [
  { pattern: /\bselain itu\b/gi, replacement: 'di samping hal tersebut' },
  { pattern: /\bpenting untuk dicatat bahwa\b/gi, replacement: 'perlu disadari bahwa' },
  { pattern: /\bsecara garis besar\b/gi, replacement: 'pada tataran praktis' },
  { pattern: /\bsecara komprehensif\b/gi, replacement: 'secara mendalam dan menyeluruh' },
  { pattern: /\bhal ini menunjukkan bahwa\b/gi, replacement: 'fakta ini menegaskan bahwa' },
  { pattern: /\bdi sisi lain\b/gi, replacement: 'sementara itu' },
  { pattern: /\bdalam era globalisasi saat ini\b/gi, replacement: 'dalam dinamika pasar saat ini' },
  { pattern: /\bdapat dipahami bahwa terdapat urgensi\b/gi, replacement: 'urgensi nyata terlihat dari' },
  { pattern: /\bsebagai kesimpulan, dapat disimpulkan bahwa\b/gi, replacement: 'pada akhirnya' },
  { pattern: /\bsecara keseluruhan\b/gi, replacement: 'secara praktis' },
  { pattern: /\btentunya kita perlu menyadari\b/gi, replacement: 'kita perlu melihat bahwa' },
  { pattern: /\btransformasi lanskap\b/gi, replacement: 'perkembangan praktik' },
  { pattern: /\bmenjadi sangat krusial\b/gi, replacement: 'menjadi sangat menentukan' },
  { pattern: /\bdi satu sisi\b/gi, replacement: 'pada satu aspek' }
];

export const DNA_SYSTEM_PROMPT = `
================================================================================
ATURAN MUTLAK GAYA PENULISAN (DNA ILHAM PRADANI - HUMAN ASYMMETRIC & ORGANIC):
================================================================================
Naskah WAJIB ditulis dengan meniru gaya berpikir dan karakter tulisan tangan asli Ilham Pradani (berdasarkan esai Sekpol 2026). DILARANG KERAS menggunakan pola penulisan generik robotik AI!

1. PRINSIP NOL PEMBATASAN ARTIFISIAL (ZERO ARTIFICIAL CONSTRAINTS):
   DILARANG MEMBATASI ATAU MEMATOK PANJANG PARAGRAF SECARA KAKU/SERAGAM. Setiap paragraf wajib mengalir murni secara dinamis dan organik: bebas memanjang dan mendalam saat membedah doktrin, formulasi matematika, atau kasus lapangan substantif, dan bebas pendek menusuk saat menegaskan prinsip.

2. ASIMETRI & KEACAKAN PARAGRAF ALAMI (DYNAMIC PARAGRAPH BURSTINESS):
   Panjang paragraf WAJIB acak dan bervariasi secara ekstrem (Anti-Monotoni AI):
   - Paragraf Pendek Menusuk (15–35 kata): Untuk melontarkan pertanyaan provokatif, premis inti, atau prinsip kausalitas hukum/ekonomi.
   - Paragraf Sedang Terfokus (45–80 kata): Untuk menyambung transisi logika dan menghubungkan premis dengan data empiris.
   - Paragraf Panjang Mendalam (100–190 kata): Untuk analisis doktrinal KUHPerdata, penurunan rumus matematika optimasi, atau deskripsi kasus lapangan yang kaya detail.

3. PENDEKATAN PRAGMATIS-SOLUTIF & MENGINJAK BUMI:
   Awali pemikiran dari KONTRAKSI DAN KERUGIAN NYATA DI LAPANGAN INDONESIA (misalnya: SPBN macet di Krui Pesisir Barat, rantai pasok ikan busuk, tengkulak menekan harga nelayan, pembatalan sepihak pesanan marketplace, atau klausula eksonerasi platform). Jangan berteori di awang-awang tanpa kaitan empiris langsung.

4. GAYA KALIMAT MAJEMUK MENGALIR ALAMI:
   Gunakan struktur kalimat hidup yang mengalir wajar layaknya pemikir lapangan: "di mana...", "hal ini penting untuk...", "namun kita memiliki masalah yang cukup penting di sini...", "oleh karena itu saya berinisiatif...".

5. ZERO TOLERANCE KATA KLISE AI (100% BANNED):
   DILARANG KERAS memuat kata/frasa transisi klise khas AI seperti:
   - "Selain itu" (Ganti dengan: di samping hal tersebut, sementara itu, atau langsung sambung kalimat)
   - "Penting untuk dicatat bahwa"
   - "Secara komprehensif"
   - "Di satu sisi ... di sisi lain"
   - "Transformasi lanskap"
   - "Menjadi sangat krusial"
   - "Secara garis besar"

6. SOLUSI BERTAHAP & TERUKUR (SKEMA BERJENJANG / MVP):
   Tawarkan skema operasional taktis bertahap (1, 2, 3, 4) yang membumi, dapat dieksekusi langsung tanpa menunggu perombakan birokrasi raksasa.

7. KEWAJIBAN VISUALISASI:
   Naskah wajib dilengkapi minimal Tabel 1 Format Tiga Garis (Three-Line Table Booktabs) dan bagan alur konseptual yang kokoh.
================================================================================
`;

/**
 * Memeriksa kepatuhan DNA dan burstiness teks
 */
export function auditTextDna(text) {
  if (!text || typeof text !== 'string') {
    return { passed: false, score: 0, violations: ['Teks kosong'] };
  }

  const lower = text.toLowerCase();
  const violations = [];

  for (const item of BANNED_AI_CLICHES) {
    const matches = lower.match(item.pattern);
    if (matches && matches.length > 0) {
      violations.push(`Ditemukan ${matches.length}x kata klise AI: '${matches[0]}'`);
    }
  }

  // Hitung variasi panjang paragraf (Asymmetry test)
  const paragraphs = text.split(/\n\s*\n/).map(p => p.trim()).filter(p => p.length > 20 && !p.startsWith('#') && !p.startsWith('|') && !p.startsWith('$'));
  let paragraphStdDev = 0;
  let minWords = 0;
  let maxWords = 0;

  if (paragraphs.length >= 3) {
    const wordCounts = paragraphs.map(p => p.split(/\s+/).length);
    minWords = Math.min(...wordCounts);
    maxWords = Math.max(...wordCounts);
    const avgWords = wordCounts.reduce((a, b) => a + b, 0) / wordCounts.length;
    const variance = wordCounts.reduce((acc, val) => acc + Math.pow(val - avgWords, 2), 0) / wordCounts.length;
    paragraphStdDev = Math.sqrt(variance);

    if (paragraphStdDev < 15.0) {
      violations.push(`Paragraf terlalu seragam (Std Dev: ${paragraphStdDev.toFixed(1)} kata). Wajib lebih asimetris dan acak (pendek vs panjang)!`);
    }
  }

  let score = 100.0 - (violations.length * 15.0);
  score = Math.max(0.0, score);
  const passed = violations.length === 0 && score >= 85.0;

  return {
    passed,
    score,
    paragraphCount: paragraphs.length,
    minParagraphWords: minWords,
    maxParagraphWords: maxWords,
    paragraphStdDev: parseFloat(paragraphStdDev.toFixed(1)),
    violations
  };
}

/**
 * Membersihkan kata-kata klise AI secara otomatis (Self-Healing Sanitizer)
 */
export function sanitizeDnaViolations(text) {
  if (!text || typeof text !== 'string') return text;
  let sanitized = text;

  for (const item of BANNED_AI_CLICHES) {
    sanitized = sanitized.replace(item.pattern, item.replacement);
  }

  return sanitized;
}
