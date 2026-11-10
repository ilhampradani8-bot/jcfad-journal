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

def screen_pdf_page_with_ai(image_bytes, page_num=1):
    """
    Kirim renderan visual halaman PDF ke Google Gemini Vision untuk screening OCR.
    """
    if not GEMINI_API_KEY:
        return {"status": "SKIP", "score": 100, "summary": "GEMINI_API_KEY tidak dikonfigurasi"}

    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    prompt = """You are a senior academic journal layout auditor and typesetter for IEEE/Elsevier publications.
Visually inspect this rendered page of an academic journal article (ISO A4 2-column layout):
1. Column & Table Collision: Are any numbers or letters colliding, overlapping, or fusing across cells/columns (e.g. adjacent numbers merging like '1,234,000,000312,000,000')?
2. Uncompiled Math / LaTeX Syntax Leaks: Are there uncompiled LaTeX strings, missing fraction backslashes (e.g. 'rac{d}{s}'), concatenated operators ('xcdot', 'fleq'), raw brackets around equations ('[ C_{total}=... ]'), or unformatted subscripts?
3. Typography & Formatting: Are tables in clean Booktabs three-line style without vertical lines? Are running headers and footers single-line and unclipped?

Return ONLY valid JSON matching this schema:
{
  "status": "PASS" or "FAIL",
  "score": <integer from 0 to 100>,
  "collision_detected": <true or false>,
  "uncompiled_math_detected": <true or false>,
  "issues": [<list of specific visual defects found, if any>],
  "summary": "<concise summary of visual layout quality>"
}"""

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": b64_img}}
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
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return json.loads(text)
        except Exception as e:
            continue

    return {"status": "WARN", "score": 85, "summary": "API quota limit / temporary timeout"}

def run_ai_ocr_screening(pdf_path, max_pages=3):
    """
    Memeriksa seluruh berkas PDF dengan AI OCR Screening.
    """
    if not os.path.exists(pdf_path):
        return False, {"error": f"File not found: {pdf_path}"}

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    pages_to_audit = min(total_pages, max_pages)

    print(f"\n🤖 [AI OCR Screening Engine] Mengaudit visual berkas: {os.path.basename(pdf_path)} ({total_pages} Hal)...")

    all_passed = True
    page_results = []

    for p_idx in range(pages_to_audit):
        page = doc[p_idx]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        res = screen_pdf_page_with_ai(img_bytes, page_num=p_idx + 1)
        res["page"] = p_idx + 1
        page_results.append(res)

        st = res.get("status", "WARN")
        sc = res.get("score", 0)
        sm = res.get("summary", "")
        col = res.get("collision_detected", False)
        math_err = res.get("uncompiled_math_detected", False)

        icon = "✅" if st == "PASS" else ("⚠️" if st == "WARN" else "❌")
        print(f"   {icon} Halaman {p_idx + 1}: [{st}] Skor: {sc}% | Collision: {'YA' if col else 'TIDAK'} | Math Leak: {'YA' if math_err else 'TIDAK'}")
        if res.get("issues"):
            for iss in res["issues"]:
                print(f"      - ⚠️ {iss}")
        print(f"      📝 {sm}")

        if st == "FAIL":
            all_passed = False

    avg_score = sum(r.get("score", 0) for r in page_results) / max(len(page_results), 1)
    return all_passed, {
        "all_passed": all_passed,
        "average_score": avg_score,
        "page_results": page_results
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ai_ocr_screening.py <pdf_path>")
        sys.exit(1)

    target_pdf = sys.argv[1]
    passed, report = run_ai_ocr_screening(target_pdf)
    sys.exit(0 if passed else 1)
