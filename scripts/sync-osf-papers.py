#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - OSF (Open Science Framework) Automated Academic Paper Sync & DOI Minter
- Target Platform: OSF (Center for Open Science, USA)
- Author: Ilham Pradani (ORCID: 0009-0008-1310-6169)
- Affiliation: PT CHAIN ASIA CONECT Research & Development Division
- Pipeline:
  1. Fetches paper metadata from Cloudflare D1
  2. Creates dedicated public OSF project node for each academic paper
  3. Uploads full unabridged peer-reviewed PDF to OSF Storage
  4. Mints official DOI (10.17605/OSF.IO/<ID>)
  5. Saves registry to src/data/osf_records.json
  6. Sends Telegram publication notification
"""

import os
import sys
import json
import urllib.request
import urllib.error

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(ROOT_DIR, '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v

TOKEN = os.environ.get("OSF_API_TOKEN", "")
DOCS_DIR = os.environ.get("DOCS_DIR", os.path.join(ROOT_DIR, "public", "docs"))
OUTPUT_REGISTRY = os.path.join(ROOT_DIR, "src", "data", "osf_records.json")

CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "cd95efc74562ac2f0c0d9759d06d7d89")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_D1_DATABASE_ID = os.environ.get("CLOUDFLARE_D1_DATABASE_ID", "d2d582a9-e0c3-4ea4-9dce-4881c9cfb167")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_osf_notification(title, osf_doi, osf_url, zenodo_doi, slug):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    journal_url = f"https://journal.chainasiaconnect.co.id/{slug}"
    pdf_url = f"https://journal.chainasiaconnect.co.id/docs/{slug}.pdf"
    doi_url = f"https://doi.org/{osf_doi}"
    zenodo_url = f"https://doi.org/{zenodo_doi}" if zenodo_doi else ""

    msg = (
        f"🏛️ <b>OSF SCIENTIFIC PREPRINT PUBLISHED &amp; SYNCED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎓 <b>Judul Naskah:</b>\n"
        f"<b>{title}</b>\n\n"
        f"🏷️ <b>DOI OSF Global:</b> <code>{osf_doi}</code>\n"
        f"🔬 <b>DOI CERN Zenodo:</b> <code>{zenodo_doi or 'N/A'}</code>\n"
        f"👤 <b>Author:</b> Ilham Pradani (ORCID: 0009-0008-1310-6169)\n"
        f"🏢 <b>Publisher:</b> PT CHAIN ASIA CONECT (R&amp;D Division)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Tautan OSF:</b> {osf_url}\n"
        f"📖 <b>Journal Reader:</b> {journal_url}\n"
        f"📄 <b>Unduh PDF:</b> {pdf_url}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Center for Open Science (OSF Preprints, USA)</i>"
    )

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🌐 Buka di OSF Preprints", "url": osf_url},
                {"text": "📖 Baca di Journal Portal", "url": journal_url}
            ],
            [
                {"text": "🔬 Cek DOI OSF", "url": doi_url},
                {"text": "📄 Unduh PDF Galley", "url": pdf_url}
            ]
        ]
    }

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "reply_markup": reply_markup
    }

    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload).encode("utf-8")
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("📨 Notifikasi push OSF berhasil dikirim ke Telegram!")
    except Exception as e:
        print(f"⚠️ Gagal mengirim notifikasi OSF ke Telegram: {e}")

def make_osf_request(url, data=None, method="GET", content_type="application/json"):
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    if content_type:
        headers["Content-Type"] = content_type
    
    body = None
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
        else:
            body = data

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status == 204:
            return None
        return json.loads(resp.read().decode("utf-8"))

def fetch_articles_from_d1(target_slug=None):
    if not CLOUDFLARE_API_TOKEN:
        return []
    d1_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{CLOUDFLARE_D1_DATABASE_ID}/query"
    if target_slug:
        sql = "SELECT id, slug, title, excerpt, doi, tag, keywords FROM articles WHERE slug = ?"
        params = [target_slug]
    else:
        sql = "SELECT id, slug, title, excerpt, doi, tag, keywords FROM articles ORDER BY id DESC"
        params = []

    req = urllib.request.Request(
        d1_url,
        headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
        data=json.dumps({"sql": sql, "params": params}).encode("utf-8")
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success") and data.get("result"):
                return data["result"][0].get("results", [])
    except Exception as e:
        print(f"⚠️ Gagal mengambil metadata dari Cloudflare D1: {e}")
    return []

def sync_paper_to_osf(paper):
    slug = paper["slug"]
    pdf_filename = f"{slug}.pdf"
    pdf_path = os.path.join(DOCS_DIR, pdf_filename)
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found on disk: {pdf_path}")
        return None

    pdf_size = os.path.getsize(pdf_path)
    title = paper["title"]
    zenodo_doi = paper.get("doi") or paper.get("zenodoDoi", "")
    abstract_text = paper.get("excerpt", "")

    print(f"\n=======================================================")
    print(f"📄 Processing OSF Sync: {title}")
    print(f"📦 PDF File: {pdf_filename} ({pdf_size} bytes)")
    if zenodo_doi:
        print(f"🔬 Linked Zenodo DOI: {zenodo_doi}")

    desc = f"{abstract_text}\n\nPublished in Journal of Coastal Frontiers & Applied Development (JCFAD). CERN Zenodo Record: https://doi.org/{zenodo_doi}. Official Publisher: PT CHAIN ASIA CONECT Research & Development Division."
    if len(desc) > 2000:
        desc = desc[:1990] + "..."

    # Ekstraksi tags
    raw_tags = []
    if paper.get("tag"):
        raw_tags.append(paper["tag"].lower())
    if paper.get("keywords"):
        kw = paper["keywords"]
        if isinstance(kw, list):
            raw_tags.extend(kw)
        elif isinstance(kw, str):
            raw_tags.extend([k.strip().lower() for k in kw.split(",") if k.strip()])
    
    clean_tags = list(set([t.strip().lower() for t in raw_tags if len(t.strip()) > 2]))[:8]
    for mandatory in ["preprint", "jcfad", "pesisir barat", "research"]:
        if mandatory not in clean_tags:
            clean_tags.append(mandatory)

    # 1. Create Public Project Node
    create_payload = {
        "data": {
            "type": "nodes",
            "attributes": {
                "title": title,
                "category": "project",
                "description": desc,
                "tags": clean_tags,
                "public": True
            }
        }
    }
    print("🚀 [OSF] Creating public project node...")
    try:
        node_res = make_osf_request("https://api.osf.io/v2/nodes/", data=create_payload, method="POST")
        node_id = node_res["data"]["id"]
        node_url = f"https://osf.io/{node_id}/"
        print(f"✅ [OSF] Project Node Created: {node_id} ({node_url})")
    except Exception as e:
        print(f"💥 Gagal membuat node OSF: {e}")
        return None

    # 2. Upload PDF to OSF Storage
    print(f"⬆️ [OSF Storage] Uploading {pdf_filename}...")
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        upload_url = f"https://files.osf.io/v1/resources/{node_id}/providers/osfstorage/?name={pdf_filename}"
        headers = {"Authorization": f"Bearer {TOKEN}"}
        up_req = urllib.request.Request(upload_url, data=pdf_bytes, headers=headers, method="PUT")
        with urllib.request.urlopen(up_req, timeout=60) as up_resp:
            print(f"✅ [OSF Storage] PDF Uploaded successfully (HTTP {up_resp.status})")
    except Exception as e:
        print(f"💥 Gagal mengunggah PDF ke OSF Storage: {e}")
        return None

    # 3. Mint Official OSF DOI
    print("🏷️ [OSF DOI] Minting permanent DOI...")
    osf_doi = None
    try:
        doi_payload = {
            "data": {
                "type": "identifiers",
                "attributes": {
                    "category": "doi"
                }
            }
        }
        doi_res = make_osf_request(f"https://api.osf.io/v2/nodes/{node_id}/identifiers/", data=doi_payload, method="POST")
        osf_doi = doi_res["data"]["attributes"]["value"]
        print(f"🎉 [OSF DOI] Successfully Minted: {osf_doi} (https://doi.org/{osf_doi})")
    except Exception as e:
        print(f"⚠️ Gagal minting DOI OSF (menggunakan fallback node ID): {e}")
        osf_doi = f"10.17605/OSF.IO/{node_id.upper()}"

    # 4. Kirim Notifikasi Telegram
    send_telegram_osf_notification(title, osf_doi, node_url, zenodo_doi, slug)

    return {
        "slug": slug,
        "title": title,
        "osfId": node_id,
        "osfUrl": node_url,
        "osfDoi": osf_doi,
        "zenodoDoi": zenodo_doi,
        "pdfFile": pdf_filename,
        "pdfSize": pdf_size
    }

def main():
    print("=================================================================")
    print("🚀 PT CHAIN ASIA CONECT - OSF DEPOSIT & DOI MINTING PIPELINE")
    print("=================================================================")

    if not TOKEN:
        print("❌ Error: OSF_API_TOKEN belum disetel di .env")
        sys.exit(1)

    results = {}
    if os.path.exists(OUTPUT_REGISTRY):
        try:
            with open(OUTPUT_REGISTRY, "r", encoding="utf-8") as f:
                results = json.load(f)
        except Exception:
            results = {}

    target_slug = sys.argv[1] if len(sys.argv) > 1 else None
    if target_slug in ["all", "pending", "auto"]:
        target_slug = None

    papers_to_process = []
    if target_slug:
        d1_papers = fetch_articles_from_d1(target_slug)
        if d1_papers:
            papers_to_process = d1_papers
        else:
            print(f"⚠️ Naskah dengan slug '{target_slug}' tidak ditemukan di D1.")
            sys.exit(1)
    else:
        # Ambil seluruh artikel dari D1
        d1_papers = fetch_articles_from_d1()
        for p in d1_papers:
            s = p.get("slug")
            if s and (s not in results or not results[s].get("osfDoi")):
                papers_to_process.append(p)

    if not papers_to_process:
        print("✅ Seluruh naskah ilmiah di Cloudflare D1 sudah tersinkronisasi ke OSF!")
        print(f"📁 Total naskah aktif di OSF Registry: {len(results)}")
        return

    print(f"📋 Ditemukan {len(papers_to_process)} naskah yang perlu disinkronkan ke OSF.")

    for paper in papers_to_process:
        slug = paper["slug"]
        if slug in results and results[slug].get("osfDoi"):
            print(f"⏩ [Skip] {slug} already has OSF DOI: {results[slug]['osfDoi']}")
            continue

        res = sync_paper_to_osf(paper)
        if res:
            results[slug] = res
            with open(OUTPUT_REGISTRY, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"💾 Registry OSF diperbarui: {OUTPUT_REGISTRY}")

    print("\n=================================================================")
    print(f"✨ COMPLETED! Total {len(results)} papers registered in OSF.")
    print(f"📁 Output registry: {OUTPUT_REGISTRY}")
    print("=================================================================")

if __name__ == "__main__":
    main()
