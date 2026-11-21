# AGENTS.md - JCFAD Journal Context & Guardrails

## 🎯 Repository Purpose
This repository (`/root/journal`) contains the complete standalone code and assets for **Journal of Coastal Frontiers & Applied Development (JCFAD)**, hosted at **`https://journal.chainasiaconnect.co.id`**.

## 🛑 Critical Boundaries
1. **Academic Journal & Monograph Series Only**: Do NOT inject corporate marketing, company business offerings, or consumer products into this repository. Keep it strictly focused on open-access research papers, peer reviews, editorial policies, scholarly indexing, and academic monographs.
2. **Edge Deployment**: The site deploys 100% serverlessly to Cloudflare Pages (`jcfad-journal`). It must never depend on a local server being online to serve requests.
3. **Backend Engines Stay on UTM**: Heavy PDF compilation (`scripts/generate-paper-pdf.py`), Typst rendering, and automated repository syncs (`scripts/sync-osf-papers.py`, `scripts/zenodo-publisher.py`, `scripts/compile-book-typst.py`) are executed locally on UTM.
4. **Typst PDF Integrity**: When compiling papers or books to PDF, verify that word count is fully preserved and all headings/subheadings are present (audit score must pass >= 90%). Never truncate text after tables.
5. **Real-Time DOI Reservation & Absolute Ban on ResearchGate DOIs**:
   - Every paper generated via `auto-article-groq.mjs` MUST reserve an official CERN Zenodo DOI in real-time (`10.5281/zenodo.*`) via `POST /api/deposit/depositions` BEFORE saving to Cloudflare D1 and BEFORE compiling the PDF galley.
   - Dummy or preprint ResearchGate DOIs (`10.13140/RG.*`) are **100% PERMANENTLY BANNED** from all databases, PDFs, and repository records.
   - Dual-minting: Every paper must also be synced to OSF (`scripts/sync-osf-papers.py`) to receive an official OSF DOI (`10.17605/OSF.IO/*`).
6. **24/7 Multi-Layer Watchdog & Supervisor**:
   - The daily auto-article generator is guarded by `/etc/cron.d/chainasia-auto-article` with `flock` race-condition prevention (07:00 WIB daily, `@reboot` catch-up, and hourly daytime safety watchdog 08:00–21:00 WIB).
   - The WhatsApp Bot CPNS Hub on UTM is supervised 24/7 by `/etc/cron.d/cpns-bot` (per-minute process check) and `/root/CPNS/scripts/run_daemon.sh` (5-second auto-restart loop).

## 📚 Book & Paper Engine Guardrails & Typography Standards (LOCKED RULES)
1. **Zero Card / Frameless Math**: Rumus matematika DILARANG dibungkus card, box abu-abu (`#box(fill: luma(248)...)`), atau border apa pun. Wajib native block math `$ equation $` dengan spasi vertikal `#v(0.85em)`.
2. **Catatan Pemahaman Awam untuk Rumus Matematika**: Setiap rumus matematika display wajib disertai catatan pemahaman konseptual (`size: 8pt, style: "italic"`) tepat di bawah rumus agar pembaca non-teknis / praktisi hukum dapat memahami makna intuitifnya tanpa terhalang simbol rumit.
3. **Inline Math Zero-Space Rule**: Rumus inline Typst WAJIB rapat tanpa spasi di tepi dalam (`$expr$`, BUKAN `$ expr $`). Spasi di tepi dalam tanda `$` mengubah rumus menjadi display math dan memutus baris paragraf (memicu kurung gantung / *orphan parentheses*). Koma desimal LaTeX `{,}` dinormalisasi menjadi `0.71`.
4. **Booktabs Dynamic Typography & Zero-Collision Rule**: Seluruh tabel markdown wajib dikonversi ke `#table(...)` Typst standar Booktabs (tanpa garis vertikal). Dalam layout 2-kolom:
   - Tabel dengan 5+ kolom WAJIB memakai font `6.6pt` (atau `7.5pt` pada monograf satu kolom ISO-B5), inset padding rapat, dan lebar proporsional (`1.2fr` untuk deskripsi, `1fr` untuk angka) agar teks dan angka tidak saling tumpang tindih (*zero cell collision*).
   - Tabel 4 kolom memakai font `7.5pt` - `8pt`.
   - Tabel <= 3 kolom memakai font `8.2pt` - `8.5pt`.
5. **Bagan Alur Presisi (Bagan Kotak Tipis Resmi, Zero AI Cards)**:
   - Diagram proses atau kausalitas yuridis tidak boleh menggunakan teks ASCII typewriter patah (`--->`).
   - Wajib dikonversi ke `#block(...)` Typst bergaris tipis formal (`0.6pt black`, sudut siku tajam `radius: 0pt`) dengan panah typographical (`↓`, `→`, `←`), grid simetris, dan judul bagan resmi (`*Bagan X.Y: ...*`).
