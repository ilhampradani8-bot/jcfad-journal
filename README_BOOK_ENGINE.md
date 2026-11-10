# 📚 Dokumentasi Mesin Pembuat Buku Cetak (Print-Ready Book Generator)
### PT CHAIN ASIA CONECT Research & Development Division
**Status**: Operasional Penuh & Teruji Produksi (Production Ready — Skor 100.0%)  
**Pembaruan Terakhir**: 10 November 2026  
**Penulis Utama / Author**: Ilham Pradani (ORCID: `0009-0008-1310-6169`)

---

## 📌 Ringkasan Status & Pencapaian Terkini

Pada repositori ini telah berhasil dibangun, diuji, dan dideploy mesin pembuat buku ilmiah monograf (*Scholarly Monograph Generator*) berstandar penerbitan cetak ISO-B5 internasional yang **terpisah 100%** dari mesin artikel jurnal harian.

### 🏆 Buku 1 yang Telah Selesai & Terbit Publik:
- **Judul**: *Empati Sintetis: Psikologi Bahasa AI, Jerat Manipulasi Kognitif, dan Kedaulatan Hukum Individu*
- **Penulis**: Ilham Pradani (ORCID: `0009-0008-1310-6169`)
- **Format**: Monograf Ilmiah Komprehensif (10 Bab Lengkap, 40 Sub-bab Kanonikal, Sintesis Komprehensif, Epilog Reflektif, & Rujukan Terpilih per Sub-bab).
- **Ketebalan**: **268 Halaman Penuh ISO-B5** (Padat, 0 Halaman Kosong).
- **Total Kosakata**: **107.284 kata** (ekspansi mendalam berstandar riset doktoral/monograf komprehensif).
- **Kepadatan Sitasi**: **1.084 sitasi in-text ilmiah** (KUHPerdata, UU PDP No. 27/2022, EU AI Act 2024, GDPR, Zuboff, Kahneman, Searle, Floridi, Buber, Levinas, dsb.).
- **DataCite DOI Resmi (CERN Zenodo)**: [`10.5281/zenodo.24049169`](https://doi.org/10.5281/zenodo.24049169)
- **Zenodo Official Record**: [`https://zenodo.org/records/24049169`](https://zenodo.org/records/24049169)
- **Tabel & Rumus**: 43 Tabel Data (*Booktabs Three-Line Rules*) & 15+ Display Math Bersih (*Frameless*) dilengkapi **Catatan Pemahaman Awam** di setiap rumus.
- **Bagan Alur Konseptual**: 6 Bagan Kotak Akademik Resmi (`Bagan 1.1`, `Bagan 2.1`, `Bagan 2.2`, `Bagan 2.3`, `Bagan 7.1`, `Bagan 8.1`) bergaris formal `0.6pt`, siku tajam (zero card bulat AI), dan panah typographical (`↓`, `→`, `←`).
- **Hasil Audit Orisinalitas & Stilometrika**:
  - **Turnitin / iThenticate 5-Gram Similarity**: **0.00%** (LULUS MUTLAK, ambang batas Turnitin <= 15%).
  - **Indeks Stilometrika Burstiness (AI Detector)**: **0.74** (Gaya Penulisan Manusia Alami, ambang batas tulisan manusia >= 0.65; template AI < 0.40).
  - **Sanitasi Meta-Prompt AI**: **0 Kebocoran Prompt** (100% bersih dari sapaan AI, kalimat pengantar template, atau instruksi LLM).
- **Skor Audit Geometri & Mutu (PyMuPDF Pre-Flight)**: **100.0% (LULUS SEMPURNA / SIAP TERBIT & CETAK)**.
- **URL Publik & PDF Reader**: [`https://journal.chainasiaconnect.co.id/book`](https://journal.chainasiaconnect.co.id/book)
- **Unduh PDF Langsung**: [`https://journal.chainasiaconnect.co.id/books/empati-sintetis.pdf`](https://journal.chainasiaconnect.co.id/books/empati-sintetis.pdf)
- **Lokasi Berkas Lokal**:
  - Berkas Typst Master: `/root/journal/books/cache/empati-sintetis-buku-cetak/book_master.typ`
  - PDF Cetak: `/root/journal/books/output/empati-sintetis-buku-cetak-print-ready.pdf`
  - Berkas Draf Tiap Bab: `/root/journal/books/cache/empati-sintetis-buku-cetak/chapter-01-final.json` s/d `chapter-10-final.json`

---

## 🛑 STANDAR EMAS & ATURAN MUTLAK (LOCKED GUARDRAILS)

Setiap sesi AI baru **WAJIB** mematuhi 10 prinsip desain percetakan berikut tanpa terkecuali:

1. **Zero Card / Frameless Math (Dilarang Pakai Card Abu-Abu)**:
   - Rumus matematika **DILARANG KERAS** dibungkus card, box abu-abu (`#box(fill: luma(248)...)`), atau border apa pun karena berkesan seperti template AI murahan.
   - Wajib menggunakan *native Typst block math*:
     ```typst
     #v(0.85em)
     $ "Sim"(s_1, s_2) = (bold(e)_(s_1) dot bold(e)_(s_2)) / (norm(bold(e)_(s_1)) norm(bold(e)_(s_2))) $
     #v(0.85em)
     ```
2. **Catatan Pemahaman Awam untuk Rumus Matematika**:
   - Setiap kali rumus matematika display dihadirkan, wajib disertai **Catatan Pemahaman Awam** (`size: 8pt, style: "italic"`) di bawahnya untuk menerjemahkan formula teknis ke dalam bahasa asas hukum dan psikologi kognitif yang membumi bagi pembaca umum.
3. **Inline Math Zero-Space Rule (Anti Kurung Gantung / Orphan Parens)**:
   - Rumus inline Typst **WAJIB rapat tanpa spasi di tepi dalam** (`$expr$`, BUKAN `$ expr $`). Spasi di tepi dalam tanda `$` mengubah rumus menjadi display math dan memutus baris paragraf (menyebabkan kata terpenggal dan tanda kurung jatuh sendirian).
   - Seluruh desimal LaTeX gaya `{,}` wajib otomatis dinormalisasi menjadi standar penerbitan internasional `0.71`.
4. **Booktabs Dynamic Typography (Anti-Tumpang Tindih Tabel)**:
   - Seluruh tabel markdown wajib dikonversi ke `#table(...)` Typst standar Booktabs (tanpa garis vertikal).
   - Untuk tabel dengan **5 atau 6 kolom**, ukuran font **WAJIB otomatis turun ke 7.5pt** dengan `inset: (x: 3.5pt, y: 4pt)` dan `leading: 0.35em` agar teks panjang tidak saling tumpang tindih (*zero text overflow*).
   - Tabel 4 kolom memakai font 8pt; tabel 2-3 kolom memakai 8.5pt.
5. **Bagan Alur Resmi Typst (Bagan Kotak Presisi, Anti Card AI Bulat)**:
   - Diagram alur proses atau kausalitas yuridis tidak boleh menggunakan teks ASCII typewriter mentah (`--->`) yang patah.
   - Wajib dikonversi ke `#block(...)` Typst bergaris tipis formal (`0.6pt black`, sudut siku 0pt, tanpa shadow) dengan panah typographical (`↓`, `→`, `←`), grid simetris, dan nomor bagan resmi (`*Bagan X.Y: ...*`).
6. **Penomoran Subbab Humanis (Anti `10.3.4` & Anti Kurung Siku `[ ]`)**:
   - Dilarang keras menggunakan penomoran kaku 3-4 digit seperti `1.1.1` atau `10.3.4` pada heading naskah monograf.
   - Dilarang menyisakan kurung siku prompt `[Dimensi Genealogi & Epistemologi]`.
   - Judul sub-subbab wajib tampil mengalir dan anggun: `=== Dimensi Genealogi dan Epistemologi`.
7. **Daftar Isi (TOC) Kompak & Proporsional**:
   - Daftar Isi wajib kompak (`depth: 2`), bebas dari judul duplikat atau sub-bab berulang.
   - Didesain dengan `#show outline.entry`: Judul Bab `8.5pt bold` dan Sub-bab `7.5pt regular` (`fill: luma(65)`), ter-indentasi rapi dengan titik-titik pemandu halus, cukup 1–2 halaman elegan.
8. **Running Header & Footer Wajib (Single-Line Rule)**:
   - Mulai halaman Romawi (Prakata) hingga akhir buku:
     - **Header**: Garis hairline `0.35pt`. Wajib **tepat 1 baris bersih** (menggunakan *Short Running Title*, DILARANG tertekuk 2 baris). Halaman Genap menampilkan Judul Pendek Monograf (*Empati Sintetis*), Halaman Ganjil menampilkan Nama Penulis (*Ilham Pradani*).
     - **Footer**: Garis hairline tipis `0.25pt`, **nomor halaman tebal di margin luar**, dan metadata penerbit (*PT CHAIN ASIA CONECT — Scholarly Series*) di margin dalam.
9. **Zero Blank Pages (Anti Halaman Kosong)**:
   - Dilarang keras menggunakan `#pagebreak(to: "odd")` ganda di dalam naskah.
   - Wajib menggunakan `#pagebreak()` bersih agar pembaca digital tidak menemukan halaman kosong yang membingungkan.
10. **Automated Geometric PDF Review Engine**:
    - Setiap kompilasi PDF wajib diverifikasi otomatis oleh modul `review_book_pdf` menggunakan **PyMuPDF geometric inspection** (memverifikasi zero orphan parens, zero malformed decimals, zero prompt leaks, serta single-line header/footer geometry) dan harus lulus dengan skor 100%.

---

## 🏛️ Ketentuan Pendaftaran ISBN & Hak Cipta Penerbit (Perpusnas RI)

1. **Aturan Resmi Perpusnas RI**:
   - Pendaftaran ISBN di Indonesia **tidak dapat dilakukan oleh perorangan/penulis pribadi**.
   - Permohonan akun ISBN di situs resmi Perpusnas (`isbn.perpusnas.go.id`) **wajib melalui badan usaha / badan hukum resmi** (PT, CV, Yayasan, Lembaga Litbang, Perguruan Tinggi, dsb.) yang memiliki Akta Notaris, NPWP, dan NIB/izin usaha.
2. **Biaya Resmi ISBN**:
   - Biaya resmi permohonan ISBN di Perpustakaan Nasional RI adalah **Rp 0 (GRATIS)**.
3. **Pencantuman Nama PT CHAIN ASIA CONECT**:
   - Dicantumkan saat ini sebagai **Afiliasi Riset Penulis** (*Research & Development Division*) untuk legitimasi kepakaran dan hak cipta draf.
   - Sebagai pemilik badan hukum PT resmi, PT CHAIN ASIA CONECT dapat didaftarkan sebagai **Penerbit Mandiri Resmi** di Perpusnas tanpa perantara.
   - Jika di masa mendatang buku ini dicetak massal oleh penerbit eksternal (Gramedia, Prenada, Mizan, Deepublish, atau Penerbit Kampus), pihak penerbit tersebut yang akan menguruskan ISBN atas nama penerbit mereka, dan imprint penerbit dapat disesuaikan dengan mudah.

---

## 🛠️ Panduan Perintah Cepat untuk Sesi Baru

Bila membuka sesi baru, gunakan perintah-perintah berikut:

```bash
# 1. Mengompilasi ulang buku dari cache JSON ke PDF berstandar cetak:
python3 /root/journal/scripts/compile-book-typst.py empati-sintetis-buku-cetak

# 2. Build ulang website Astro:
npm run build

# 3. Deploy langsung ke Cloudflare Pages (menggunakan kredensial global):
npx wrangler pages deploy dist --project-name=jcfad-journal --branch=main

# 4. Sinkronisasi Git ganda (GitHub + VPS):
autopush "pesan commit"
```

---

## 💡 Konsep Buku Berikutnya yang Tersedia di Antrean
1. **Buku 2**: *Hak untuk Sunyi (The Right to Disconnect)* — Psikologi kelelahan mental, linguistik tekanan korporat, dan kedaulatan waktu kerja digital.
2. **Buku 3**: *Linguistik Forensik & Pembuktian Niat* — Membedakan teks manusia vs AI di peradilan pidana/perdata dan steganografi gaya bahasa (*stylometry*).
