#!/usr/bin/env python3
"""
Full Academic Audit Runner for All Published JCFAD Papers
Audits 100% of published articles in Cloudflare D1 & public/docs against IEEE/Elsevier standards.
"""

import os
import sys
import json
import urllib.request
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

import importlib.util

spec = importlib.util.spec_from_file_location("generate_paper_pdf", os.path.join(PROJECT_ROOT, "scripts/generate-paper-pdf.py"))
gen_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen_module)

build_article_pdf = gen_module.build_article_pdf
review_pdf = gen_module.review_pdf
DOCS_DIR = gen_module.DOCS_DIR

def run_audit_all():
    print("=" * 80)
    print("🔍 JCFAD JOURNAL - COMPREHENSIVE ACADEMIC AUDIT ENGINE FOR ALL PAPERS")
    print("=" * 80)

    # 1. Fetch all articles from D1
    req = urllib.request.Request(
        'https://api.chainasiaconnect.co.id/',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    articles = data.get('articles', [])
    print(f"📦 Terdeteksi {len(articles)} Naskah Ilmiah Resmi di Cloudflare D1.\n")

    results = []

    for idx, art in enumerate(articles, 1):
        slug = art.get('slug')
        title = art.get('title', 'Unknown')
        short_title = title[:45] + "..." if len(title) > 45 else title
        pdf_path = os.path.join(DOCS_DIR, f"{slug}.pdf")

        # If PDF doesn't exist, compile it first
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 25000:
            print(f"⚙️ [{idx}/{len(articles)}] Mengompilasi PDF baru: [{slug}]...")
            build_article_pdf(art, pdf_path)

        # Run review
        passed, checks, fail_keys = review_pdf(pdf_path, art, attempt=1)

        # If failed, trigger self-healing regeneration
        if not passed:
            print(f"⚠️ [{slug}] Membutuhkan perbaikan mandiri, mengaktifkan adaptive loop...")
            build_article_pdf(art, pdf_path, max_attempts=4)
            passed, checks, fail_keys = review_pdf(pdf_path, art, attempt=2)

        sz_kb = os.path.getsize(pdf_path) / 1024
        score = sum(1 for _, s, _ in checks if s == "PASS") / len(checks) * 100
        results.append({
            "idx": idx,
            "slug": slug,
            "title": short_title,
            "size_kb": f"{sz_kb:.1f} KB",
            "score": f"{score:.1f}%",
            "status": "PASS" if passed else "WARN/FAIL",
            "fails": fail_keys
        })

    # Summary Table
    print("\n" + "=" * 80)
    print("📊 RINGKASAN HASIL AUDIT KELAYAKAN SELURUH ARTIKEL JURNAL (JCFAD)")
    print("=" * 80)
    print(f"{'No':<3} | {'Skor':<7} | {'Status':<6} | {'Ukuran':<9} | {'Judul Naskah'}")
    print("-" * 80)
    
    total_passed = 0
    for r in results:
        status_icon = "✅" if r["status"] == "PASS" else "❌"
        if r["status"] == "PASS":
            total_passed += 1
        print(f"{r['idx']:<3} | {r['score']:<7} | {status_icon} {r['status']:<4} | {r['size_kb']:<9} | {r['title']}")

    print("=" * 80)
    pass_rate = (total_passed / len(results)) * 100
    print(f"🎯 Total Artikel: {len(results)} | Lulus Audit: {total_passed}/{len(results)} ({pass_rate:.1f}%)")
    print("=" * 80 + "\n")

    return total_passed == len(results)

if __name__ == "__main__":
    success = run_audit_all()
    sys.exit(0 if success else 1)
