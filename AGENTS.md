# AGENTS.md - JCFAD Journal Context & Guardrails

## 🎯 Repository Purpose
This repository (`/root/journal`) contains the complete standalone code and assets for **Journal of Coastal Frontiers & Applied Development (JCFAD)**, hosted at **`https://journal.chainasiaconnect.co.id`**.

## 🛑 Critical Boundaries
1. **Academic Journal Only**: Do NOT inject corporate marketing, company business offerings, or consumer products into this repository. Keep it strictly focused on open-access research papers, peer reviews, editorial policies, and scholarly indexing.
2. **Edge Deployment**: The site deploys 100% serverlessly to Cloudflare Pages (`jcfad-journal`). It must never depend on a local server being online to serve requests.
3. **Backend Engines Stay on UTM**: Heavy PDF compilation (`scripts/generate-paper-pdf.py`), Typst rendering, and automated repository syncs (`scripts/sync-osf-papers.py`, `scripts/zenodo-publisher.py`) are executed locally on UTM.
4. **Typst PDF Integrity**: When compiling papers to PDF, verify that word count is fully preserved and all headings/subheadings are present (audit score must pass >= 90%). Never truncate text after tables.

## 🛠 Commands
- `npm run dev`: Start local Astro dev server
- `npm run build`: Build production static files into `dist/`
- `npx wrangler pages deploy dist --project-name=jcfad-journal`: Deploy to Cloudflare Pages
- `autopush "<message>"`: Dual-push to GitHub + trigger deploy + notify Telegram

