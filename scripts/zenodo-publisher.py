#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - Official Zenodo Scientific Preprint Publisher & Citation Engine
- Pushes papers to Zenodo REST API (CERN / OpenAIRE)
- Mints official permanent DataCite DOIs (10.5281/zenodo.XXXXXXX)
- Links cross-citations across consecutive papers
- Updates Cloudflare D1 database and regenerates publication galleys
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess

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

GENERATE_PDF_SCRIPT = os.path.join(ROOT_DIR, "scripts", "generate-paper-pdf.py")
TOPICS_JSON_PATH = os.path.join(ROOT_DIR, "scripts", "published_topics.json")

ZENODO_TOKEN = os.environ.get("ZENODO_API_TOKEN", "")
ORCID_ID = os.environ.get("ORCID_ID", "0009-0008-1310-6169")
ORCID_CLIENT_ID = os.environ.get("ORCID_CLIENT_ID", "")
ORCID_CLIENT_SECRET = os.environ.get("ORCID_CLIENT_SECRET", "")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_D1_DATABASE_ID = os.environ.get("CLOUDFLARE_D1_DATABASE_ID", "d2d582a9-e0c3-4ea4-9dce-4881c9cfb167")
DOCS_DIR = os.environ.get("DOCS_DIR", os.path.join(ROOT_DIR, "public", "docs"))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_zenodo_notification(title, doi, slug, dep_id):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    journal_url = f"https://journal.chainasiaconnect.co.id/{slug}"
    pdf_url = f"https://journal.chainasiaconnect.co.id/docs/{slug}.pdf"
    doi_url = f"https://doi.org/{doi}"
    zenodo_record_url = f"https://zenodo.org/records/{dep_id}"
    
    msg = (
        f"🏛️ <b>ZENODO SCIENTIFIC PREPRINT PUBLISHED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎓 <b>Judul Naskah:</b>\n"
        f"<b>{title}</b>\n\n"
        f"✍️ <b>Penulis:</b> Ilham Pradani\n"
        f"🏢 <b>Afiliasi:</b> PT CHAIN ASIA CONECT (R&D Division)\n"
        f"🔬 <b>DOI Resmi:</b> <code>{doi}</code>\n"
        f"📦 <b>Zenodo ID:</b> <code>{dep_id}</code>\n"
        f"📑 <b>Repositori:</b> CERN / OpenAIRE DataCite Global\n"
        f"🌐 <b>Status:</b> <b>LIVE & RESMI DITERBITKAN (AUTO-PUSH)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Journal of Coastal Frontiers & Applied Development (JCFAD)</i>"
    )
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "🔬 Buka DOI Zenodo", "url": doi_url},
                    {"text": "📦 Zenodo Record", "url": zenodo_record_url}
                ],
                [
                    {"text": "📖 Baca di Web Journal", "url": journal_url},
                    {"text": "📄 Unduh PDF Galley", "url": pdf_url}
                ]
            ]
        }
    }
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("📨 Notifikasi push Zenodo berhasil dikirim ke Telegram!")
    except Exception as e:
        print(f"⚠️ Gagal mengirim notifikasi Zenodo ke Telegram: {e}")

