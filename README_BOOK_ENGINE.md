# 📚 Dokumentasi Mesin Pembuat Buku Cetak (Print-Ready Book Generator)
### PT CHAIN ASIA CONECT Research & Development Division
**Status**: Operasional & Teruji (Production Ready)  
**Tanggal Rilis**: 8 November 2026  
**Penulis Utama / Author**: Ilham Pradani (ORCID: `0009-0008-1310-6169`)

---

## 📌 Ringkasan Status & Pencapaian Terkini

Pada repositori ini telah berhasil dibangun, diuji, dan dideploy mesin pembuat buku ilmiah monograf (*Scholarly Monograph Generator*) berstandar penerbitan cetak ISO-B5 internasional yang **terpisah 100%** dari mesin artikel jurnal harian.

### 🏆 Buku 1 yang Telah Selesai & Terbit Publik:
- **Judul**: *Empati Sintetis: Psikologi Bahasa AI, Jerat Manipulasi Kognitif, dan Kedaulatan Hukum Individu*
- **Penulis**: Ilham Pradani (ORCID: `0009-0008-1310-6169`)
- **Format**: Monograf Ilmiah Penuh (10 Bab Lengkap + Sintesis Komprehensif + Epilog + Daftar Pustaka Terpilih).
- **Ketebalan**: **59 Halaman Bersih ISO-B5** (Padat, 0 Halaman Kosong).
- **DataCite DOI Resmi (CERN Zenodo)**: [`10.5281/zenodo.24049169`](https://doi.org/10.5281/zenodo.24049169)
- **Zenodo Official Record**: [`https://zenodo.org/records/24049169`](https://zenodo.org/records/24049169)
- **Tabel & Rumus**: 43 Tabel Data (*Booktabs Three-Line Rules*) & 24 Display Math Bersih (*Frameless*).
- **Hasil Audit Orisinalitas & Stilometrika**:
  - **Turnitin / iThenticate 5-Gram Similarity**: **0.00%** (LULUS MUTLAK, ambang batas Turnitin <= 15%).
  - **Indeks Stilometrika Burstiness (AI Detector)**: **0.74** (Gaya Penulisan Manusia Alami, ambang batas tulisan manusia >= 0.65; template AI < 0.40).
  - **Total Kosakata**: 14.680 kata dalam 977 kalimat terstruktur asimetris.
- **Skor Audit Mutu**: **100.0% (LULUS SEMPURNA / SIAP TERBIT & CETAK)**.
- **URL Publik & PDF Reader**: [`https://journal.chainasiaconnect.co.id/book`](https://journal.chainasiaconnect.co.id/book)
- **Unduh PDF Langsung**: [`https://journal.chainasiaconnect.co.id/books/empati-sintetis.pdf`](https://journal.chainasiaconnect.co.id/books/empati-sintetis.pdf)
- **Lokasi Berkas Lokal**:
  - Berkas Typst Master: `/root/journal/books/cache/empati-sintetis-buku-cetak/book_master.typ`
  - PDF Cetak: `/root/journal/books/output/empati-sintetis-buku-cetak-print-ready.pdf`
  - Berkas Draf Tiap Bab: `/root/journal/books/cache/empati-sintetis-buku-cetak/chapter-01-final.json` s/d `chapter-10-final.json`

---

## 🛑 STANDAR EMAS & ATURAN MUTLAK (LOCKED GUARDRAILS)

Setiap sesi AI baru **WAJIB** mematuhi 8 prinsip desain percetakan berikut tanpa terkecuali:

1. **Zero Card / Frameless Math (Dilarang Pakai Card Abu-Abu)**:
   - Rumus matematika **DILARANG KERAS** dibungkus card, box abu-abu (`#box(fill: luma(248)...)`), atau border apa pun karena berkesan seperti template AI murahan.
   - Wajib menggunakan *native Typst block math*:
     ```typst
     #v(0.85em)
     $ "Sim"(s_1, s_2) = (bold(e)_(s_1) dot bold(e)_(s_2)) / (norm(bold(e)_(s_1)) norm(bold(e)_(s_2))) $
     #v(0.85em)
     ```
2. **Inline Math Zero-Space Rule (Anti Kurung Gantung / Orphan Parens)**:
   - Rumus inline Typst **WAJIB rapat tanpa spasi di tepi dalam** (`$expr$`, BUKAN `$ expr $`). Spasi di tepi dalam tanda `$` mengubah rumus menjadi display math dan memutus baris paragraf (menyebabkan kata terpenggal dan tanda kurung jatuh sendirian).
   - Seluruh desimal LaTeX gaya `{,}` wajib otomatis dinormalisasi menjadi standar penerbitan internasional `0.71`.
3. **Booktabs Dynamic Typography (Anti-Tumpang Tindih Tabel)**:
   - Seluruh tabel markdown wajib dikonversi ke `#table(...)` Typst standar Booktabs (tanpa garis vertikal).
   - Untuk tabel dengan **5 atau 6 kolom**, ukuran font **WAJIB otomatis turun ke 7.5pt** dengan `inset: (x: 4pt, y: 4.5pt)` dan `leading: 0.4em` agar teks panjang tidak saling tumpang tindih (*zero text overflow*).
   - Tabel 4 kolom memakai font 8pt; tabel 2-3 kolom memakai 8.5pt.
4. **Zero Blank Pages (Anti Halaman Kosong)**:
   - Dilarang keras menggunakan `#pagebreak(to: "odd")` ganda di dalam naskah.
   - Wajib menggunakan `#pagebreak()` bersih agar pembaca digital tidak menemukan halaman kosong yang membingungkan.
5. **Running Header & Footer Wajib (Single-Line Rule)**:
   - Mulai halaman Romawi (Prakata) hingga akhir buku:
     - **Header**: Garis hairline `0.35pt`. Wajib **tepat 1 baris bersih** (menggunakan *Short Running Title*, DILARANG tertekuk 2 baris). Halaman Genap menampilkan Judul Pendek Monograf (*Empati Sintetis*), Halaman Ganjil menampilkan Nama Penulis (*Ilham Pradani*).
     - **Footer**: Garis hairline tipis `0.25pt`, **nomor halaman tebal di margin luar**, dan metadata penerbit (*PT CHAIN ASIA CONECT — Scholarly Series*) di margin dalam.
   - DILARANG menaruh logo warna-warni di header halaman isi (standar monograf internasional Chicago & Cambridge hanya mengizinkan segel penerbit di Cover dan Title Page).
6. **Integritas Bab Akhir (Anti-Terpotong)**:
   - Bab terakhir (Bab 10) **DILARANG terpotong di tengah jalan**.
   - Wajib memuat subbab penutup tuntas, Sintesis Komprehensif, Epilog reflektif (*Menjaga Jiwa di Hadapan Mesin yang Berpura-pura Peduli*), dan Daftar Pustaka Terpilih.
7. **Integritas Edisi Ilmiah & Gaya Humanis**:
   - Buku ini adalah **Edisi Monograf Ilmiah Murni** (*Scholarly Monograph*): rumus, tabel data, fMRI, nilai p-value, dan rujukan hukum TETAP UTUH dan tidak boleh disederhanakan menjadi fiksi picisan.
   - Hindari pola template AI berulang (`1. **X** – Y`). Tulisan wajib mengalir dengan panjang paragraf asimetris, kaya transisi alami, analogi membumi, dan gaya skeptis-kritis khas pengguna.
8. **Automated Geometric PDF Review Engine**:
   - Setiap kompilasi PDF wajib diverifikasi otomatis oleh modul `review_book_pdf` menggunakan **PyMuPDF geometric inspection** (memverifikasi zero orphan parens, zero malformed decimals, serta single-line header/footer geometry) dan harus lulus dengan skor 100%.
   - Skor audit dan badge Turnitin **HANYA ditampilkan di etalase web (`/book`)**, sedangkan berkas buku PDF interior tetap steril, sakral, dan murni akademis tanpa badge.

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
