# Journal of Coastal Frontiers & Applied Development (JCFAD)

Official independent open-access scholarly journal portal hosted at **[https://journal.chainasiaconnect.co.id](https://journal.chainasiaconnect.co.id)**.

---

## 📌 Identitas & Metadata Jurnal

- **Nama Jurnal**: Journal of Coastal Frontiers & Applied Development (JCFAD)
- **ISSN / Tipe**: Open Access Working Paper Preprint Series
- **Publisher**: PT CHAIN ASIA CONECT Research & Development Division
- **Focus & Scope**: Empirical Regional Studies, Supply Chain Finance, Cold-Chain Logistics, Indonesian Civil Code (KUHPerdata) Contract Law, and Applied Development in 3T Frontiers (Krui, Pesisir Barat Regency, Lampung, Indonesia).
- **Indexing & Repositories**: Scopus Standard, CERN Zenodo (DOI Prefix `10.5281/zenodo.*`), Open Science Framework (OSF, DOI Prefix `10.17605/OSF.IO/*`), Crossref, Google Scholar, SINTA Kemendikbudristek, ORCID.
- **Licensing**: Creative Commons Attribution 4.0 International (CC BY 4.0 Open Access).
- **Arsitektur Hosting**: 100% Serverless di Cloudflare Pages Edge (`jcfad-journal`), zero VPS/hardware dependency, 24/7 global uptime.

---

## 🏗️ Struktur Proyek & Panduan AI Agent

Proyek ini telah **dipisahkan secara permanen** dari repositori korporat `chainasiaweb` agar AI agent memiliki context window yang bersih, fokus, dan tidak tercampur aduk dengan fitur korporasi.

```
/root/journal
├── astro.config.mjs              # Konfigurasi Astro (site: https://journal.chainasiaconnect.co.id)
├── package.json                  # Dependencies (Astro, Tailwind, Wrangler, etc.)
├── README.md                     # Dokumentasi arsitektur & panduan AI agent
├── .gitignore                    # Git ignore (dist, .wrangler, tokens, cache)
├── public/
│   ├── _headers                  # CORS & Header Caching PDF untuk Google Scholar Crawler
│   ├── robots.txt                # Robot crawl rules & sitemap index
│   ├── docs/                     # Repositori file PDF naskah ilmiah resmi hasil kompilasi
│   └── images/                   # Asset visual jurnal (seal, logo, indexing logos)
├── src/
│   ├── components/               # Komponen UI (JournalHeader, Footer, TelegramChatBubble)
│   ├── layouts/                  # Layout utama (Layout.astro dengan Google Scholar meta tags)
│   ├── lib/                      # Utilitas parsing berita/jurnal, filter artikel, & parser tabel
│   │   ├── news.js               # Parser D1 API / Google Sheets & Three-Line Table HTML
│   │   └── versions.js           # Penanganan versi naskah & riwayat revisi
│   ├── data/
│   │   ├── osf_records.json      # Mapping metadata naskah, DOI OSF, & File ID
│   │   └── versions_v1.json      # Snapshot riwayat naskah
│   └── pages/
│       ├── index.astro           # Halaman Beranda JCFAD (Volume, Isu, Daftar Artikel)
│       ├── [slug].astro          # Halaman Pembaca Naskah Ilmiah (Freeze sidebar, sitasi, DOI, PDF)
│       ├── editorial-board.astro # Dewan Redaksi & Peer Reviewers
│       ├── focus-scope.astro     # Fokus & Ruang Lingkup Penelitian
│       ├── indexing.astro        # Informasi Indeksasi & Repositori Ilmiah
│       ├── ethics.astro          # Etika Publikasi & Integritas Ilmiah
│       ├── submissions.astro     # Panduan Penulisan & Pengiriman Naskah
│       └── sitemap.xml.js        # Dynamic scholarly sitemap generator
└── scripts/
    ├── generate-paper-pdf.py     # Engine kompilasi PDF naskah Typst 2-kolom berstandar IEEE/ACM
    ├── sync-osf-papers.py        # Script sinkronisasi & push revisi naskah ke OSF Storage
    └── zenodo-publisher.py       # Script deposit naskah ilmiah ke CERN Zenodo API
```

---

## 📜 Panduan & Aturan AI Agent (Agent Rules & Guardrails)

Jika Anda adalah AI Agent (Antigravity, Cursor, Claude Code, Gemini CLI) yang bekerja pada repositori ini, patuhi aturan mutlak berikut:

1. **Integritas Konteks Ilmiah (Jurnal Murni)**:
   - Proyek ini adalah **portal jurnal ilmiah murni**. Dilarang keras menambahkan card produk jualan, penawaran korporat, atau berita umum yang tidak relevan dengan paper ilmiah.
   - Semua halaman harus mempertahankan nuansa akademik klasik (Oxford University Press / Springer / PKP OJS style): tipografi tajam, latar belakang kontras tinggi, dan tanpa efek washed-out / glassmorphism buram.
2. **Kompilasi PDF Typst (scripts/generate-paper-pdf.py)**:
   - Saat mengompilasi naskah menjadi PDF, gunakan layout 2-kolom dengan Typst (font Libertinus Serif 9pt, leading rapat).
   - **Wajib menjalankan audit kelengkapan kata & sub-judul** (skrip memiliki auditor otomatis). Jangan izinkan pemotongan teks atau penghapusan bab apapun.
   - Naskah harus memiliki header resmi (OSF Preprints atau Zenodo Preprints) dengan DOI yang aktif.
3. **Metadata Google Scholar & Indeksasi**:
   - File `src/layouts/Layout.astro` dan `src/pages/[slug].astro` menyematkan tag `<meta name="citation_*">` (Highwire Press / Google Scholar standard).
   - Jangan pernah merusak atau menghapus meta tag sitasi tersebut (`citation_title`, `citation_author`, `citation_publication_date`, `citation_pdf_url`, dll.).
4. **Mesin & Backend Tetap di UTM**:
   - Seluruh backend komputasi, generator Typst, D1 API serverless, dan Python dependencies dijalankan langsung di lingkungan UTM (WSL2 Ubuntu).

---

## 🚀 Alur Kerja & Eksekusi Perintah

### 1. Menjalankan Server Development Lokal
```bash
cd /root/journal
npm run dev
```

### 2. Membangun Proyek (Production Build)
```bash
npm run build
```

### 3. Deploy ke Cloudflare Pages Edge
```bash
# Deploy langsung folder dist ke Cloudflare Pages (Serverless)
npx wrangler pages deploy dist --project-name=jcfad-journal
```

### 4. Git Push & Sinkronisasi Global
```bash
# Menggunakan autopush universal UTM (otomatis push ke GitHub + VPS + notifikasi Telegram)
autopush "feat: update academic paper reader and indexing metadata"
```

---

## 🌐 Layanan Terkait & Integrasi

- **Domain Utama**: `https://journal.chainasiaconnect.co.id`
- **Cloudflare Pages Project**: `jcfad-journal` (`https://jcfad-journal.pages.dev`)
- **GitHub Repository**: `https://github.com/ilhampradani8-bot/jcfad-journal`
- **OSF Preprints Repository**: Open Science Framework (`https://osf.io/preprints/`)
- **CERN Zenodo Community**: `https://zenodo.org/`