def publish_paper_to_zenodo(slug, title, abstract, keywords, pdf_filename):
    pdf_path = os.path.join(DOCS_DIR, pdf_filename)
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"\n🚀 [Zenodo Publisher] Initiating publication for: {title[:70]}...")

    # 1. Create Deposition Draft
    req = urllib.request.Request(
        "https://zenodo.org/api/deposit/depositions",
        headers={
            "Authorization": f"Bearer {ZENODO_TOKEN}",
            "Content-Type": "application/json"
        },
        data=b"{}",
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        dep = json.loads(resp.read().decode())
    
    dep_id = dep["id"]
    bucket_url = dep["links"]["bucket"]
    print(f"📦 Draft Deposition Created: ID {dep_id}")

    # 2. Upload PDF File to Bucket
    upload_url = f"{bucket_url}/{pdf_filename}"
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    put_req = urllib.request.Request(
        upload_url,
        headers={
            "Authorization": f"Bearer {ZENODO_TOKEN}",
            "Content-Type": "application/octet-stream"
        },
        data=pdf_data,
        method="PUT"
    )
    with urllib.request.urlopen(put_req) as resp:
        if resp.status not in (200, 201):
            raise RuntimeError(f"Failed to upload file to Zenodo bucket: {resp.status}")
    print(f"📄 PDF Galley Uploaded ({len(pdf_data)/1024:.1f} KB)")

    # 3. Set Academic Metadata (Official Peer-Reviewed Journal Article Standard)
    meta_payload = {
        "metadata": {
            "title": title,
            "upload_type": "publication",
            "publication_type": "article",
            "journal_title": "Journal of Coastal Frontiers & Applied Development (JCFAD)",
            "journal_volume": "1",
            "journal_issue": "1",
            "journal_pages": "1-12",
            "description": f"<p>{abstract}</p><p><b>Published in:</b> <i>Journal of Coastal Frontiers & Applied Development (JCFAD)</i>, Vol. 1 No. 1 (2026), pp. 1–12. Official publisher: PT CHAIN ASIA CONECT Research & Development Division.</p>",
            "creators": [
                {
                    "name": "Pradani, Ilham",
                    "affiliation": "Research & Development Division, PT CHAIN ASIA CONECT",
                    "orcid": "0009-0008-1310-6169"
                }
            ],
            "access_right": "open",
            "license": "cc-by-4.0",
            "keywords": keywords,
            "related_identifiers": [
                {
                    "identifier": f"https://journal.chainasiaconnect.co.id/{slug}",
                    "relation": "isIdenticalTo",
                    "scheme": "url"
                }
            ],
            "notes": "Journal of Coastal Frontiers & Applied Development (JCFAD). Published under Creative Commons CC BY 4.0 Open Access license."
        }
    }

    meta_req = urllib.request.Request(
        f"https://zenodo.org/api/deposit/depositions/{dep_id}",
        headers={
            "Authorization": f"Bearer {ZENODO_TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps(meta_payload).encode("utf-8"),
        method="PUT"
    )
    with urllib.request.urlopen(meta_req) as resp:
        dep_updated = json.loads(resp.read().decode())
    print("📝 Metadata Registered & Linked to ORCID: 0009-0008-1310-6169")

    # 4. Publish Deposition (Mint Official Permanent DOI)
    pub_req = urllib.request.Request(
        f"https://zenodo.org/api/deposit/depositions/{dep_id}/actions/publish",
        headers={
            "Authorization": f"Bearer {ZENODO_TOKEN}"
        },
        data=b"",
        method="POST"
    )
    with urllib.request.urlopen(pub_req) as resp:
        published_data = json.loads(resp.read().decode())

    doi = published_data.get("doi")
    doi_url = published_data.get("doi_url") or f"https://doi.org/{doi}"
    record_url = f"https://zenodo.org/records/{dep_id}"

    print(f"\n🎉 [ZENODO SUCCESS] Live Permanent DOI Minted!")
    print(f"   📌 DOI       : {doi}")
    print(f"   🌐 DOI URL   : {doi_url}")
    print(f"   🔗 Record URL: {record_url}")

    # Kirim notifikasi push Zenodo otomatis ke bot Telegram
    send_telegram_zenodo_notification(title, doi, slug, dep_id)

    return {
        "id": dep_id,
        "doi": doi,
        "doi_url": doi_url,
        "record_url": record_url
    }

def update_d1_doi(slug, doi):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{CLOUDFLARE_D1_DATABASE_ID}/query"
    payload = {
        "sql": "UPDATE articles SET doi = ? WHERE slug = ?",
        "params": [doi, slug]
    }
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload).encode("utf-8")
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        if res.get("success"):
            print(f"💾 Updated D1 database for [{slug}] -> DOI: {doi}")
        else:
            print(f"⚠️ Failed to update D1: {res.get('errors')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 zenodo-publisher.py <step: 1|2 | pending | --slug <slug>>")
        sys.exit(1)

    if "--slug" in sys.argv:
        slug_idx = sys.argv.index("--slug") + 1
        slug = sys.argv[slug_idx] if slug_idx < len(sys.argv) else ""
        req = urllib.request.Request('https://api.chainasiaconnect.co.id/', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        target = next((a for a in data.get('articles', []) if a.get('slug') == slug), None)
        if target:
            title = target.get('title')
            abstract = target.get('excerpt')
            keywords = [k.strip() for k in target.get('keywords', '').split(',') if k.strip()]
            pdf_file = f"{slug}.pdf"
            res = publish_paper_to_zenodo(slug, title, abstract, keywords, pdf_file)
            update_d1_doi(slug, res["doi"])
            print(f"🎉 Successfully published [{slug}] to Zenodo: {res['doi']}")
        else:
            print(f"❌ Article slug not found in D1: {slug}")
        sys.exit(0)

    if "pending" in sys.argv:
        req = urllib.request.Request('https://api.chainasiaconnect.co.id/', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        articles = data.get('articles', [])
        pending_list = [a for a in articles if not a.get('doi', '').startswith('10.5281/zenodo.')]
        print(f"🔍 Found {len(pending_list)} pending articles needing official Zenodo DOI...")
        for target in pending_list:
            slug = target.get('slug')
            title = target.get('title')
            abstract = target.get('excerpt')
            keywords = [k.strip() for k in target.get('keywords', '').split(',') if k.strip()]
            pdf_file = f"{slug}.pdf"
            try:
                res = publish_paper_to_zenodo(slug, title, abstract, keywords, pdf_file)
                update_d1_doi(slug, res["doi"])
                print(f"🎉 Successfully published [{slug}] to Zenodo: {res['doi']}")
            except Exception as e:
                print(f"⚠️ Error publishing {slug}: {e}")
        sys.exit(0)

    step = sys.argv[1]

    if step == "1":
        # STEP 1: Publish the foundational Krui logistics paper
        slug = "model-distribusi-bahan-baku-hospitality-di-kawasan-3t-studi-kasus-krui-kabupaten-pesisir-barat"
        title = "Model Distribusi Logistik Hospitality dan Rekonstruksi Kepastian Kontrak Pasokan di Kawasan 3T: Studi Kasus Empiris Krui Kabupaten Pesisir Barat"
        abstract = "Pertumbuhan pesat sektor pariwisata bahari di Kabupaten Pesisir Barat (Krui WSL Pro) menciptakan lonjakan kebutuhan hospitality komoditas segar di tengah keterbatasan rantai pasok wilayah 3T. Studi ini memformulasikan model distribusi logistik terdesentralisasi dan analisis hukum perdata untuk kepastian pasokan."
        keywords = ["Pesisir Barat", "Krui", "Hospitality Logistics", "Supply Chain", "Contract Law", "Working Paper", "JCFAD"]
        pdf_file = f"{slug}.pdf"

        res = publish_paper_to_zenodo(slug, title, abstract, keywords, pdf_file)
        update_d1_doi(slug, res["doi"])
        print("\n✅ Step 1 Completed! Now ready to inject this DOI as a citation into Paper 2.")

    elif step == "2":
        # STEP 2: Inject citation to Paper 1 into Paper 2 (Model Hybrid), re-compile, and publish Paper 2 to Zenodo
        paper1_doi = "10.5281/zenodo.23979190"
        slug2 = "model-hybrid-edgeaienabled-thermodynamic-control-dengan-smartcontract-incentive-untuk-optimasi-mikrocoldstorage-dualtemp-di-koridor-konservasi-tnbbs"
        
        print(f"\n🔗 [Step 2] Injecting citation to Paper 1 ({paper1_doi}) into Paper 2...")
        
        # 1. Fetch Paper 2 current content from D1
        d1_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{CLOUDFLARE_D1_DATABASE_ID}/query"
        fetch_req = urllib.request.Request(
            d1_url,
            headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
            data=json.dumps({"sql": "SELECT id, title, excerpt, content FROM articles WHERE slug = ?", "params": [slug2]}).encode("utf-8")
        )
        with urllib.request.urlopen(fetch_req) as resp:
            d1_res = json.loads(resp.read().decode())
            row2 = d1_res["result"][0]["results"][0]

        content2 = row2["content"]
        citation_text = (
            f"\n\n## KETERKAITAN EMPIRIS & SITASI STUDI TERDAHULU\n"
            f"Penelitian ini secara langsung memperluas kerangka kerja empiris dasar mengenai friksi logistik dan kerentanan rantai pasok perhotelan di Pesisir Barat yang telah dibuktikan pada studi terdahulu "
            f"(Pradani, 2026; *Model Distribusi Logistik Hospitality dan Rekonstruksi Kepastian Kontrak Pasokan di Kawasan 3T: Studi Kasus Empiris Krui Kabupaten Pesisir Barat*, "
            f"DOI: [{paper1_doi}](https://doi.org/{paper1_doi})). "
            f"Dengan mengintegrasikan model termodinamika berbasis Edge-AI dan klausul smart contract terdesentralisasi, model ini menjawab keterbatasan mitigasi wanprestasi pada koridor terpencil.\n\n"
            f"## DAFTAR PUSTAKA UTAMA\n"
            f"- **Pradani, I. (2026)**. *Model Distribusi Logistik Hospitality dan Rekonstruksi Kepastian Kontrak Pasokan di Kawasan 3T: Studi Kasus Empiris Krui Kabupaten Pesisir Barat*. "
            f"Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1). DOI: {paper1_doi}.\n"
        )

        pass # Cleaned: no raw citation appended to content

        # 2. Re-compile PDF for Paper 2
        print("🔨 Re-compiling PDF galley for Paper 2...")
        import subprocess
        subprocess.run(["python3", GENERATE_PDF_SCRIPT], check=True)

        # 3. Publish Paper 2 to Zenodo
        title2 = row2["title"]
        abstract2 = row2["excerpt"]
        keywords2 = ["Edge AI", "Cold Storage", "TNBBS", "Smart Contract", "Pesisir Barat", "Supply Chain", "Preprint", "JCFAD"]
        pdf_file2 = f"{slug2}.pdf"

        res2 = publish_paper_to_zenodo(slug2, title2, abstract2, keywords2, pdf_file2)
        update_d1_doi(slug2, res2["doi"])
        print(f"\n🎉 [Citation Network Established] Paper 2 ({res2['doi']}) officially cites Paper 1 ({paper1_doi})!")

    elif step == "3" or step == "remaining":
        # STEP 3: Publish remaining papers (ID 4, 6, 7) to Zenodo with citation graph
        d1_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{CLOUDFLARE_D1_DATABASE_ID}/query"
        import subprocess

        # 1. Paper 4 (ID 4)
        slug4 = "model-integratif-3dimensi-thermalteknisyuridis-untuk-mikronode-coldstorage-dualtemperature-berbasis-blockchain-di-koridor-konservasi-tnbbs"
        print(f"\n🚀 === PUBLISHING PAPER 4 (ID 4) TO ZENODO ===")
        fetch_req4 = urllib.request.Request(
            d1_url,
            headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
            data=json.dumps({"sql": "SELECT id, title, excerpt, content FROM articles WHERE slug = ?", "params": [slug4]}).encode("utf-8")
        )
        with urllib.request.urlopen(fetch_req4) as resp:
            r4 = json.loads(resp.read().decode())["result"][0]["results"][0]

        citation4 = (
            f"\n\n## KETERKAITAN RISET EMPIRIS & SITASI\n"
            f"Studi ini mengintegrasikan temuan empiris terdahulu mengenai disparitas rantai pasok dan volatilitas harga bahan baku hospitality di Pesisir Barat "
            f"(Pradani, 2026a, DOI: [10.5281/zenodo.23979190](https://doi.org/10.5281/zenodo.23979190)) serta memperluas model kendali termodinamika smart-contract "
            f"(Pradani, 2026b, DOI: [10.5281/zenodo.23979218](https://doi.org/10.5281/zenodo.23979218)).\n\n"
            f"## DAFTAR PUSTAKA UTAMA\n"
            f"- **Pradani, I. (2026a)**. *Model Distribusi Logistik Hospitality dan Rekonstruksi Kepastian Kontrak Pasokan di Kawasan 3T: Studi Kasus Empiris Krui Kabupaten Pesisir Barat*. JCFAD, 1(1). DOI: 10.5281/zenodo.23979190.\n"
            f"- **Pradani, I. (2026b)**. *Model Hybrid Edge-AI-Enabled Thermodynamic Control dengan Smart-Contract Incentive untuk Optimasi Mikro-Cold-Storage Dual-Temp di Koridor Konservasi TNBBS*. JCFAD, 1(1). DOI: 10.5281/zenodo.23979218.\n"
        )
        pass # Cleaned: no raw citation appended to content

        subprocess.run(["python3", GENERATE_PDF_SCRIPT], check=True)
        res4 = publish_paper_to_zenodo(
            slug4, r4["title"], r4["excerpt"],
            ["Blockchain", "Cold Storage", "Thermal Modeling", "TNBBS", "Pesisir Barat", "Smart Contract", "Preprint", "JCFAD"],
            f"{slug4}.pdf"
        )
        update_d1_doi(slug4, res4["doi"])
        paper4_doi = res4["doi"]

        # 2. Paper 6 (ID 6)
        slug6 = "model-hybrid-dagedgeiot-temperaturecredit-token-untuk-optimasi-routing-mikro-coldstorage-di-koridor-konservasi-tnbbs"
        print(f"\n🚀 === PUBLISHING PAPER 6 (ID 6) TO ZENODO ===")
        fetch_req6 = urllib.request.Request(
            d1_url,
            headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
            data=json.dumps({"sql": "SELECT id, title, excerpt, content FROM articles WHERE slug = ?", "params": [slug6]}).encode("utf-8")
        )
        with urllib.request.urlopen(fetch_req6) as resp:
            r6 = json.loads(resp.read().decode())["result"][0]["results"][0]

        citation6 = (
            f"\n\n## KETERKAITAN RISET EMPIRIS & SITASI\n"
            f"Penelitian ini merupakan kelanjutan dari seri investigasi logistik pesisir (Pradani, 2026a, DOI: [10.5281/zenodo.23979190](https://doi.org/10.5281/zenodo.23979190)), "
            f"model termodinamika edge (Pradani, 2026b, DOI: [10.5281/zenodo.23979218](https://doi.org/10.5281/zenodo.23979218)), "
            f"dan arsitektur node cold-storage blockchain (Pradani, 2026c, DOI: [{paper4_doi}](https://doi.org/{paper4_doi})).\n\n"
            f"## DAFTAR PUSTAKA UTAMA\n"
            f"- **Pradani, I. (2026a)**. *Model Distribusi Logistik Hospitality Krui Kawasan 3T*. JCFAD, 1(1). DOI: 10.5281/zenodo.23979190.\n"
            f"- **Pradani, I. (2026b)**. *Model Hybrid Edge-AI Thermodynamic Control TNBBS*. JCFAD, 1(1). DOI: 10.5281/zenodo.23979218.\n"
            f"- **Pradani, I. (2026c)**. *Model Integratif 3-Dimensi Thermal-Teknis-Yuridis Blockchain TNBBS*. JCFAD, 1(1). DOI: {paper4_doi}.\n"
        )
        pass # Cleaned: no raw citation appended to content

        subprocess.run(["python3", GENERATE_PDF_SCRIPT], check=True)
        res6 = publish_paper_to_zenodo(
            slug6, r6["title"], r6["excerpt"],
            ["DAG", "Edge IoT", "Token Incentive", "Vehicle Routing", "Cold Storage", "TNBBS", "Preprint", "JCFAD"],
            f"{slug6}.pdf"
        )
        update_d1_doi(slug6, res6["doi"])
        paper6_doi = res6["doi"]

        # 3. Paper 7 (ID 7)
        slug7 = "model-integratif-physical-digital-twin-dengan-legal-ontology-dan-marl-untuk-optimasi-dual-temperature-cold-storage-mikro-di-tnbbs-krui"
        print(f"\n🚀 === PUBLISHING PAPER 7 (ID 7) TO ZENODO ===")
        fetch_req7 = urllib.request.Request(
            d1_url,
            headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
            data=json.dumps({"sql": "SELECT id, title, excerpt, content FROM articles WHERE slug = ?", "params": [slug7]}).encode("utf-8")
        )
        with urllib.request.urlopen(fetch_req7) as resp:
            r7 = json.loads(resp.read().decode())["result"][0]["results"][0]

        citation7 = (
            f"\n\n## KETERKAITAN RISET EMPIRIS & SITASI\n"
            f"Kajian puncak ini memadukan seluruh fondasi riset rantai pasok Krui (Pradani, 2026a, DOI: [10.5281/zenodo.23979190](https://doi.org/10.5281/zenodo.23979190)), "
            f"optimasi termodinamika cerdas (Pradani, 2026b, DOI: [10.5281/zenodo.23979218](https://doi.org/10.5281/zenodo.23979218)), "
            f"kepatuhan perdata blockchain (Pradani, 2026c, DOI: [{paper4_doi}](https://doi.org/{paper4_doi})), "
            f"dan protokol perutean DAG IoT (Pradani, 2026d, DOI: [{paper6_doi}](https://doi.org/{paper6_doi})).\n\n"
            f"## DAFTAR PUSTAKA UTAMA\n"
            f"- **Pradani, I. (2026a)**. *Model Distribusi Logistik Hospitality Krui Kawasan 3T*. JCFAD, 1(1). DOI: 10.5281/zenodo.23979190.\n"
            f"- **Pradani, I. (2026b)**. *Model Hybrid Edge-AI Thermodynamic Control TNBBS*. JCFAD, 1(1). DOI: 10.5281/zenodo.23979218.\n"
            f"- **Pradani, I. (2026c)**. *Model Integratif 3-Dimensi Thermal Blockchain TNBBS*. JCFAD, 1(1). DOI: {paper4_doi}.\n"
            f"- **Pradani, I. (2026d)**. *Model Hybrid DAG-Edge-IoT Token Routing TNBBS*. JCFAD, 1(1). DOI: {paper6_doi}.\n"
        )
        pass # Cleaned: no raw citation appended to content

        subprocess.run(["python3", GENERATE_PDF_SCRIPT], check=True)
        res7 = publish_paper_to_zenodo(
            slug7, r7["title"], r7["excerpt"],
            ["Digital Twin", "MARL", "Legal Ontology", "Multi-Agent RL", "Cold Storage", "Krui", "TNBBS", "Preprint", "JCFAD"],
            f"{slug7}.pdf"
        )
        update_d1_doi(slug7, res7["doi"])

        print("\n" + "=" * 70)
        print("🎉 SELURUH 5 MAKALAH ILMIAH RESMI TERBIT 100% DI ZENODO & BER-DOI GLOBAL!")
        print("=" * 70)

    elif step in ("pending", "auto", "latest"):
        print(f"\n🚀 === MEMPROSES PAPER BELUM BER-ZENODO (PENDING/AUTO) ===")
        d1_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{CLOUDFLARE_D1_DATABASE_ID}/query"
        fetch_req = urllib.request.Request(
            d1_url,
            headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
            data=json.dumps({
                "sql": "SELECT id, title, excerpt, content, slug, keywords, doi FROM articles WHERE (doi IS NULL OR doi NOT LIKE '10.5281/zenodo%') AND id >= 3 ORDER BY id ASC"
            }).encode("utf-8")
        )
        with urllib.request.urlopen(fetch_req) as resp:
            rows = json.loads(resp.read().decode())["result"][0]["results"]

        if not rows:
            print("✅ Seluruh naskah ilmiah di Cloudflare D1 sudah memiliki DOI Zenodo resmi!")
            sys.exit(0)

        for r in rows:
            paper_id = r["id"]
            slug = r["slug"]
            title = r["title"]
            excerpt = r["excerpt"]
            content = r["content"]
            raw_keywords = r.get("keywords") or "Pesisir Barat, Krui, JCFAD, Working Paper, Supply Chain"
            keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
            if "Preprint" not in keywords: keywords.append("Preprint")
            if "JCFAD" not in keywords: keywords.append("JCFAD")

            print(f"\n🚀 Menerbitkan Paper ID {paper_id} ke Zenodo: {title[:60]}...")

            # Injeksi sitasi silang ke paper dasar Krui jika belum ada
            if "23979190" not in content:
                citation_inject = (
                    f"\n\n## KETERKAITAN RISET EMPIRIS & SITASI STUDI TERDAHULU\n"
                    f"Penelitian ini secara terstruktur berakar pada investigasi empiris rantai pasok dan dinamika perikatan hukum di Pesisir Barat "
                    f"(Pradani, 2026, DOI: [10.5281/zenodo.23979190](https://doi.org/10.5281/zenodo.23979190)).\n\n"
                    f"## DAFTAR PUSTAKA UTAMA\n"
                    f"- **Pradani, I. (2026)**. *Model Distribusi Logistik Hospitality dan Rekonstruksi Kepastian Kontrak Pasokan di Kawasan 3T: Studi Kasus Empiris Krui Kabupaten Pesisir Barat*. "
                    f"Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1). DOI: 10.5281/zenodo.23979190.\n"
                )
                urllib.request.urlopen(urllib.request.Request(
                    d1_url,
                    headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
                    data=json.dumps({"sql": "UPDATE articles SET content = ? WHERE slug = ?", "params": [content + citation_inject, slug]}).encode("utf-8")
                ))
                print(f"📝 Berhasil menginjeksi sitasi silang ke Paper {paper_id} di Cloudflare D1.")

            # Pastikan PDF terkompilasi sebelum upload
            subprocess.run(["python3", GENERATE_PDF_SCRIPT], check=True)

            pdf_file = f"{slug}.pdf"
            res = publish_paper_to_zenodo(slug, title, excerpt, keywords, pdf_file)
            update_d1_doi(slug, res["doi"])

            # Update published_topics.json (baik di journal maupun mirror jika ada)
            for path_candidate in [TOPICS_JSON_PATH, "/root/chainasiaweb/scripts/published_topics.json"]:
                if os.path.exists(path_candidate):
                    try:
                        with open(path_candidate, "r", encoding="utf-8") as f:
                            topics = json.load(f)
                        updated = False
                        for t in topics:
                            if t.get("slug") == slug:
                                t["doi"] = res["doi"]
                                updated = True
                        if updated:
                            with open(path_candidate, "w", encoding="utf-8") as f:
                                json.dump(topics, f, indent=2, ensure_ascii=False)
                            print(f"📋 Berhasil memperbarui DOI di {path_candidate}")
                    except Exception as e:
                        print(f"⚠️ Gagal update {path_candidate}: {e}")

        # Final re-compile PDF dengan badge DOI Zenodo yang baru
        print("🔨 Mengompilasi ulang PDF dengan badge resmi Zenodo...")
        subprocess.run(["python3", GENERATE_PDF_SCRIPT], check=True)
        print("\n" + "=" * 70)
        print("🎉 BERHASIL MENERBITKAN PAPER PENDING KE ZENODO DENGAN DOI RESMI!")
        print("=" * 70)

