#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - OSF (Open Science Framework) Automated Academic Paper Sync & DOI Minter
- Target Platform: OSF (Center for Open Science, USA)
- Author: Ilham Pradani (ORCID: 0009-0008-1310-6169)
- Affiliation: PT CHAIN ASIA CONECT Research & Development Division
- Pipeline:
  1. Creates dedicated public OSF project node for each academic paper
  2. Uploads full 4-5 page unabridged peer-reviewed PDF to OSF Storage
  3. Mints official DOI (10.17605/OSF.IO/<ID>)
  4. Saves registry to src/data/osf_records.json
"""

import os
import sys
import json
import urllib.request
import urllib.error

TOKEN = os.environ.get("OSF_API_TOKEN", "")
DOCS_DIR = os.environ.get("DOCS_DIR", "/root/journal/public/docs")
OUTPUT_REGISTRY = "/root/journal/src/data/osf_records.json"

PAPERS_METADATA = [
    {
        "slug": "model-integratif-physical-digital-twin-dengan-legal-ontology-dan-marl-untuk-optimasi-dual-temperature-cold-storage-mikro-di-tnbbs-krui",
        "title": "Integrative Physical-Digital Twin Model with Legal Ontology and Multi-Agent Reinforcement Learning for Dual-Temperature Micro Cold-Storage in TNBBS, Krui",
        "category": "project",
        "tags": ["digital twin", "cold storage", "multi-agent reinforcement learning", "legal ontology", "tnbbs", "pesisir barat", "smart contracts"],
        "zenodoDoi": "10.5281/zenodo.24028621",
        "pdfFile": "model-integratif-physical-digital-twin-dengan-legal-ontology-dan-marl-untuk-optimasi-dual-temperature-cold-storage-mikro-di-tnbbs-krui.pdf"
    },
    {
        "slug": "hybrid-model-pembiayaan-faktur-digital-berbasis-perikatan-perdata-dan-jaminan-stok-sembako-untuk-pedagang-pasar-tradisional-krui",
        "title": "Hybrid Digital Invoice Financing Model Based on Civil Obligations and Staple Food Stock Collateral for Traditional Market Vendors in Krui",
        "category": "project",
        "tags": ["fintech", "invoice financing", "civil code", "kuhperdata", "traditional markets", "staple food supply chain", "pesisir barat"],
        "zenodoDoi": "10.5281/zenodo.24028618",
        "pdfFile": "hybrid-model-pembiayaan-faktur-digital-berbasis-perikatan-perdata-dan-jaminan-stok-sembako-untuk-pedagang-pasar-tradisional-krui.pdf"
    },
    {
        "slug": "model-integratif-3dimensi-thermalteknisyuridis-untuk-mikronode-coldstorage-dualtemperature-berbasis-blockchain-di-koridor-konservasi-tnbbs",
        "title": "Three-Dimensional Integrative Model (Thermal, Technical, and Juridical) for Blockchain-Based Dual-Temperature Micro-Node Cold Storage in TNBBS Conservation Corridor",
        "category": "project",
        "tags": ["thermal modeling", "blockchain", "cfd simulation", "smart legal contracts", "tnbbs", "cold chain", "conservation logistics"],
        "zenodoDoi": "10.5281/zenodo.24028633",
        "pdfFile": "model-integratif-3dimensi-thermalteknisyuridis-untuk-mikronode-coldstorage-dualtemperature-berbasis-blockchain-di-koridor-konservasi-tnbbs.pdf"
    },
    {
        "slug": "model-hybrid-dagedgeiot-temperaturecredit-token-untuk-optimasi-routing-mikro-coldstorage-di-koridor-konservasi-tnbbs",
        "title": "Hybrid DAG-Edge-IoT Temperature-Credit Token Model for Routing Optimization of Micro Cold-Storage in TNBBS Conservation Corridor",
        "category": "project",
        "tags": ["directed acyclic graph", "edge computing", "iot sensors", "temperature-credit token", "marl", "green logistics", "tnbbs"],
        "zenodoDoi": "10.5281/zenodo.24028626",
        "pdfFile": "model-hybrid-dagedgeiot-temperaturecredit-token-untuk-optimasi-routing-mikro-coldstorage-di-koridor-konservasi-tnbbs.pdf"
    },
    {
        "slug": "model-distribusi-bahan-baku-hospitality-di-kawasan-3t-studi-kasus-krui-kabupaten-pesisir-barat",
        "title": "Hospitality Raw Material Distribution Logistics and Supply Contract Certainty Reconstruction in 3T Frontiers: Empirical Study of Krui, Pesisir Barat Regency",
        "category": "project",
        "tags": ["hospitality supply chain", "3t frontier logistics", "pesisir barat", "contract certainty", "perikatan perdata", "tourism economics"],
        "zenodoDoi": "10.5281/zenodo.24028640",
        "pdfFile": "model-distribusi-bahan-baku-hospitality-di-kawasan-3t-studi-kasus-krui-kabupaten-pesisir-barat.pdf"
    },
    {
        "slug": "model-hybrid-edgeaienabled-thermodynamic-control-dengan-smartcontract-incentive-untuk-optimasi-mikrocoldstorage-dualtemp-di-koridor-konservasi-tnbbs",
        "title": "Hybrid Edge-AI-Enabled Thermodynamic Control with Smart Contract Incentives for Dual-Temperature Micro-Cold-Storage in TNBBS Conservation Corridor",
        "category": "project",
        "tags": ["edge ai", "thermodynamic control", "smart contracts", "lstm predictive modeling", "tnbbs", "solar pv mini-grid"],
        "zenodoDoi": "10.5281/zenodo.24028629",
        "pdfFile": "model-hybrid-edgeaienabled-thermodynamic-control-dengan-smartcontract-incentive-untuk-optimasi-mikrocoldstorage-dualtemp-di-koridor-konservasi-tnbbs.pdf"
    },
    {
        "slug": "a-stochastic-optimization-framework-integrating-real-time-wave-forecasting-probabilistic-cargo-loss-assessment-and-performance-linked-subsidy-allocation-for-small-scale-jukung-operators-in-pulau-pisang-pesisir-barat",
        "title": "A Stochastic Optimization Framework Integrating Real-Time Wave Forecasting, Probabilistic Cargo-Loss Assessment, and Performance-Linked Subsidy Allocation for Small-Scale Jukung Operators in Pulau Pisang, Pesisir Barat",
        "category": "project",
        "tags": ["stochastic optimization", "wave forecasting", "jukung operators", "maritime safety", "cargo loss", "pulau pisang", "pesisir barat"],
        "zenodoDoi": "10.5281/zenodo.24029072",
        "pdfFile": "a-stochastic-optimization-framework-integrating-real-time-wave-forecasting-probabilistic-cargo-loss-assessment-and-performance-linked-subsidy-allocation-for-small-scale-jukung-operators-in-pulau-pisang-pesisir-barat.pdf"
    }
]

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

def sync_paper_to_osf(paper):
    slug = paper["slug"]
    pdf_path = os.path.join(DOCS_DIR, paper["pdfFile"])
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found on disk: {pdf_path}")
        return None

    pdf_size = os.path.getsize(pdf_path)
    print(f"\n=======================================================")
    print(f"📄 Processing: {paper['title']}")
    print(f"📦 PDF File: {paper['pdfFile']} ({pdf_size} bytes)")

    # 1. Fetch D1 description/abstract
    d1_url = f"https://api.chainasiaconnect.co.id/news/{slug}"
    abstract_text = ""
    try:
        req = urllib.request.Request(d1_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            art_data = json.loads(r.read().decode("utf-8"))
            abstract_text = art_data.get("excerpt", "")
    except Exception as e:
        print(f"⚠️ Failed to fetch excerpt from D1: {e}")

    desc = f"{abstract_text}\n\nPublished in Journal of Coastal Frontiers & Applied Development (JCFAD), Vol. 1 No. 1 (2026). CERN Zenodo Record: https://doi.org/{paper['zenodoDoi']}. Official Publisher: PT CHAIN ASIA CONECT Research & Development Division."
    if len(desc) > 2000:
        desc = desc[:1990] + "..."

    # 2. Create Public Project Node
    create_payload = {
        "data": {
            "type": "nodes",
            "attributes": {
                "title": paper["title"],
                "category": "project",
                "description": desc,
                "tags": paper["tags"],
                "public": True
            }
        }
    }
    print("🚀 [OSF] Creating public project node...")
    node_res = make_osf_request("https://api.osf.io/v2/nodes/", data=create_payload, method="POST")
    node_id = node_res["data"]["id"]
    node_url = f"https://osf.io/{node_id}/"
    print(f"✅ [OSF] Project Node Created: {node_id} ({node_url})")

    # 3. Upload PDF to OSF Storage
    print(f"⬆️ [OSF Storage] Uploading {paper['pdfFile']}...")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    upload_url = f"https://files.osf.io/v1/resources/{node_id}/providers/osfstorage/?name={paper['pdfFile']}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    up_req = urllib.request.Request(upload_url, data=pdf_bytes, headers=headers, method="PUT")
    with urllib.request.urlopen(up_req, timeout=60) as up_resp:
        print(f"✅ [OSF Storage] PDF Uploaded successfully (HTTP {up_resp.status})")

    # 4. Mint Official OSF DOI
    print("🏷️ [OSF DOI] Minting permanent DOI...")
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

    return {
        "slug": slug,
        "title": paper["title"],
        "osfId": node_id,
        "osfUrl": node_url,
        "osfDoi": osf_doi,
        "zenodoDoi": paper["zenodoDoi"],
        "pdfFile": paper["pdfFile"],
        "pdfSize": pdf_size
    }

def main():
    print("=================================================================")
    print("🚀 PT CHAIN ASIA CONECT - OSF DEPOSIT & DOI MINTING PIPELINE")
    print("=================================================================")

    results = {}
    if os.path.exists(OUTPUT_REGISTRY):
        try:
            with open(OUTPUT_REGISTRY, "r") as f:
                results = json.load(f)
        except Exception:
            results = {}

    for paper in PAPERS_METADATA:
        slug = paper["slug"]
        if slug in results and results[slug].get("osfDoi"):
            print(f"⏩ [Skip] {slug} already has OSF DOI: {results[slug]['osfDoi']}")
            continue

        res = sync_paper_to_osf(paper)
        if res:
            results[slug] = res
            with open(OUTPUT_REGISTRY, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

    print("\n=================================================================")
    print(f"✨ COMPLETED! {len(results)} papers successfully registered in OSF.")
    print(f"📁 Output registry saved to: {OUTPUT_REGISTRY}")
    print("=================================================================")

if __name__ == "__main__":
    main()

