# AGENTS.md - JCFAD Journal Context & Guardrails

## 🎯 Repository Purpose
This repository (`/root/journal`) contains the complete standalone code and assets for **Journal of Coastal Frontiers & Applied Development (JCFAD)**, hosted at **`https://journal.chainasiaconnect.co.id`**.

## 🛑 Critical Boundaries
1. **Academic Journal Only**: Do NOT inject corporate marketing, company business offerings, or consumer products into this repository. Keep it strictly focused on open-access research papers, peer reviews, editorial policies, and scholarly indexing.
2. **Edge Deployment**: The site deploys 100% serverlessly to Cloudflare Pages (`jcfad-journal`). It must never depend on a local server being online to serve requests.
3. **Backend Engines Stay on UTM**: Heavy PDF compilation (`scripts/generate-paper-pdf.py`), Typst rendering, and automated repository syncs (`scripts/sync-osf-papers.py`, `scripts/zenodo-publisher.py`) are executed locally on UTM.
4. **Typst PDF Integrity**: When compiling papers to PDF, verify that word count is fully preserved and all headings/subheadings are present (audit score must pass >= 90%). Never truncate text after tables.

## 📚 Book & Paper Engine Guardrails & Typography Standards (LOCKED RULES)
1. **Zero Card / Frameless Math**: Rumus matematika DILARANG dibungkus card, box abu-abu (`#box(fill: luma(248)...)`), atau border apa pun. Wajib native block math `$ equation $` dengan spasi vertikal `#v(0.85em)`.
2. **Inline Math Zero-Space Rule**: Rumus inline Typst WAJIB rapat tanpa spasi di tepi dalam (`$expr$`, BUKAN `$ expr $`). Spasi di tepi dalam tanda `$` mengubah rumus menjadi display math dan memutus baris paragraf (memicu kurung gantung / *orphan parentheses*). Koma desimal LaTeX `{,}` dinormalisasi menjadi `0.71`.
3. **Booktabs Dynamic Typography & Zero-Collision Rule**: Seluruh tabel markdown wajib dikonversi ke `#table(...)` Typst standar Booktabs (tanpa garis vertikal). Dalam layout 2-kolom:
   - Tabel dengan 5+ kolom WAJIB memakai font `6.6pt`, inset padding `(x: 2.0pt, y: 3.0pt)`, leading `0.30em`, dan lebar proporsional (`1.2fr` untuk deskripsi, `1fr` untuk angka) agar angka milyaran tidak saling tumpang tindih (*zero cell collision*).
   - Tabel 4 kolom memakai font `7.5pt`, inset `3.2pt` x `3.5pt`, leading `0.35em`.
   - Tabel <= 3 kolom memakai font `8.2pt`, inset `4.5pt` x `4.0pt`.
4. **Isolated Bracket Math & Concatenated Operator Normalization**:
   - Formula matematika yang dibungkus kurung siku mandiri `[` dan `]` pada baris baru wajib dideteksi dan dikonversi menjadi display math Typst `$ equation $`.
   - Operator tanpa backslash seperti `xcdot`, `dcdot`, `fleq`, `fgeq` wajib dinormalisasi otomatis menjadi `$x dot d$` dan `$f <= f_max$`. Variabel dalam kurung `(C_{total})` pada teks dan header tabel wajib dinormalisasi ke `$C_("total")$`.
5. **Bulletproof 4-Tier Self-Healing Loop**:
   - Generator PDF wajib memiliki mekanisme swa-pulih 4 lapis: Layer 1 (AST Math Normalizer) -> Layer 2 (Typst Compiler Error Feedback untuk menangkap unknown variables `PI`, `TCT`) -> Layer 3 (Academic Audit Gate) -> Layer 4 (Universal Failsafe Mode) guna memastikan kompilasi 100% sukses tanpa kegagalan.
6. **Zero Blank Pages (Anti Halaman Kosong)**: Dilarang menggunakan `#pagebreak(to: "odd")` ganda. Gunakan `#pagebreak()` bersih agar pembaca PDF digital tidak menemukan halaman kosong.
7. **Running Header & Footer Wajib (Single-Line Rule)**: Setiap halaman (mulai halaman Romawi & Arab) wajib memiliki garis hairline tipis, nomor halaman di pojok luar (*outer margin*), dan metadata penerbit di pojok dalam. Running Header WAJIB tepat 1 baris bersih (menggunakan *Short Running Title*, dilarang membungkus/tertekuk 2 baris).
8. **Integritas Penutup Bab Akhir**: Bab terakhir DILARANG terpotong di tengah jalan. Wajib memuat subbab penutup tuntas, Sintesis Komprehensif, Epilog reflektif, dan Daftar Pustaka Terpilih.
9. **Gaya Penulisan Humanis (Anti-Robotik)**: Hindari pola template AI berulang (`1. **X** – Y`). Tulisan wajib mengalir dengan panjang paragraf asimetris, kaya transisi alami, analogi membumi, dan gaya skeptis-kritis khas pengguna (Target Burstiness Index >= 0.65; buku ini terverifikasi 0.74).
10. **Automated Geometric PDF Review Engine**: Kompilasi buku dan naskah wajib melewati modul audit `review_pdf` / `review_book_pdf` (menggunakan PyMuPDF inspection untuk zero orphan parens, zero malformed decimals, zero syntax leaks, serta single-line header/footer geometry) dan harus lulus minimal 90%.

## 🛠 Commands
- `npm run dev`: Start local Astro dev server
- `npm run build`: Build production static files into `dist/`
- `npx wrangler pages deploy dist --project-name=jcfad-journal`: Deploy to Cloudflare Pages (Production)
- `python3 scripts/audit_all_published.py`: Run full academic audit on 100% published papers
- `python3 scripts/sync-osf-papers.py --update-nodes`: Sync clean metadata & updated PDFs to all OSF nodes
- `autopush "<message>"`: Dual-push to GitHub + trigger deploy + notify Telegram

