# 📚 Dokumentasi Mesin Pembuat Buku Cetak (Print-Ready Book Generator)
### PT CHAIN ASIA CONECT Research & Development Division
**Status**: Operasional & Teruji (Production Ready)  
**Tanggal Rilis**: 8 November 2026  
**Penulis Utama / Author**: Ilham Pradani (ORCID: `0009-0008-1310-6169`)

---

## 📌 Ringkasan Sesi & Pencapaian Utama

Pada sesi ini telah berhasil dibangun dan diuji sistem generator buku akademik & non-fiksi profesional yang **terpisah 100%** dari mesin artikel jurnal harian.

1. **Skrip Eksekusi Mandiri**: 
   - Generator Utama: [`/root/journal/scripts/generate-book.mjs`](file:///root/journal/scripts/generate-book.mjs)
   - Kompiler Typst Khusus: [`/root/journal/scripts/compile-book-typst.py`](file:///root/journal/scripts/compile-book-typst.py)
2. **Arsitektur Tanpa Gangguan**: Tidak menyentuh database D1, cron job harian (`/etc/cron.d/chainasia-auto-article`), atau portal artikel JCFAD.
3. **100% Versi Revisi Tripartit**: Tiap bab melewati siklus `Draf Awal (gpt-oss-20b)` $\rightarrow$ `Audit Reviewer Kritis (qwen3.8-27b)` $\rightarrow$ `Full Revision Pass (gpt-oss-120b / fallback 20b)` sebelum disimpan permanen ke disk.
4. **Standar Cetak Percetakan (Print-Ready)**:
   - Layout Typst format **ISO-B5 (176 × 250 mm)** atau **ISO-A5**.
   - Gutter margin sisi dalam 2,5 cm (aman untuk jilid lem panas / *perfect binding*).
   - Penomoran romawi (`i, ii, iii`) untuk prakata dan angka biasa (`1, 2, 3...`) untuk isi buku.
   - Daftar isi otomatis (*Table of Contents*) presisi dengan titik-titik.
   - Halaman judul, hak cipta (tercantum ORCID: `0009-0008-1310-6169`), dan running header dua sisi (genap: judul buku, ganjil: nama penulis).
   - Aturan *Recto*: Setiap bab baru selalu dimulai di halaman ganjil (sebelah kanan).
5. **Hasil Nyata yang Telah Selesai Dikompilasi**:
   - **Buku 1 (Empati Sintetis - 10 Bab Lengkap)**:
     - Judul: *Empati Sintetis: Psikologi Bahasa AI, Jerat Manipulasi Kognitif, dan Kedaulatan Hukum Individu*
     - Total: **62 Halaman Buku Cetak ISO-B5** (~15.000 kata naskah revisi berbobot).
     - Berkas PDF: [`/root/journal/books/output/empati-sintetis-buku-cetak-print-ready.pdf`](file:///root/journal/books/output/empati-sintetis-buku-cetak-print-ready.pdf)
     - Direktori Cache Naskah: [`/root/journal/books/cache/empati-sintetis-buku-cetak/`](file:///root/journal/books/cache/empati-sintetis-buku-cetak/)
   - **Buku Uji Coba Awal (Rantai Dingin 3T - 2 Bab)**:
     - Total: **19 Halaman Buku Cetak ISO-B5** di `books/output/buku-panduan-tata-kelola-digital-rantai-dingin-3t-print-ready.pdf`.

---

## 🌐 Sumber API Buku Gratis (Telah Diverifikasi)

Mesin telah disiapkan untuk menarik referensi buku pembanding guna mencari celah pasar (*novelty gap*):
* **Crossref Monographs API**: Buku & monograf ilmiah penerbit dunia (Springer, CRC Press, Routledge 2024–2026).
* **Open Library API (Internet Archive)**: Jutaan buku dunia & buku teks nasional Indonesia (Pusat Perbukuan, Balai Pustaka).
* **OpenAlex Books API**: Buku akademik global beserta metrik sitasi internasional (`OPENALEX_API_KEY`).

---

## 💡 3 Konsep Buku Berdampak Tinggi (Siap Dieksekusi di Sesi Baru)

Tiga konsep buku lintas disiplin yang memadukan **Isu Internasional** dengan **Dimensi Personal (Hukum + Psikologi + Bahasa/Linguistik + AI)**:

### 1. Empati Sintetis (Synthetic Empathy) — *Paling Direkomendasikan*
* **Tema**: Analisis linguistik terhadap bahasa persuasif chatbot AI yang memanipulasi psikologi kognitif manusia, serta batas pertanggungjawaban hukum perdata/pidana (*cognitive liberty & consent*).
* **Judul**: *Synthetic Empathy: The Psychology of Language, Algorithmic Deception, and the Law of Cognitive Liberty*
* **Judul Indo**: *Empati Sintetis: Psikologi Bahasa AI, Jerat Manipulasi Kognitif, dan Kedaulatan Hukum Individu*

### 2. Hak untuk Sunyi (The Right to Disconnect)
* **Tema**: Psikologi kelelahan mental (*burnout*) di era kerja jarak jauh global, linguistik tekanan dalam komunikasi korporat digital, dan pengakuan yuridis hak asasi untuk tidak dapat dihubungi.
* **Judul**: *The Architecture of Digital Solitude: Mental Sovereignty, Workplace Linguistics, and the Right to Disconnect*

### 3. Linguistik Forensik & Pembuktian Niat
* **Tema**: Membedakan tulisan manusia vs teks sintetis AI dalam pembuktian hukum pengadilan, profiling psikologis, dan steganografi gaya bahasa (*stylometry*).
* **Judul**: *Words on Trial: Forensic Linguistics, Cognitive Profiling, and Evidence in the Algorithmic Age*

---

## 🚀 Perintah Cepat untuk Sesi Baru

Buka sesi baru, lalu cukup berikan instruksi kepada asisten:

```bash
# Perintah mengeksekusi pembuatan buku di sesi baru:
node /root/journal/scripts/generate-book.mjs \
  --title="Empati Sintetis: Psikologi Bahasa AI, Jerat Manipulasi Kognitif, dan Kedaulatan Hukum Individu" \
  --subtitle="Kajian Lintas Disiplin Linguistik Komputasional, Bias Psikologis, dan Kedaulatan Mental" \
  --chapters=10 \
  --author="Ilham Pradani" \
  --size="iso-b5"
```

Dokumen PDF buku utuh siap cetak puluhan bab akan langsung tercipta di `/root/journal/books/output/`.

