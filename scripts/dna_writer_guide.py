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
        "GAYA PENULISAN WAJIB (DNA ILHAM PRADANI - HUMAN AUTHENTIC):\n"
        "1. Tulis dengan gaya bertutur intelektual pragmatis-solutif khas Ilham Pradani (lugas, berani, menginjak bumi).\n"
        "2. Awali pembahasan dari KONTRAKDIKSI NYATA DI LAPANGAN (studi kasus faktual e-commerce Indonesia, sengketa kerugian nyata, klausula eksonerasi).\n"
        "3. Gunakan pola kalimat majemuk mengalir alami: 'di mana...', 'hal ini penting untuk...', 'namun kita memiliki masalah yang cukup penting di sini...', 'oleh karena itu saya berinisiatif...'.\n"
        "4. Terapkan variasi panjang kalimat yang tinggi (High Burstiness): padukan kalimat pendek tajam dengan elaborasi logis panjang.\n"
        "5. DILARANG KERAS menggunakan kata transisi klise AI: 'Selain itu', 'Penting untuk dicatat bahwa', 'Secara komprehensif', 'Hal ini menunjukkan bahwa', 'Di sisi lain'.\n"
        "6. Rancang solusi secara bertahap (skema berjenjang/MVP): Tahap 1 (Pintu Masuk Pembuktian Terbalik), Tahap 2 (Tanggung Jawab Mutlak Berjenjang Platform & Vendor).\n"
        "7. Sajikan visualisasi konkret (Bagan 1 Diagram Alur Resmi dan Tabel 1 Matriks Perbandingan Sistem)."
    )

def audit_text_dna(text: str) -> dict:
    """Audits a text against banned AI clichés and checks burstiness."""
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
    if std_dev < 5.0: # Low burstiness (too uniform)
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
    import sys
    test_text = (
        "Perkembangan teknologi transaksi elektronik saat ini sudah bergerak sangat jauh melampaui "
        "apa yang dibayangkan oleh para perancang KUHPerdata. Namun kita memiliki masalah hukum yang sangat "
        "penting di sini, karena hukum perdata Indonesia belum siap menghadapi situasi ketika mesin cerdas "
        "tersebut membuat keputusan yang keliru. Oleh karena itu saya berinisiatif merumuskan skema baru."
    )
    res = audit_text_dna(test_text)
    print("Test Audit Result:", res)
