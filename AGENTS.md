# AGENTS.md - JCFAD Journal Context & Guardrails

## 🎯 Repository Purpose
This repository (`/root/journal`) contains the complete standalone code and assets for **Journal of Coastal Frontiers & Applied Development (JCFAD)**, hosted at **`https://journal.chainasiaconnect.co.id`**.

## 🛑 Critical Boundaries
1. **Academic Journal Only**: Do NOT inject corporate marketing, company business offerings, or consumer products into this repository. Keep it strictly focused on open-access research papers, peer reviews, editorial policies, and scholarly indexing.
2. **Edge Deployment**: The site deploys 100% serverlessly to Cloudflare Pages (`jcfad-journal`). It must never depend on a local server being online to serve requests.
3. **Backend Engines Stay on UTM**: Heavy PDF compilation (`scripts/generate-paper-pdf.py`), Typst rendering, and automated repository syncs (`scripts/sync-osf-papers.py`, `scripts/zenodo-publisher.py`) are executed locally on UTM.
4. **Typst PDF Integrity**: When compiling papers to PDF, verify that word count is fully preserved and all headings/subheadings are present (audit score must pass >= 90%). Never truncate text after tables.

## 📚 Book Engine Guardrails & Typography Standards (LOCKED RULES)
1. **Zero Card / Frameless Math**: Rumus matematika DILARANG dibungkus card, box abu-abu (`#box(fill: luma(248)...)`), atau border apa pun. Wajib native block math `$ equation $` dengan spasi vertikal `#v(0.85em)`.
2. **Inline Math Zero-Space Rule**: Rumus inline Typst WAJIB rapat tanpa spasi di tepi dalam (`$expr$`, BUKAN `$ expr $`). Spasi di tepi dalam tanda `$` mengubah rumus menjadi display math dan memutus baris paragraf (memicu kurung gantung / *orphan parentheses*). Koma desimal LaTeX `{,}` dinormalisasi menjadi `0.71`.
3. **Booktabs Dynamic Typography**: Seluruh tabel markdown wajib dikonversi ke `#table(...)` Typst standar Booktabs (tanpa garis vertikal). Tabel dengan 5+ kolom wajib memakai font `7.5pt` dan inset `4pt` agar tidak tumpang tindih (*zero overflow*).
4. **Zero Blank Pages (Anti Halaman Kosong)**: Dilarang menggunakan `#pagebreak(to: "odd")` ganda. Gunakan `#pagebreak()` bersih agar pembaca PDF digital tidak menemukan halaman kosong.
5. **Running Header & Footer Wajib**: Setiap halaman (mulai halaman Romawi & Arab) wajib memiliki garis hairline tipis, nomor halaman di pojok luar (*outer margin*), dan metadata penerbit di pojok dalam.
6. **Integritas Penutup Bab Akhir**: Bab terakhir DILARANG terpotong di tengah jalan. Wajib memuat subbab penutup tuntas, Sintesis Komprehensif, Epilog reflektif, dan Daftar Pustaka Terpilih.
7. **Gaya Penulisan Humanis (Anti-Robotik)**: Hindari pola template AI berulang (`1. **X** – Y`). Tulisan wajib mengalir dengan panjang paragraf asimetris, kaya transisi alami, analogi membumi, dan gaya skeptis-kritis khas pengguna (Target Burstiness Index >= 0.65; buku ini terverifikasi 0.74).
8. **Automated Geometric PDF Review Engine**: Kompilasi buku wajib melewati modul audit `review_book_pdf` (menggunakan PyMuPDF inspection untuk zero orphan parens & zero malformed decimals) dan harus lulus 100%. Score Turnitin & AI Stilometrika hanya ditampilkan di website (`/book`), bukan di dalam isi berkas PDF buku cetak.

## 🛠 Commands
- `npm run dev`: Start local Astro dev server
- `npm run build`: Build production static files into `dist/`
- `npx wrangler pages deploy dist --project-name=jcfad-journal`: Deploy to Cloudflare Pages
- `autopush "<message>"`: Dual-push to GitHub + trigger deploy + notify Telegram

