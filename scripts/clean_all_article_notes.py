#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - Database & File Cleaner for Revision Notes & Reviewer Comments
- Cleans articles in Cloudflare D1 (IDs 4, 5, 7, 8) by stripping appended revision notes / reviewer comments
- Cleans src/data/versions_v1.json
- Verifies that all articles in D1 and v1 JSON are 100% free of reviewer responses and meta-prompts
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error

ENV_PATH = "/root/chainasiaweb/.env"
ENV_VARS = {}
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                ENV_VARS[k.strip()] = v.strip().strip('"').strip("'")

CF_ACCOUNT_ID = ENV_VARS.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "cd95efc74562ac2f0c0d9759d06d7d89")
CF_API_TOKEN = ENV_VARS.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN", "")
D1_DATABASE_ID = "d2d582a9-e0c3-4ea4-9dce-4881c9cfb167"

def execute_d1(sql, params=[]):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{D1_DATABASE_ID}/query"
    body = {"sql": sql}
    if params:
        body["params"] = params
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        if res.get("success"):
            return res.get("result", [{}])[0].get("results", [])
        else:
            raise Exception(f"D1 Error: {res.get('errors')}")

def clean_d1_articles():
    print("🧹 [1/3] Membersihkan naskah artikel di Cloudflare D1 Database...")
    rows = execute_d1("SELECT id, title, content FROM articles ORDER BY id")
    
    clean_targets = {
        4: "## 3.4 Synthesis of Reconciliation",
        5: "# 3.4 Synthesis of Reconciliation",
        7: "## 3.4 Synthesis of Reconciliation",
        8: "## 6. Revision Notes"
    }

    for r in rows:
        cid = r["id"]
        title = r["title"]
        content = r["content"] or ""
        
        if cid in clean_targets:
            marker = clean_targets[cid]
            idx = content.find(marker)
            if idx != -1:
                cleaned = content[:idx].rstrip()
                # Hapus disclaimer fiktif jika ada
                cleaned = re.sub(r"\*Note: All thermal, technical.*?\*\s*$", "", cleaned, flags=re.DOTALL).strip()
                # Hapus sisa garis pemisah di akhir
                cleaned = re.sub(r"(?:---|___|\*\*\*)\s*$", "", cleaned).strip()
                
                print(f"   ✂️ Article #{cid}: dipotong di '{marker}' (dari {len(content)} -> {len(cleaned)} karakter)")
                execute_d1("UPDATE articles SET content = ? WHERE id = ?", [cleaned, cid])
            else:
                print(f"   ⚠️ Article #{cid}: marker '{marker}' tidak ditemukan, melewati.")
        else:
            print(f"   ✅ Article #{cid} ({title[:35]}...): sudah bersih ({len(content)} karakter).")

def clean_versions_v1_json():
    print("\n🧹 [2/3] Membersihkan arsip naskah Versi 1 di src/data/versions_v1.json...")
    v1_path = "/root/chainasiaweb/src/data/versions_v1.json"
    with open(v1_path, "r", encoding="utf-8") as f:
        v1_data = json.load(f)

    for slug, data in v1_data.items():
        body = data.get("body", "")
        old_len = len(body)
        
        # Potong dari deklarasi integritas atau catatan revisi
        cut_markers = [
            "## 3.4 Sintesis",
            "# 3.4 Sintesis",
            "7. Contractual Revisions",
            "DEKLARASI INTEGRITAS & PREPRINT",
            "Deklarasi Integritas & Preprint"
        ]
        
        cut_idx = -1
        for m in cut_markers:
            pos = body.find(m)
            if pos != -1 and (cut_idx == -1 or pos < cut_idx):
                cut_idx = pos
                
        if cut_idx != -1:
            cleaned_body = body[:cut_idx].rstrip()
            cleaned_body = re.sub(r"(?:---|___|\*\*\*)\s*$", "", cleaned_body).strip()
            data["body"] = cleaned_body
            print(f"   ✂️ V1 Slug '{slug[:35]}...': dipotong dari {old_len} -> {len(cleaned_body)} karakter")
        else:
            print(f"   ✅ V1 Slug '{slug[:35]}...': bersih ({old_len} karakter)")

    with open(v1_path, "w", encoding="utf-8") as f:
        json.dump(v1_data, f, indent=2, ensure_ascii=False)
    print("   💾 Berhasil menyimpan src/data/versions_v1.json yang bersih.")

def audit_all_clean():
    print("\n🔍 [3/3] Menjalankan Audit Kepatuhan Akhir...")
    rows = execute_d1("SELECT id, title, content FROM articles ORDER BY id")
    leak_terms = ["revision notes", "catatan revisi", "reviewer 1", "reviewer 2", "sintesis rekonsiliasi", "penajaman doktrinal", "universitas terbuka"]
    
    all_clean = True
    for r in rows:
        cid = r["id"]
        c = (r["content"] or "").lower()
        leaks = [t for t in leak_terms if t in c]
        if leaks:
            print(f"   ❌ D1 Article #{cid} MASIH MENGANDUNG: {leaks}")
            all_clean = False
        else:
            print(f"   ✅ D1 Article #{cid}: 100% BEBAS DARI BOCORAN CATATAN REVISI")

    with open("/root/chainasiaweb/src/data/versions_v1.json", "r", encoding="utf-8") as f:
        v1_data = json.load(f)
    for slug, d in v1_data.items():
        b = (d.get("body", "")).lower()
        leaks = [t for t in leak_terms if t in b]
        if leaks:
            print(f"   ❌ V1 '{slug[:30]}' MASIH MENGANDUNG: {leaks}")
            all_clean = False
        else:
            print(f"   ✅ V1 '{slug[:30]}': 100% BEBAS DARI BOCORAN CATATAN REVISI")

    if all_clean:
        print("\n🎉 AUDIT KELULUSAN 100%: Seluruh naskah publikasi telah bersih total!")
    else:
        print("\n⚠️ Perhatian: Masih ditemukan catatan yang perlu ditinjau.")

if __name__ == "__main__":
    clean_d1_articles()
    clean_versions_v1_json()
    audit_all_clean()

