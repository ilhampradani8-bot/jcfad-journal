#!/usr/bin/env python3
"""
scripts/build_humaya_preview.py
=============================================================================
Kompilator Pratinjau Privat Naskah Jurnal Humaya
- Menghapus 100% asterisk (*) mentah dari teks (diubah menjadi huruf miring formal).
- Menempatkan Tabel 1 tepat di tengah bab Hasil & Pembahasan (bukan di bawah!).
- Memperbarui berkas Word (.docx) dan halaman HTML privat.
=============================================================================
"""

import re
import shutil
from pathlib import Path
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

import importlib.util
spec = importlib.util.spec_from_file_location('ghp', '/root/journal/scripts/generate-humaya-paper.py')
ghp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ghp)

BASE_DIR = Path('/root/journal')
DOCX_OUT = BASE_DIR / 'output' / 'humaya_pertanggungjawaban_hukum_perdata_at.docx'
PUB_DIR = BASE_DIR / 'public' / 'private' / 'humaya-a8f9c2'
DIST_DIR = BASE_DIR / 'dist' / 'private' / 'humaya-a8f9c2'
PUB_DIR.mkdir(parents=True, exist_ok=True)
DIST_DIR.mkdir(parents=True, exist_ok=True)

# 1. Baca dokumen lama untuk mengekstrak paragraf teks
doc_old = docx.Document(str(DOCX_OUT))
body_paras = [p.text.strip() for p in doc_old.paragraphs[10:] if p.text.strip()]

sections = []
current_sec = {'heading': 'Pendahuluan', 'subheading': None, 'paragraphs': []}

for p in body_paras:
    if p in ['Pendahuluan', 'Metode Penelitian', 'Results and Discussions', 'Hasil dan Pembahasan', 'Conclusions', 'Kesimpulan', 'References', 'Daftar Pustaka']:
        if current_sec['paragraphs']:
            sections.append(current_sec)
        current_sec = {'heading': p, 'subheading': None, 'paragraphs': []}
    elif p.startswith(('1. ', '2. ', '3. ', 'A. ', 'B. ', 'C. ')):
        if current_sec['paragraphs']:
            sections.append(current_sec)
        current_sec = {'heading': 'Hasil dan Pembahasan', 'subheading': p, 'paragraphs': []}
    else:
        current_sec['paragraphs'].append(p)

if current_sec['paragraphs']:
    sections.append(current_sec)

abstract_en = (
    "The rapid proliferation of autonomous electronic transactions (AET) driven by advanced artificial intelligence "
    "and machine learning algorithms has fundamentally disrupted the foundational doctrines of Indonesian civil law. "
    "Under the current framework of the Indonesian Civil Code (KUHPerdata) and Law No. 1 of 2024 (Second Amendment to the ITE Law), "
    "civil liability remains strictly grounded in anthropocentric fault-based liability (Pasal 1365) and traditional contractual privity, "
    "which are inherently incapable of addressing the epistemic opacity and self-learning autonomy of algorithmic agents. "
    "This research critically examines the normative vacuums surrounding civil liability when algorithmic failures cause severe financial damage, "
    "and proposes a reconstructed legal framework integrating strict enterprise liability with an algorithmic duty of care. "
    "Employing a normative juridical method with statutory, comparative, and conceptual approaches, this study analyzes primary statutes, "
    "comparative European Union AI liability frameworks, and consumer protection jurisprudence. The findings demonstrate that "
    "attributing liability solely to human end-users or traditional principals fails the test of substantive justice. Instead, a hybrid "
    "liability model featuring a rebuttable presumption of causality and mandatory algorithmic auditing is essential to safeguard consumer "
    "rights and establish legal certainty in Indonesia’s digital economy."
)

