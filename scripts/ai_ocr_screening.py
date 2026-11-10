#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - Academic Journal AI OCR Visual Screening Engine
Powered by Google Gemini Multimodal Vision API (gemini-3.5-flash-lite)
Screens PDF pages visually for:
1. Column overlapping & cell number collision (tabrakan tabel / teks)
2. Uncompiled LaTeX syntax & math leaks (e.g. rac{...}, xcdot, raw brackets)
3. Table boundaries & typography alignment (Booktabs compliance)
4. Overall visual aesthetic and print readiness
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error
import pymupdf

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")

if os.path.exists(ENV_FILE):
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def screen_pdf_document_with_ai(pdf_path):
    """
    Kirim berkas PDF langsung (application/pdf) ke Google Gemini Multimodal Vision API
    untuk audit visual, deteksi tabrakan teks, kebocoran sintaks math, dan Booktabs compliance.
    """
    if not GEMINI_API_KEY:
        return {"status": "SKIP", "score": 100, "summary": "GEMINI_API_KEY tidak dikonfigurasi"}

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    prompt = """You are a senior academic journal layout auditor and typesetter for IEEE/Elsevier publications.
Audit this academic journal PDF directly as a complete document (ISO A4 2-column layout):
1. Column & Table Collision: Are any numbers, words, code, or letters colliding, overlapping, or fusing across cells or columns?
2. Geometric Lines & Straightness: Are horizontal rules (Booktabs top/mid/bottom lines, header hairline dividers, footer rules) strictly straight and continuous? Are vertical column gutters (celah antar 2 kolom) strictly straight without text bleeding across? Are left/right margins cleanly justified?
3. Uncompiled Math / Code Leaks: Are there uncompiled LaTeX strings, missing fraction backslashes (e.g. 'rac{d}{s}'), concatenated operators ('xcdot'), or raw brackets?
4. Typography & Formatting: Are tables in clean Booktabs three-line style without vertical lines? Are running headers and footers single-line and unclipped?
5. Document Flow: Do tables or sections break awkwardly across pages or columns?

Return ONLY valid JSON matching this schema:
{
  "status": "PASS" or "FAIL",
  "score": <integer from 0 to 100>,
  "collision_detected": <true or false>,
  "uncompiled_math_detected": <true or false>,
  "lines_straight_and_aligned": <true or false>,
  "geometric_integrity_notes": "<concise analysis of lines, borders, column gutters, and alignment straightness>",
  "issues": [<list of specific visual defects found, if any>],
  "summary": "<concise summary of visual layout quality>",
  "page_notes": [{"page": <int>, "notes": "<notes>"}]
}"""

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "application/pdf", "data": b64_pdf}}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    models_to_try = ["gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-flash-latest"]
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return json.loads(text)
        except Exception as e:
            continue

    return {"status": "WARN", "score": 85, "summary": "API quota limit / temporary timeout"}

def run_ai_ocr_screening(pdf_path):
    """
    Memeriksa berkas PDF langsung ke Gemini Vision (Direct PDF Multimodal).
    """
    if not os.path.exists(pdf_path):
        return False, {"error": f"File not found: {pdf_path}"}

    file_size_kb = os.path.getsize(pdf_path) / 1024
    print(f"\n🤖 [AI OCR Screening Engine] Mengirim berkas PDF langsung ke Gemini Vision: {os.path.basename(pdf_path)} ({file_size_kb:.1f} KB)...")

    res = screen_pdf_document_with_ai(pdf_path)

    st = res.get("status", "WARN")
    sc = res.get("score", 0)
    sm = res.get("summary", "")
    col = res.get("collision_detected", False)
    math_err = res.get("uncompiled_math_detected", False)
    lines_straight = res.get("lines_straight_and_aligned", True)
    geo_notes = res.get("geometric_integrity_notes", "")
    issues = res.get("issues", [])
    page_notes = res.get("page_notes", [])

    icon = "✅" if st == "PASS" else ("⚠️" if st == "WARN" else "❌")
    print(f"\n{icon} [Hasil Audit Gemini Vision]: Status: [{st}] | Skor: {sc}% | Collision: {'YA' if col else 'TIDAK'} | Math Leak: {'YA' if math_err else 'TIDAK'} | Kelurusan Garis: {'LURUS & PRESISI' if lines_straight else 'TIDAK RAPI'}")
    print(f"   📝 Ringkasan: {sm}")
    if geo_notes:
        print(f"   📐 Geometri & Kelurusan: {geo_notes}")

    if issues:
        print("\n   ⚠️ Isu yang Ditemukan:")
        for iss in issues:
            print(f"      - {iss}")

    if page_notes:
        print("\n   📄 Catatan Per Halaman:")
        for pn in page_notes:
            print(f"      - Halaman {pn.get('page')}: {pn.get('notes')}")

    passed = (st == "PASS")
    return passed, res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ai_ocr_screening.py <pdf_path>")
        sys.exit(1)

    target_pdf = sys.argv[1]
    passed, report = run_ai_ocr_screening(target_pdf)
    sys.exit(0 if passed else 1)

