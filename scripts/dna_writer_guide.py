#!/usr/bin/env python3
"""
DNA Writer Guide & Validator Module
Enforces Author Ilham Pradani Writing DNA across all generators.
Source: DNA_WRITING_STYLE_ILHAM_PRADANI.md
"""

import re

# Banned robotic AI cliché words / transitions
BANNED_AI_CLICHES = [
    r"\bselain itu\b",
    r"\bpenting untuk dicatat bahwa\b",
    r"\bsecara garis besar\b",
    r"\bsecara komprehensif\b",
    r"\bhal ini menunjukkan bahwa\b",
    r"\bdi sisi lain\b",
    r"\bdalam era globalisasi saat ini\b",
    r"\bdapat dipahami bahwa terdapat urgensi\b",
    r"\bsebagai kesimpulan, dapat disimpulkan bahwa\b",
    r"\bsecara keseluruhan\b",
    r"\btentunya kita perlu menyadari\b"
]

def get_dna_system_prompt() -> str:
    """Returns the prompt instruction to inject into LLMs (Groq, Gemini, etc.)"""
    return (
        "GAYA PENULISAN WAJIB (DNA ILHAM PRADANI - HUMAN DYNAMIC & CONTENT-DRIVEN):\n"
        "1. KEBEBASAN DINAMIS & KEDALAMAN ORGANIK (ZERO ARTIFICIAL RESTRICTIONS): "
        "DILARANG MEMBATASI ATAU MEMATOK PANJANG PARAGRAF SECARA KAKU. Setiap paragraf harus murni mengalir "
        "sesuai kebutuhan pembahasan substansi. Kembangkan pembahasan secara leluasa, mendalam, dan panjang bila topik "
        "memerlukan telaah doktriner/empiris komprehensif, dan gunakan paragraf pendek menusuk saat menegaskan prinsip atau premis inti.\n"
        "2. KEACAKAN ALAMI (ORGANIC DYNAMIC RANDOMNESS): Biarkan panjang paragraf bervariasi secara alami dan organik "
        "mengikuti intensitas dialektika pemikiran (narasi studi kasus bisa panjang dan hidup, diselingi paragraf penegasan singkat, "
        "lalu poin-poin operasional teknis 1, 2, 3, 4).\n"
        "3. PRAGMATIS-SOLUTIF & MENGINJAK BUMI: Awali pembahasan dari KONTRAKDIKSI NYATA DI LAPANGAN "
        "(studi kasus faktual e-commerce Indonesia, sengketa kerugian nyata konsumen, klausula eksonerasi platform).\n"
        "4. KALIMAT MAJEMUK MENGALIR: Gunakan kata hubung alami bahasa Indonesia: 'di mana...', 'hal ini penting untuk...', "
        "'namun kita memiliki masalah yang cukup penting di sini...', 'oleh karena itu saya berinisiatif...'.\n"
        "5. ZERO TOLERANCE KATA KLISE AI: DILARANG KERAS menggunakan 'Selain itu', 'Penting untuk dicatat bahwa', "
        "'Secara komprehensif', 'Hal ini menunjukkan bahwa', 'Di sisi lain'.\n"
        "6. SOLUSI BERTAHAP (SKEMA BERJENJANG / MVP): Uraikan tahapan operasional bernomor (1, 2, 3, 4) dengan rincian praktis "
        "yang bisa langsung dieksekusi tanpa menunggu revisi undang-undang.\n"
        "7. VISUALISASI FORMAL: Sertakan Bagan 1 Alur Logika Resmi dan Tabel 1 Matriks Perbandingan."
    )

def audit_text_dna(text: str) -> dict:
    """
    Audits a text against banned AI clichés and checks burstiness.
    Does NOT restrict maximum paragraph length, ensuring true dynamic human freedom.
    """
    lower_text = text.lower()
    violations = []
    
    for pat in BANNED_AI_CLICHES:
        matches = re.findall(pat, lower_text)
        if matches:
            violations.append(f"Ditemukan {len(matches)}x kata klise AI: '{matches[0]}'")
            
    # Measure sentence length variation (Burstiness)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 5]
    if sentences:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5
    else:
        avg_len, std_dev = 0, 0
        
    score = 100.0 - (len(violations) * 15.0)
    if std_dev < 5.0: # Low burstiness (monotonous sentence length)
        score -= 20.0
        violations.append(f"Variasi kalimat terlalu seragam/monoton (Std Dev: {std_dev:.1f} kata). Perlu lebih acak.")
        
    passed = len(violations) == 0 and score >= 85.0
    return {
        "passed": passed,
        "score": max(0.0, score),
        "sentence_count": len(sentences),
        "avg_words_per_sentence": round(avg_len, 1),
        "burstiness_std_dev": round(std_dev, 1),
        "violations": violations
    }

if __name__ == "__main__":
    prompt = get_dna_system_prompt()
    print("DNA Prompt Guide:\n", prompt)