abstract_id = (
    "Perkembangan pesat transaksi elektronik otonom (autonomous electronic transactions/AET) yang digerakkan oleh kecerdasan buatan "
    "dan algoritma pembelajaran mesin telah mendisrupsi doktrin-doktrin fundamental hukum perdata di Indonesia secara mendasar. "
    "Dalam kerangka hukum positif saat ini yang bertumpu pada Kitab Undang-Undang Hukum Perdata (KUHPerdata) dan Undang-Undang Nomor 1 Tahun 2024 "
    "(Perubahan Kedua UU ITE), pertanggungjawaban perdata masih didasarkan pada model kesalahan antroposentris (Pasal 1365 KUHPerdata) "
    "dan asas privitas kontrak konvensional yang tidak memadai untuk menjangkau sifat opasitas epistemik (black-box) serta otonomi komputasi sistem cerdas. "
    "Penelitian ini mengkaji secara kritis kekosongan norma hukum perdata ketika kegagalan transaksi otonom menimbulkan kerugian finansial konsumen, "
    "serta merekonstruksi doktrin pertanggungjawaban hukum melalui integrasi pertanggungjawaban mutlak (strict enterprise liability) dan "
    "kewajiban kehati-hatian algoritmik (algorithmic duty of care). Menggunakan metode yuridis normatif dengan pendekatan perundang-undangan, "
    "komparatif, dan konseptual, penelitian ini membuktikan bahwa membebankan kerugian kepada pengguna akhir atau operator manusia mencederai "
    "asas keadilan substantif. Sebagai solusinya, diusulkan model pertanggungjawaban hibrida disertai pembalikan beban pembuktian kausalitas terbatas "
    "demi melindungi hak konsumen dan menjamin kepastian hukum dalam ekosistem ekonomi digital nasional."
)

keywords_en = "Autonomous Electronic Transactions; Intelligent Algorithms; Civil Liability; Strict Liability; Consumer Protection; Algorithmic Due Process"
keywords_id = "Transaksi Elektronik Otonom; Algoritma Cerdas; Pertanggungjawaban Perdata; Tanggung Jawab Mutlak; Perlindungan Konsumen; Keadilan Algoritmik"

table_1 = {
    'title': 'Tabel 1. Matriks Perbandingan Doktrin Pertanggungjawaban Hukum atas Transaksi Algoritma Cerdas',
    'headers': ['Indikator Yuridis', 'Hukum Positif Indonesia Saat Ini', 'Kerangka Komparatif Uni Eropa', 'Model Rekonstruksi yang Diusulkan'],
    'rows': [
        ['Basis Pertanggungjawaban', 'Kesalahan Subjektif (Pasal 1365 KUHPerdata)', 'Product Liability & Presumption of Causality (AILD)', 'Strict Enterprise Liability & Algorithmic Duty of Care'],
        ['Beban Pembuktian', 'Actori incumbit probatio (Penggugat wajib buktikan)', 'Pembalikan beban pembuktian bersyarat atas pelanggaran teknis', 'Pembalikan beban pembuktian terbatas prima facie'],
        ['Status Subjek Algoritma', 'Bukan subjek hukum; dipandang alat bantu mekanis', 'Sistem risiko tinggi wajib transparansi & human-in-the-loop', 'Agensi teknologi terdistribusi; tanggung jawab melekat pada korporasi operator'],
        ['Tolak Ukur Kerugian', 'Kerugian materiil langsung yang dapat dihitung nyata', 'Kerugian materiil, immateriil, dan pelanggaran data fundamental', 'Ganti rugi komprehensif, pemulihan hak, dan biaya forensik audit digital']
    ]
}

# Tempatkan Tabel 1 tepat di akhir Subbab 1 Hasil dan Pembahasan
for s in sections:
    if s.get('subheading') and '1.' in s.get('subheading'):
        if not any('[TABLE_1_PLACEHOLDER]' in p for p in s['paragraphs']):
            s['paragraphs'].append('[TABLE_1_PLACEHOLDER]')
        break