6. **Penomoran Subbab Humanis (Anti `10.3.4` & Anti Kurung Siku `[ ]`)**:
   - Dilarang keras menggunakan penomoran bertingkat kaku 3-4 digit (`1.1.1`, `10.3.4`) pada naskah monograf.
   - Dilarang menyisakan kurung siku prompt `[Dimensi Genealogi & Epistemologi]`.
   - Judul sub-subbab wajib tampil anggun: `=== Dimensi Genealogi dan Epistemologi`.
7. **Daftar Isi (TOC) Kompak & Proporsional**:
   - TOC monograf wajib kompak (`depth: 2`), bebas dari judul duplikat atau sub-bab berulang.
   - Didesain dengan `#show outline.entry`: Judul Bab `8.5pt bold` dan Sub-bab `7.5pt regular` (`fill: luma(65)`), ter-indentasi rapi dengan titik-titik pemandu halus, cukup 1–2 halaman elegan.
8. **Sanitasi Total Meta-Prompt AI**:
   - Generator dan kompilator wajib memiliki filter regex yang membuang 100% sapaan AI, kalimat pembuka template, atau meta-evaluasi LLM (`Berikut adalah naskah...`, `standar akademik yang Anda tuntut...`).
9. **Zero Blank Pages (Anti Halaman Kosong)**: Dilarang menggunakan `#pagebreak(to: "odd")` ganda. Gunakan `#pagebreak()` bersih agar pembaca PDF digital tidak menemukan halaman kosong.
10. **Running Header & Footer Wajib (Single-Line Rule)**: Setiap halaman (mulai halaman Romawi & Arab) wajib memiliki garis hairline tipis, nomor halaman di pojok luar (*outer margin*), dan metadata penerbit di pojok dalam. Running Header WAJIB tepat 1 baris bersih (menggunakan *Short Running Title*, dilarang membungkus/tertekuk 2 baris).
11. **Automated Geometric & AI OCR PDF Review Engine**:
    - Kompilasi buku dan naskah wajib melewati modul audit `review_pdf` / `review_book_pdf` (menggunakan PyMuPDF inspection untuk zero orphan parens, zero malformed decimals, zero syntax leaks, serta single-line header/footer geometry) dan harus lulus minimal 90% (Buku 1 *Empati Sintetis* saat ini terverifikasi **100.0% PASS**).
    - Verifikasi visual berkas PDF dapat dilakukan langsung via AI OCR Vision Screening (`python3 scripts/ai_ocr_screening.py <path-to-pdf>`) yang mengirim biner PDF langsung ke Gemini Vision untuk mengevaluasi kelurusan garis, gutter kolom, zero collision, dan ketiadaan uncompiled math leak (ambang batas >= 90% PASS).
12. **LaTeX Inline & Nested Math Parsing Guardrail**:
    - Parser Typst `scripts/generate-paper-pdf.py` WAJIB mengonversi seluruh delimiter LaTeX `\(` dan `\)` menjadi `$expr$` sebelum `replace_paren_math` dieksekusi, serta menormalkan fungsi bersarang seperti `(\exp(-G\times t_{store}/Q))` menjadi `$exp(-G times t_("store")/Q)$` guna mencegah pecahan sintaks mentah bocor ke badan naskah PDF.

## 🛠 Commands
- `npm run dev`: Start local Astro dev server
- `npm run build`: Build production static files into `dist/`
- `npx wrangler pages deploy dist --project-name=jcfad-journal`: Deploy to Cloudflare Pages (Production)
- `python3 scripts/generate-paper-pdf.py --slug <slug> --osf`: Compile 2-column academic PDF with self-healing loop & audit
- `python3 scripts/ai_ocr_screening.py <path-to-pdf>`: Run Gemini Vision AI OCR layout, gutter & line straightness screening
- `python3 scripts/zenodo-publisher.py reserve`: Reserve a real-time CERN Zenodo deposition draft & guaranteed DOI
- `python3 scripts/zenodo-publisher.py --slug <slug>`: Publish a paper to CERN Zenodo with verified ORCID & CC-BY-4.0
- `python3 scripts/compile-book-typst.py empati-sintetis-buku-cetak`: Compile ISO-B5 book to print-ready PDF and run 100% quality audit
- `python3 scripts/compile-kdp-typst.py`: Compile Amazon KDP 6"x9" manuscript & full cover PDFs (Hardcover + Paperback)
- `python3 scripts/compile-kdp-epub.py`: Compile Amazon Kindle reflowable EPUB 3 & standalone cover JPEG
- `python3 scripts/audit_all_published.py`: Run full academic audit on 100% published papers
- `python3 scripts/sync-osf-papers.py --update-nodes`: Sync clean metadata & updated PDFs to all OSF nodes
- `autopush "<message>"`: Dual-push to GitHub + trigger deploy + notify Telegram
