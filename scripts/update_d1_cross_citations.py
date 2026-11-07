#!/usr/bin/env python3
"""
Update Cloudflare D1 Database with Official Cross-Citations (Zenodo DOIs)
Ensures every JCFAD paper cites sister papers by Ilham Pradani / PT Chain Asia Conect
to generate valid mutual academic indexing and citations in Google Scholar & OpenAIRE.
"""

import urllib.request
import json
import subprocess
import os
import sys

CANONICAL = {
    9: "Pradani, I. (2026). A Stochastic Optimization Framework Integrating Real-Time Wave Forecasting, Probabilistic Cargo-Loss Assessment, and Performance-Linked Subsidy Allocation for Small-Scale Jukung Operators in Pulau Pisang, Pesisir Barat. Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1), 1–12. https://doi.org/10.5281/zenodo.24029072",
    8: "Pradani, I. (2026). Hybrid Digital Invoice Financing Model Based on Civil Obligations and Staple Food Stock Collateral for Traditional Market Vendors in Krui. Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1), 1–12. https://doi.org/10.5281/zenodo.24028618",
    7: "Pradani, I. (2026). Integrative Physical-Digital Twin Model with Legal Ontology and Multi-Agent Reinforcement Learning for Dual-Temperature Micro Cold-Storage in TNBBS, Krui. Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1), 1–12. https://doi.org/10.5281/zenodo.24028621",
    6: "Pradani, I. (2026). Hybrid DAG-Edge-IoT Temperature-Credit Token Model for Routing Optimization of Micro Cold-Storage in TNBBS Conservation Corridor. Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1), 1–12. https://doi.org/10.5281/zenodo.24028626",
    5: "Pradani, I. (2026). Hybrid Edge-AI-Enabled Thermodynamic Control with Smart Contract Incentives for Dual-Temperature Micro-Cold-Storage in TNBBS Conservation Corridor. Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1), 1–12. https://doi.org/10.5281/zenodo.24028629",
    4: "Pradani, I. (2026). Three-Dimensional Integrative Model (Thermal, Technical, and Juridical) for Blockchain-Based Dual-Temperature Micro-Node Cold Storage in TNBBS Conservation Corridor. Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1), 1–12. https://doi.org/10.5281/zenodo.24028633",
    3: "Pradani, I. (2026). Hospitality Raw Material Distribution Logistics and Supply Contract Certainty Reconstruction in 3T Frontiers: Empirical Study of Krui, Pesisir Barat Regency. Journal of Coastal Frontiers & Applied Development (JCFAD), 1(1), 1–12. https://doi.org/10.5281/zenodo.24028640"
}

# Cross-citation matrix ensuring closed-loop citation graph
CROSS_CITES = {
    9: [8, 7],       # Jukung cites Invoice & Digital Twin
    8: [7, 3],       # Invoice cites Digital Twin & Hospitality
    7: [6, 5],       # Digital Twin cites DAG-IoT & Edge-AI
    6: [7, 4, 3],    # DAG-IoT cites Digital Twin, 3D Model & Hospitality
    5: [7, 4],       # Edge-AI cites Digital Twin & 3D Model
    4: [6, 5],       # 3D Model cites DAG-IoT & Edge-AI
    3: [8, 7]        # Hospitality cites Invoice & Digital Twin
}

def parse_existing_refs(raw):
    if not raw:
        return []
    raw = raw.strip()
    items = []
    if raw.startswith('[') and raw.endswith(']'):
        try:
            arr = json.loads(raw)
            for item in arr:
                if isinstance(item, dict):
                    auth = item.get('author', '').strip()
                    yr = item.get('year', '').strip()
                    ti = item.get('title', '').strip()
                    jr = item.get('journal', '').strip()
                    doi = item.get('doi', '').strip()
                    doi_str = f" https://doi.org/{doi}" if doi else ""
                    items.append(f"{auth} ({yr}). {ti}. {jr}.{doi_str}")
                elif isinstance(item, str):
                    if ';' in item:
                        items.extend([p.strip() for p in item.split(';') if p.strip()])
                    else:
                        items.append(item.strip())
            return items
        except Exception:
            pass
    return [p.strip() for p in raw.split(';') if p.strip()]

def main():
    print("=" * 60)
    print("🚀 FETCHING CURRENT ARTICLES FROM D1 API...")
    print("=" * 60)
    
    req = urllib.request.Request('https://api.chainasiaconnect.co.id/', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    articles = data.get('articles', [])
    
    sql_statements = []
    
    for a in sorted(articles, key=lambda x: x.get('id', 0)):
        aid = a.get('id')
        slug = a.get('slug')
        if aid not in CROSS_CITES:
            continue
            
        raw_refs = a.get('references_list', '')
        parsed = parse_existing_refs(raw_refs)
        
        # Filter out outdated placeholder Pradani citations
        clean_refs = []
        for r in parsed:
            # Check for dummy journals / non-existent DOIs
            if ('Pradani' in r or 'Ilham' in r) and any(dummy in r for dummy in [
                '10.1016/j.jai', '10.1234/jem', 'Journal of Applied Informatics',
                'Journal of Environmental Monitoring', '10.1234/jcp'
            ]):
                continue
            clean_refs.append(r)
            
        # Prepend new sister cross-citations
        sister_cites = [CANONICAL[cid] for cid in CROSS_CITES[aid]]
        final_refs = sister_cites + clean_refs
        
        # Format as clean JSON array
        final_json_str = json.dumps(final_refs, ensure_ascii=False)
        # Escape single quotes for SQL
        escaped_sql_str = final_json_str.replace("'", "''")
        
        sql = f"UPDATE articles SET references_list = '{escaped_sql_str}' WHERE id = {aid};"
        sql_statements.append(sql)
        print(f"✅ Prepared Article ID {aid} ({slug[:40]}...): {len(final_refs)} references (added {len(sister_cites)} sister citations)")
        
    sql_file_path = "/tmp/update_cross_citations.sql"
    with open(sql_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements) + "\n")
        
    print(f"\n📁 SQL Migration file written to {sql_file_path}")
    print("⚡ Executing remote migration on Cloudflare D1 (chainasia-seo-articles)...")
    
    cmd = [
        "npx", "wrangler", "d1", "execute", "chainasia-seo-articles",
        "--remote", f"--file={sql_file_path}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("❌ Error executing SQL on D1:", res.stderr)
        sys.exit(1)
        
    print("🎉 D1 DATABASE SUCCESSFULLY UPDATED WITH CROSS-CITATIONS!")

if __name__ == "__main__":
    main()