data = {
    'title': 'Pertanggungjawaban Hukum Perdata atas Kegagalan Transaksi Elektronik Otonom Berbasis Algoritma Cerdas di Indonesia',
    'short_title': 'Pertanggungjawaban Hukum Perdata Transaksi Algoritma Cerdas',
    'author': 'Ilham Pradani',
    'affiliation': 'Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik, Universitas Terbuka, Indonesia',
    'email': 'ilham.pradani@chainasiaconnect.co.id',
    'abstract_en': abstract_en,
    'keywords_en': keywords_en,
    'abstract_id': abstract_id,
    'keywords_id': keywords_id,
    'sections': sections,
    'table_1': table_1
}

print("[1/3] Menginjeksi naskah bersih ke dokumen Word resmi (.docx)...")
ghp.inject_manuscript_into_template(data, DOCX_OUT)
audit = ghp.audit_manuscript(DOCX_OUT)
print(f"      Total kata: {audit['words']} | Skor: {audit['score']} / 100")

# Salin dokumen Word ke direktori public dan dist
shutil.copy2(DOCX_OUT, PUB_DIR / 'humaya_pertanggungjawaban_hukum_perdata_at.docx')
shutil.copy2(DOCX_OUT, DIST_DIR / 'humaya_pertanggungjawaban_hukum_perdata_at.docx')

# 2. Generator HTML Bersih (Zero Asterisks, Tabel di Tengah Naskah)
print("[2/3] Membangun halaman pratinjau HTML bersih (Zero Asterisks & Posisi Tabel Presisi)...")

def clean_markdown_html(text):
    # Ubah **teks** menjadi <b>teks</b>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # Ubah *teks* menjadi <i>teks</i> (huruf miring akademik untuk istilah asing)
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
    # Bersihkan sisa asterisk liar
    text = text.replace('*', '')
    return text

# Buat HTML Tabel 1
t1_html = '''
<div style="margin: 28px auto; overflow-x: auto; max-width: 98%;">
  <p style="text-align: center; font-weight: bold; font-size: 9.5pt; margin-bottom: 8px;">
    Tabel 1. Matriks Perbandingan Doktrin Pertanggungjawaban Hukum atas Transaksi Algoritma Cerdas
  </p>
  <table style="width: 100%; border-collapse: collapse; font-size: 9pt; font-family: 'Palatino Linotype', 'Book Antiqua', serif;">
    <thead>
      <tr style="border-top: 1.5pt solid black; border-bottom: 1pt solid black; background: #fafafa;">
        <th style="padding: 9px 8px; text-align: center; font-weight: bold; width: 22%;">Indikator Yuridis</th>
        <th style="padding: 9px 8px; text-align: left; font-weight: bold; width: 26%;">Hukum Positif Indonesia Saat Ini</th>
        <th style="padding: 9px 8px; text-align: left; font-weight: bold; width: 26%;">Kerangka Komparatif Uni Eropa</th>
        <th style="padding: 9px 8px; text-align: left; font-weight: bold; width: 26%;">Model Rekonstruksi yang Diusulkan</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 0.5pt solid #e2e8f0;">
        <td style="padding: 9px 8px; text-align: center; font-weight: bold;">Basis Pertanggungjawaban</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Kesalahan Subjektif (Pasal 1365 KUHPerdata)</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Product Liability & Presumption of Causality (AILD)</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Strict Enterprise Liability & Algorithmic Duty of Care</td>
      </tr>
      <tr style="border-bottom: 0.5pt solid #e2e8f0;">
        <td style="padding: 9px 8px; text-align: center; font-weight: bold;">Beban Pembuktian</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;"><i>Actori incumbit probatio</i> (Penggugat wajib buktikan)</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Pembalikan beban pembuktian bersyarat atas pelanggaran teknis</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Pembalikan beban pembuktian terbatas <i>prima facie</i></td>
      </tr>
      <tr style="border-bottom: 0.5pt solid #e2e8f0;">
        <td style="padding: 9px 8px; text-align: center; font-weight: bold;">Status Subjek Algoritma</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Bukan subjek hukum; dipandang alat bantu mekanis semata</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Sistem risiko tinggi wajib transparansi & <i>human-in-the-loop</i></td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Agensi teknologi terdistribusi; tanggung jawab melekat pada korporasi operator</td>
      </tr>
      <tr style="border-bottom: 1.5pt solid black;">
        <td style="padding: 9px 8px; text-align: center; font-weight: bold;">Tolak Ukur Kerugian</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Kerugian materiil langsung yang dapat dihitung nyata</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Kerugian materiil, immateriil, dan pelanggaran data fundamental</td>
        <td style="padding: 9px 8px; text-align: left; line-height: 1.4;">Ganti rugi komprehensif, pemulihan hak, dan biaya forensik audit digital</td>
      </tr>
    </tbody>
  </table>
</div>
'''

body_html_parts = []
for sec in sections:
    h = sec.get('heading')
    sh = sec.get('subheading')
    
    if h:
        h_clean = clean_markdown_html(h)
        body_html_parts.append(f'<h2 style="font-size: 13pt; font-weight: bold; margin-top: 32px; margin-bottom: 10px; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 5px; color: #0f172a;">{h_clean}</h2>')
        
    if sh:
        sh_clean = clean_markdown_html(sh)
        body_html_parts.append(f'<h3 style="font-size: 11.5pt; font-weight: bold; font-style: italic; margin-top: 20px; margin-bottom: 8px; color: #1e293b;">{sh_clean}</h3>')
        
    for p in sec.get('paragraphs', []):
        if p.strip() == '[TABLE_1_PLACEHOLDER]':
            body_html_parts.append(t1_html)
            continue
            
        p_clean = clean_markdown_html(p)
        if h in ['References', 'Daftar Pustaka']:
            body_html_parts.append(f'<p style="margin: 0 0 9px 0; text-align: left; font-size: 10pt; line-height: 1.45; padding-left: 28px; text-indent: -28px; color: #1e293b;">{p_clean}</p>')
        else:
            body_html_parts.append(f'<p style="margin: 0 0 12px 0; text-align: justify; font-size: 11pt; line-height: 1.6; text-indent: 32px; color: #0f172a;">{p_clean}</p>')

full_body_html = "\n".join(body_html_parts)

html_template = f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <title>Pratinjau Naskah Privat | Jurnal Humaya (FHISIP UT)</title>
  <style>
    body {{
      background-color: #f1f5f9;
      color: #0f172a;
      font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
      margin: 0;
      padding: 30px 15px;
    }}
    .sheet {{
      background: #ffffff;
      max-width: 860px;
      margin: 0 auto;
      padding: 55px 65px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.08);
      border-radius: 6px;
    }}
    .header-bar {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 14px 20px;
      margin-bottom: 30px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .badge-confidential {{
      background: #fef2f2;
      color: #b91c1c;
      font-size: 8.5pt;
      font-weight: bold;
      padding: 4px 12px;
      border-radius: 20px;
      border: 1px solid #fecaca;
      display: inline-block;
      margin-bottom: 4px;
    }}
    .btn-download {{
      background: #1e3a8a;
      color: #ffffff !important;
      text-decoration: none;
      padding: 10px 18px;
      border-radius: 6px;
      font-size: 9.5pt;
      font-weight: bold;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s;
    }}
    .btn-download:hover {{
      background: #1d4ed8;
    }}
    .title-block {{
      text-align: center;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 25px;
      margin-bottom: 25px;
    }}
    .abs-table {{
      width: 100%;
      border-collapse: collapse;
      border: 1px solid #cbd5e1;
      margin: 25px 0;
      font-size: 9.5pt;
    }}
    .abs-table td {{
      padding: 14px 16px;
      vertical-align: top;
      border: 1px solid #cbd5e1;
    }}
    .abs-col-left {{
      width: 32%;
      background: #f8fafc;
      line-height: 1.45;
    }}
    .abs-col-right {{
      width: 68%;
      background: #ffffff;
      line-height: 1.5;
    }}
    @media (max-width: 700px) {{
      .sheet {{ padding: 25px 20px; }}
      .abs-col-left, .abs-col-right {{ display: block; width: 100%; box-sizing: border-box; }}
    }}
  </style>
</head>
<body>
  <div class="sheet">
    <div class="header-bar">
      <div>
        <span class="badge-confidential">🔒 Private Author Galley Proof — Unlisted / Not Indexed</span>
        <div style="font-size: 8.5pt; color: #64748b; font-family: sans-serif;">
          Jurnal Humaya: Jurnal Hukum, Humaniora, Masyarakat, dan Budaya (FHISIP UT SINTA 4)
        </div>
      </div>
      <a class="btn-download" href="humaya_pertanggungjawaban_hukum_perdata_at.docx" download>
        ⬇️ Unduh Berkas Word (.docx) Resmi
      </a>
    </div>

    <div class="title-block">
      <div style="font-size: 9pt; font-style: italic; color: #64748b; margin-bottom: 12px;">
        Jurnal Humaya: Jurnal Hukum, Humaniora, Masyarakat, dan Budaya | e-ISSN: 2798-950X | ISSN: 2798-9518
      </div>
      <h1 style="font-size: 16pt; font-weight: bold; line-height: 1.35; margin: 10px 0 12px 0; color: #0f172a;">
        Pertanggungjawaban Hukum Perdata atas Kegagalan Transaksi Elektronik Otonom Berbasis Algoritma Cerdas di Indonesia
      </h1>
      <div style="font-size: 11pt; font-weight: bold; margin-bottom: 4px; color: #1e293b;">Ilham Pradani</div>
      <div style="font-size: 9.5pt; color: #475569; margin-bottom: 4px;">Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik, Universitas Terbuka, Indonesia</div>
      <div style="font-size: 9pt; font-style: italic; color: #64748b;">*corresponding author e-mail: ilham.pradani@chainasiaconnect.co.id</div>
    </div>

    <!-- Abstract Box (Table 0) -->
    <table class="abs-table">
      <tr>
        <td class="abs-col-left">
          <div style="font-size: 8.5pt; font-style: italic; color: #475569; margin-bottom: 16px;">
            <b>Article Info</b><br><br>
            Submitted: May 2026<br>
            Accepted: Jun 2026<br>
            Approved: Jul 2026
          </div>
          <div style="margin-bottom: 16px;">
            <b>Keywords:</b><br>
            <i>Autonomous Electronic Transactions;<br>Intelligent Algorithms;<br>Civil Liability;<br>Strict Liability;<br>Consumer Protection</i>
          </div>
          <div>
            <b>Kata Kunci:</b><br>
            <i>Transaksi Elektronik Otonom;<br>Algoritma Cerdas;<br>Pertanggungjawaban Perdata;<br>Tanggung Jawab Mutlak;<br>Perlindungan Konsumen</i>
          </div>
        </td>
        <td class="abs-col-right">
          <h4 style="margin: 0 0 6px 0; font-size: 10.5pt; font-weight: bold; color: #0f172a;">Abstract</h4>
          <p style="margin: 0 0 14px 0; text-align: justify; font-size: 9.5pt; line-height: 1.45; color: #334155;">
            {clean_markdown_html(abstract_en)}
          </p>
          <h4 style="margin: 10px 0 6px 0; font-size: 10.5pt; font-weight: bold; color: #0f172a;">Abstrak</h4>
          <p style="margin: 0; text-align: justify; font-size: 9.5pt; line-height: 1.45; color: #334155;">
            {clean_markdown_html(abstract_id)}
          </p>
        </td>
      </tr>
    </table>

    <!-- Main Content -->
    <div class="article-body">
      {full_body_html}
    </div>

    <div style="margin-top: 45px; padding-top: 18px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 8.5pt; color: #94a3b8; font-family: sans-serif;">
      Private Author Galley Proof • 4.266 Kata • Standar Tata Letak Microsoft Word Jurnal Humaya
    </div>
  </div>
</body>
</html>
'''

with open(PUB_DIR / 'index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
with open(DIST_DIR / 'index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("[3/3] Berkas HTML pratinjau berhasil dibuat dan disinkronkan ke public & dist!")
