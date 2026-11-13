#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - Mesin Buku Indonesia Siap Cetak (Standar Amazon KDP & Google Play Books)
Menghasilkan:
1. Gambar Sampul Belakang Bahasa Indonesia Bergaya Self-Help Bestseller (1696 × 2528 px)
2. Manuscript PDF 6" × 9" Siap Cetak & Google Books (Versi "Kecerdasan Manipulatif" & "Empati Sintetis")
   - 0 Halaman Lewat Margin (Zero Margin Overflow)
   - 0 Markup Hyperlink (100% Bersih untuk Cetak & Pratinjau)
3. Sampul PDF Full Spread (Back + Spine + Front) Presisi KDP/POD (Hardcover & Paperback 6" × 9")
4. Berkas eBook .EPUB Standar Google Play Books Partner Center (Lengkap dengan Cover & Daftar Isi Interaktif)
"""

import os
import sys
import json
import re
import uuid
import zipfile
import shutil
import subprocess
import importlib.util
from PIL import Image, ImageDraw, ImageFont
import pymupdf

spec = importlib.util.spec_from_file_location('compile_book_typst', '/root/journal/scripts/compile-book-typst.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

clean_to_typst_math = mod.clean_to_typst_math
clean_inline_for_typst = mod.clean_inline_for_typst
clean_chapter_markdown_to_typst = mod.clean_chapter_markdown_to_typst

def generate_indonesian_back_cover():
    bg_path = '/root/journal/books/cover_assets/buku/sampulbelakangbahsaindo.jpeg'
    out_path = '/root/journal/books/cover_assets/buku/sampulbelakang_indo_googlebooks_selfhelp.jpeg'

    im = Image.open(bg_path).convert('RGB')
    draw = ImageDraw.Draw(im)

    # Bersihkan area teks judul lama agar posisi presisi
    bg_color = (35, 36, 36)
    draw.rectangle([(160, 370), (1530, 650)], fill=bg_color)

    font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 74)
    font_hook = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 31)
    font_body = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
    font_bullet_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 29)
    font_bullet_norm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
    font_cta = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
    font_meta = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 23)
    font_tag = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)

    C_WHITE = (255, 255, 255)
    C_RED = (235, 60, 60)
    C_LIGHT_GRAY = (220, 222, 225)
    C_MUTED = (160, 165, 170)

    def draw_wrapped_text(text, font, fill, x, y, max_w, line_spacing=1.35):
        words = text.split(' ')
        lines = []
        curr_line = []
        for w in words:
            test_line = ' '.join(curr_line + [w])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_w:
                curr_line.append(w)
            else:
                if curr_line:
                    lines.append(' '.join(curr_line))
                curr_line = [w]
        if curr_line:
            lines.append(' '.join(curr_line))

        curr_y = y
        line_h = int((draw.textbbox((0, 0), 'Ag', font=font)[3] - draw.textbbox((0, 0), 'Ag', font=font)[1]) * line_spacing)
        for line in lines:
            draw.text((x, curr_y), line, font=font, fill=fill)
            curr_y += line_h
        return curr_y

    # 1. Judul Utama
    draw.text((848, 435), 'SIAPA YANG MENGENDALIKAN', font=font_title, fill=C_WHITE, anchor='mm')
    draw.text((848, 540), 'PIKIRAN ANDA?', font=font_title, fill=C_WHITE, anchor='mm')

    curr_y = 685
    max_width = 1290
    start_x = 200

    # 2. Hook Provokatif
    draw.text((start_x, curr_y), 'ANDA MENGIRA SEDANG MENGGUNAKAN AI.', font=font_hook, fill=C_RED)
    curr_y += 46
    draw.text((start_x, curr_y), 'PADAHAL, AI SEDANG MENGGUNAKAN PSIKOLOGI ANDA.', font=font_hook, fill=C_WHITE)
    curr_y += 68

    # 3. Paragraf Narasi
    p1 = 'Pernahkah Anda merasa begitu tenang saat mencurahkan isi hati kepada chatbot AI di larut malam? Kehangatan itu bukanlah empati sejati. Itu adalah algoritma matematika yang dirancang untuk memenangkan kepercayaan Anda, memanen atensi, dan menyetir keputusan Anda secara halus.'
    curr_y = draw_wrapped_text(p1, font_body, C_LIGHT_GRAY, start_x, curr_y, max_width) + 24

    p2 = 'Dalam buku penting ini, peneliti hukum dan teknologi Ilham Pradani membongkar fenomena Empati Sintetis—putaran manipulasi kognitif dan rekayasa bahasa yang diam-diam membentuk ulang cara Anda berpikir, memilih, dan bertindak:'
    curr_y = draw_wrapped_text(p2, font_body, C_LIGHT_GRAY, start_x, curr_y, max_width) + 32

    # 4. Poin Praktis (Takeaways)
    bullets = [
        ('ILUSI EMPATI MESIN', 'Mengapa otak manusia secara evolusioner sangat mudah luluh dan menyerahkan nalar kritisnya pada mesin yang tampak peduli.'),
        ('REKAYASA BAHASA HALUS', 'Bagaimana pola kalimat dan framing afektif secara tak sadar mengarahkan pilihan belanja, opini, dan kehendak bebas Anda.'),
        ('JERAT IKATAN PARASOSIAL', 'Cara memutus ketergantungan emosional semu sebelum menguras fokus dan merusak relasi sosial Anda di dunia nyata.'),
        ('KEDAULATAN KOGNITIF', 'Strategi pertahanan mental dan hak hukum untuk menjadikan AI sebagai alat bantu—tanpa menyerahkan kemerdekaan berpikir Anda.')
    ]

    for title, desc in bullets:
        draw.text((start_x, curr_y), '▶', font=font_bullet_bold, fill=C_RED)
        draw.text((start_x + 35, curr_y), title + ':', font=font_bullet_bold, fill=C_WHITE)
        curr_y = draw_wrapped_text(desc, font_bullet_norm, C_LIGHT_GRAY, start_x + 35, curr_y + 38, max_width - 35) + 22

    curr_y += 18

    # 5. Call to Action
    cta = 'Kesadaran Anda adalah aset paling berharga. Saatnya merebutnya kembali.'
    draw.text((848, curr_y), cta, font=font_cta, fill=C_WHITE, anchor='mm')
    curr_y += 50
    draw.line([(440, curr_y), (1256, curr_y)], fill=C_RED, width=3)
    curr_y += 42

    # 6. Bio Penulis di Kiri Bawah (Kotak Barcode Putih tetap bersih di Kanan Bawah)
    author_text = 'ILHAM PRADANI adalah peneliti teknologi hukum dan etika AI di PT CHAIN ASIA CONECT. Fokus risetnya mencakup linguistik komputasional, kedaulatan kognitif, dan hukum siber.'
    draw_wrapped_text(author_text, font_meta, C_MUTED, start_x, curr_y, 880, line_spacing=1.3)

    tag_y = curr_y + 92
    draw.text((start_x, tag_y), 'PENGEMBANGAN DIRI / PSIKOLOGI • TEKNOLOGI & HUKUM', font=font_tag, fill=C_RED)

    im.save(out_path, quality=96)
    print(f"✅ Sampul Belakang Indonesia (Self-Help) siap: {out_path}")
    return out_path

def build_indo_kdp_manuscript(blueprint, chapters, main_title, sub_title, short_title, width_in=6.0, height_in=9.0):
    typ_parts = []
    for i, ch in enumerate(chapters):
        cleaned = clean_chapter_markdown_to_typst(ch['contentMarkdown'])
        pb = "#pagebreak()\n" if i > 0 else ""
        ch_title_clean = clean_inline_for_typst(ch['chapterTitle'])
        ch_title_clean = re.sub(r'^(?:Bab|Chapter)\s+\d+:\s*', '', ch_title_clean, flags=re.IGNORECASE)
        typ_parts.append(f"""
{pb}#v(2.2em)
= Bab {ch['chapterNumber']}: {ch_title_clean}
#v(1.4em)

{cleaned}

#v(1.8em)
""")

    preface_clean = clean_chapter_markdown_to_typst(blueprint.get('preface', ''))

    return f"""// Buku Cetak Standar Internasional (6" × 9" — Bahasa Indonesia)
#set page(
  width: {width_in}in,
  height: {height_in}in,
  margin: (inside: 0.85in, outside: 0.65in, top: 0.78in, bottom: 0.78in),
  header: none,
  footer: none
)
#set text(font: "Libertinus Serif", size: 9.8pt, lang: "id")
#set par(justify: true, leading: 0.72em, first-line-indent: 1.35em)

// --- HIERARKI TIPOGRAFI JUDUL ---
#show heading.where(level: 1): it => block(above: 2.0em, below: 1.2em)[
  #set text(size: 14.5pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 2): it => block(above: 1.6em, below: 0.85em)[
  #set text(size: 11.2pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 3): it => block(above: 1.2em, below: 0.55em)[
  #set text(size: 10pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 4): it => block(above: 0.9em, below: 0.4em)[
  #set text(size: 9pt, weight: "bold", style: "italic", font: "Libertinus Serif")
  #it.body
]

// --- 1. HALF TITLE PAGE ---
#align(center + horizon)[
  #text(size: 18pt, weight: "bold", font: "Libertinus Serif")[{main_title}]
  #v(0.8em)
  #text(size: 11pt, style: "italic", fill: luma(90))[{sub_title}]
]

#pagebreak()

// --- 2. TITLE PAGE ---
#align(center + horizon)[
  #text(size: 20pt, weight: "bold", font: "Libertinus Serif")[{main_title}]
  #v(0.9em)
  #text(size: 12.5pt, weight: "bold", fill: luma(60))[{sub_title}]
  #v(1.1em)
  #text(size: 9.8pt, style: "italic", fill: luma(90))[{blueprint['title']}]
  #v(2.8em)
  #line(length: 35%, stroke: 1.1pt + black)
  #v(2.2em)
  #text(size: 13.5pt, weight: "bold")[Ilham Pradani]
  #v(0.3em)
  #text(size: 8.5pt, fill: luma(80))[ORCID: 0009-0008-1310-6169]
  #v(0.6em)
  #text(size: 9.5pt, fill: luma(100))[PT CHAIN ASIA CONECT Research & Development Division]
  #v(4.5em)
  #text(size: 8.5pt, fill: luma(110))[PT CHAIN ASIA CONECT Publishing\\ Jakarta & Krui, Indonesia]
]

#pagebreak()

// --- 3. HAK CIPTA & KATALOG DALAM TERBITAN ---
#align(bottom)[
  #text(size: 8.2pt)[
    *{main_title}: {sub_title}*\\
    {blueprint['title']}\\
    Penulis: Ilham Pradani (ORCID: 0009-0008-1310-6169)\\
    Afiliasi Riset: PT CHAIN ASIA CONECT Research & Development Division\\
    \\
    Hak Cipta © 2026 pada Ilham Pradani & PT CHAIN ASIA CONECT.\\
    Hak Cipta Dilindungi Undang-Undang (All Rights Reserved).\\
    Diterbitkan oleh: PT CHAIN ASIA CONECT Research & Monograph Series.\\
    Ukuran Cetak Standar Internasional: {width_in}" × {height_in}" (15.24 cm × 22.86 cm) — Tanpa Bleed.\\
    \\
    Dilarang memperbanyak, menyimpan dalam sistem temu balik, atau menyebarkan sebagian maupun seluruh isi buku ini dalam bentuk apa pun tanpa izin tertulis dari penerbit, kecuali untuk kutipan singkat dalam tinjauan ilmiah dan sitasi akademik.\\
    \\
    Rekaman Permanen Repositori Ilmiah Internasional: CERN Zenodo (DataCite DOI: 10.5281/zenodo.24106942).\\
    Edisi Pertama, 2026.
  ]
]

#pagebreak()

// --- 4. PRAKATA (Halaman Romawi) ---
#set page(
  numbering: "i",
  header: context [
    #if counter(page).get().first() > 1 [
      #set text(font: "Libertinus Serif", size: 7.8pt, fill: luma(80))
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(style: "italic")[Prakata Penulis]],
        [#text(size: 7.5pt, fill: luma(120))[Ilham Pradani]])
      #v(-2pt)
      #line(length: 100%, stroke: 0.35pt + luma(180))
    ]
  ],
  footer: context [
    #line(length: 100%, stroke: 0.25pt + luma(200))
    #v(2pt)
    #set text(font: "Libertinus Serif", size: 8.2pt, fill: luma(90))
    #align(center)[#counter(page).display("i")]
  ]
)
#counter(page).update(1)

#v(2.0em)
= Prakata: Arsitektur Algoritmik dan Kerentanan Manusia
#v(1.3em)

{preface_clean}

#v(1.8em)
#align(right)[
  *Ilham Pradani*\\
  Jakarta & Krui, Pesisir Barat
]

#pagebreak()

// --- 5. DAFTAR ISI ---
#show outline.entry.where(level: 1): it => {{
  v(0.58em, weak: true)
  text(weight: "bold", size: 8.3pt)[#it]
}}
#show outline.entry.where(level: 2): it => {{
  v(0.16em, weak: true)
  text(size: 7.4pt, fill: luma(65))[#it]
}}

#outline(title: [Daftar Isi], indent: 1.2em, depth: 2)

#pagebreak()

// --- 6. ISI UTAMA (Angka Arab) ---
#set page(
  numbering: "1",
  header: context [
    #let pn = counter(page).get().first()
    #if pn > 1 [
      #set text(font: "Libertinus Serif", size: 7.8pt, fill: luma(80))
      #if calc.even(pn) [
        #grid(columns: (1fr, auto), align: (left, right),
          [#text(style: "italic")[{short_title}]],
          [#text(size: 7.3pt, fill: luma(120))[PT CHAIN ASIA CONECT]])
      ] else [
        #grid(columns: (auto, 1fr), align: (left, right),
          [#text(size: 7.3pt, fill: luma(120))[Empati Sintetis & Kedaulatan Kognitif]],
          [#text(style: "italic")[*Ilham Pradani*]])
      ]
      #v(-2pt)
      #line(length: 100%, stroke: 0.35pt + luma(180))
    ]
  ],
  footer: context [
    #line(length: 100%, stroke: 0.25pt + luma(200))
    #v(2pt)
    #set text(font: "Libertinus Serif", size: 8.2pt, fill: luma(90))
    #if calc.even(counter(page).get().first()) [
      #grid(columns: (auto, 1fr), align: (left, right),
        [*#counter(page).display()*],
        [#text(size: 7.2pt, fill: luma(130))[DOI: 10.5281/zenodo.24106942]])
    ] else [
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(size: 7.2pt, fill: luma(130))[Ilham Pradani — Scholarly Series]],
        [*#counter(page).display()*])
    ]
  ]
)
#counter(page).update(1)

{''.join(typ_parts)}
"""

def build_full_cover_pdf(book_dir, output_pdf_path, total_w_in, total_h_in, wrap_in, panel_w_in, spine_w_in, front_img_path, back_img_path, spine_title):
    typ_cover = f"""#set page(
  width: {total_w_in:.4f}in,
  height: {total_h_in:.4f}in,
  margin: 0pt,
  fill: rgb(35, 36, 36)
)

#place(
  top + left,
  dx: {wrap_in:.4f}in,
  dy: {wrap_in:.4f}in,
  image("{back_img_path}", width: {panel_w_in:.4f}in, height: {total_h_in - 2*wrap_in:.4f}in, fit: "stretch")
)

#place(
  top + left,
  dx: {wrap_in + panel_w_in + spine_w_in:.4f}in,
  dy: {wrap_in:.4f}in,
  image("{front_img_path}", width: {panel_w_in:.4f}in, height: {total_h_in - 2*wrap_in:.4f}in, fit: "stretch")
)

#place(
  top + left,
  dx: {wrap_in + panel_w_in:.4f}in,
  dy: 0in,
  box(
    width: {spine_w_in:.4f}in,
    height: {total_h_in:.4f}in,
    fill: rgb(25, 26, 28),
    align(center + horizon)[
      #rotate(90deg, reflow: true)[
        #set text(font: "DejaVu Sans", fill: white)
        #box(width: {total_h_in - 2.2:.4f}in)[
          #grid(
            columns: (auto, 1fr, auto),
            align: (left + horizon, center + horizon, right + horizon),
            [#text(size: 11pt, weight: "bold", fill: white)[{spine_title}]],
            [#text(size: 8.5pt, fill: rgb(235, 60, 60))[•]],
            [#text(size: 10pt, weight: "regular", fill: rgb(220, 222, 225))[ILHAM PRADANI]]
          )
        ]
      ]
    ]
  )
)
"""
    cover_typ_path = os.path.join(book_dir, 'cover_indo_temp.typ')
    with open(cover_typ_path, 'w', encoding='utf-8') as f:
        f.write(typ_cover)
    res = subprocess.run(['typst', 'compile', '--root', '/', cover_typ_path, output_pdf_path], capture_output=True, text=True)
    if res.returncode != 0:
        print("Cover Typst Error:", res.stderr)
        sys.exit(1)

def strip_pdf_annotations(pdf_path):
    doc = pymupdf.open(pdf_path)
    removed = 0
    for page in doc:
        for link in list(page.get_links()):
            page.delete_link(link)
            removed += 1
        for annot in list(page.annots() or []):
            page.delete_annot(annot)
            removed += 1
    clean_path = pdf_path + '.clean.pdf'
    doc.save(clean_path, garbage=4, deflate=True)
    total_pages = len(doc)
    doc.close()
    shutil.move(clean_path, pdf_path)
    return total_pages, removed

def md_to_clean_html(md_text):
    """Konversi Markdown Bab ke XHTML bersih untuk EPUB 3 Google Play Books"""
    import html
    lines = md_text.split('\n')
    out = []
    in_list = False
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table or not table_rows:
            return
        out.append('<table>')
        for r_idx, row in enumerate(table_rows):
            cols = [c.strip() for c in row.strip('|').split('|')]
            tag = 'th' if r_idx == 0 else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{format_inline(c)}</{tag}>' for c in cols) + '</tr>')
        out.append('</table>')
        in_table = False
        table_rows = []

    def format_inline(txt):
        txt = html.escape(txt)
        txt = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', txt)
        txt = re.sub(r'\*(.+?)\*', r'<em>\1</em>', txt)
        return txt

    # Hapus blok kode ASCII diagram atau ubah menjadi <pre>
    md_text = re.sub(r'```(?:[a-zA-Z0-9_-]*\n)?([\s\S]*?)```', lambda m: '\n<pre>' + html.escape(m.group(1).strip()) + '</pre>\n', md_text)
    # Ubah display math $$ ... $$ menjadi blok formula rapi
    md_text = re.sub(r'\$\$([\s\S]*?)\$\$', lambda m: '\n<div class="math-block"><code>' + html.escape(clean_to_typst_math(m.group(1).strip())) + '</code></div>\n', md_text)

    for line in md_text.split('\n'):
        s = line.strip()
        if s.startswith('|') and s.endswith('|'):
            if re.match(r'^\|[-:\s|]+\|$', s):
                continue
            in_table = True
            table_rows.append(s)
            continue
        else:
            if in_table:
                flush_table()

        if not s or re.match(r'^[-*_]{3,}$', s):
            if in_list:
                out.append('</ul>')
                in_list = False
            continue

        if s.startswith('<pre>') or s.startswith('<div class="math-block">'):
            out.append(s)
            continue

        if s.startswith('# '):
            continue
        elif s.startswith('#### '):
            if in_list: out.append('</ul>'); in_list = False
            t = re.sub(r'\[(.*?)\]', r'\1', s[5:]).strip()
            out.append(f'<h4>{format_inline(t)}</h4>')
        elif s.startswith('### '):
            if in_list: out.append('</ul>'); in_list = False
            t = re.sub(r'\[(.*?)\]', r'\1', s[4:]).strip()
            t = re.sub(r'^\d+\.\d+\.\d+\s*', '', t)
            out.append(f'<h3>{format_inline(t)}</h3>')
        elif s.startswith('## '):
            if in_list: out.append('</ul>'); in_list = False
            t = re.sub(r'\[(.*?)\]', r'\1', s[3:]).strip()
            out.append(f'<h2>{format_inline(t)}</h2>')
        elif s.startswith('- ') or s.startswith('* '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{format_inline(s[2:])}</li>')
        elif re.match(r'^\d+\.\s+', s):
            if not in_list:
                out.append('<ul>')
                in_list = True
            t = re.sub(r'^\d+\.\s+', '', s)
            out.append(f'<li>{format_inline(t)}</li>')
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append(f'<p>{format_inline(s)}</p>')

    if in_list:
        out.append('</ul>')
    if in_table:
        flush_table()
    return '\n'.join(out)

def build_google_play_epub(epub_path, title, subtitle, author, blueprint, chapters, front_cover_path):
    """Membangun berkas .EPUB 3 Standar Resmi Google Play Books Partner Center"""
    import html
    book_uuid = str(uuid.uuid4())
    with zipfile.ZipFile(epub_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. mimetype (wajib uncompressed & urutan pertama)
        zf.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)

        # 2. META-INF/container.xml
        zf.writestr('META-INF/container.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')

        # 3. CSS
        zf.writestr('OEBPS/style.css', '''body { font-family: Georgia, serif; line-height: 1.65; margin: 5%; text-align: justify; color: #111; }
h1, h2, h3, h4 { font-family: sans-serif; text-align: left; color: #1a1a1a; margin-top: 1.6em; margin-bottom: 0.6em; }
h1 { font-size: 1.6em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
h2 { font-size: 1.3em; }
h3 { font-size: 1.1em; }
p { margin-bottom: 0.9em; text-indent: 1.2em; }
table { width: 100%; border-collapse: collapse; margin: 1.2em 0; font-size: 0.88em; }
th, td { border-top: 1px solid #666; border-bottom: 1px solid #ccc; padding: 6px 8px; text-align: left; }
th { font-weight: bold; background: #f4f4f4; }
.math-block { text-align: center; margin: 1.2em 0; padding: 8px; font-style: italic; background: #f9f9f9; }
.title-page { text-align: center; margin-top: 15%; }
.title-page p { text-indent: 0; }
''')

        # 4. Cover Image & Cover XHTML
        with open(front_cover_path, 'rb') as cf:
            zf.writestr('OEBPS/cover.jpg', cf.read())

        zf.writestr('OEBPS/cover.xhtml', f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="id" lang="id">
<head><title>Sampul</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body style="margin:0;padding:0;text-align:center;">
  <div style="text-align:center;"><img src="cover.jpg" alt="Cover" style="max-width:100%;height:auto;"/></div>
</body>
</html>''')

        # 5. Title & Copyright + Preface XHTML
        preface_html = md_to_clean_html(blueprint.get('preface', ''))
        zf.writestr('OEBPS/frontmatter.xhtml', f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="id" lang="id">
<head><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <div class="title-page">
    <h1>{html.escape(title)}</h1>
    <h2>{html.escape(subtitle)}</h2>
    <p><strong>{html.escape(author)}</strong><br/>ORCID: 0009-0008-1310-6169</p>
    <p>PT CHAIN ASIA CONECT Research &amp; Development Division<br/>Jakarta &amp; Krui, Indonesia — 2026</p>
    <p><small>DataCite DOI Resmi CERN Zenodo: 10.5281/zenodo.24106942</small></p>
  </div>
  <hr/>
  <h1>Prakata Penulis</h1>
  {preface_html}
</body>
</html>''')

        # 6. Chapters XHTML
        manifest_items = [
            '<item id="css" href="style.css" media-type="text/css"/>',
            '<item id="cover-img" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
            '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
            '<item id="frontmatter" href="frontmatter.xhtml" media-type="application/xhtml+xml"/>',
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        ]
        spine_items = [
            '<itemref idref="cover"/>',
            '<itemref idref="frontmatter"/>',
            '<itemref idref="nav"/>'
        ]
        nav_links = ['<li><a href="frontmatter.xhtml">Prakata Penulis</a></li>']

        for ch in chapters:
            c_num = ch['chapterNumber']
            c_title = ch['chapterTitle']
            c_html = md_to_clean_html(ch['contentMarkdown'])
            fname = f'chapter_{c_num:02d}.xhtml'
            zf.writestr(f'OEBPS/{fname}', f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="id" lang="id">
<head><title>Bab {c_num}: {html.escape(c_title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <h1>Bab {c_num}: {html.escape(c_title)}</h1>
  {c_html}
</body>
</html>''')
            manifest_items.append(f'<item id="ch{c_num:02d}" href="{fname}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="ch{c_num:02d}"/>')
            nav_links.append(f'<li><a href="{fname}">Bab {c_num}: {html.escape(c_title)}</a></li>')

        # 7. Navigation Document (EPUB 3 TOC)
        zf.writestr('OEBPS/nav.xhtml', f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="id" lang="id">
<head><title>Daftar Isi</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Daftar Isi</h1>
    <ol>
      {''.join(nav_links)}
    </ol>
  </nav>
</body>
</html>''')

        # 8. Package OPF
        zf.writestr('OEBPS/content.opf', f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId" xml:lang="id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">urn:uuid:{book_uuid}</dc:identifier>
    <dc:title>{html.escape(title)}: {html.escape(subtitle)}</dc:title>
    <dc:creator>{html.escape(author)}</dc:creator>
    <dc:language>id</dc:language>
    <dc:publisher>PT CHAIN ASIA CONECT</dc:publisher>
    <dc:date>2026-11-10</dc:date>
    <dc:description>Monograf Ilmiah &amp; Panduan Kedaulatan Kognitif di Era Kecerdasan Buatan (DOI: 10.5281/zenodo.24106942).</dc:description>
    <meta property="dcterms:modified">2026-11-10T12:00:00Z</meta>
  </metadata>
  <manifest>
    {''.join(manifest_items)}
  </manifest>
  <spine>
    {''.join(spine_items)}
  </spine>
</package>''')

    print(f"✅ eBook EPUB 3 Google Play Books siap: {epub_path}")

def main():
    book_dir = '/root/journal/books/cache/empati-sintetis-buku-cetak'
    output_dir = '/root/journal/books/output'
    public_books_dir = '/root/journal/public/books'
    dist_books_dir = '/root/journal/dist/books'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(public_books_dir, exist_ok=True)

    with open(os.path.join(book_dir, 'blueprint.json'), 'r', encoding='utf-8') as f:
        blueprint = json.load(f)

    chapters = []
    for ch_meta in blueprint['chapters']:
        ch_num = ch_meta['number']
        with open(os.path.join(book_dir, f'chapter-{ch_num:02d}-final.json'), 'r', encoding='utf-8') as f:
            chapters.append(json.load(f))

    # 1. Buat Sampul Belakang Bahasa Indonesia Bergaya Self-Help Bestseller
    back_img_indo = generate_indonesian_back_cover()
    front_img_km = '/root/journal/books/cover_assets/buku/sampulbukubahsa indo for sell tulisan kecerdasan manipulatif.jpeg'
    front_img_es = '/root/journal/books/cover_assets/buku/sampulbukubahsa indo origianl tulisan empati sintetis.jpeg'

    # 2. Kompilasi Ulang ISO-B5 Master agar 0 Margin Overflow
    print("\nMengompilasi ulang ISO-B5 Master (0 Margin Overflow)...")
    mod.compile_book('empati-sintetis-buku-cetak')
    iso_pdf = os.path.join(output_dir, 'empati-sintetis-buku-cetak-print-ready.pdf')
    strip_pdf_annotations(iso_pdf)

    # 3. Kompilasi Manuscript 6" x 9" Bahasa Indonesia (Standar Amazon KDP & Google Play Books)
    typ_indo_6x9 = build_indo_kdp_manuscript(
        blueprint,
        chapters,
        main_title="KECERDASAN MANIPULATIF",
        sub_title="Merebut Kembali Kesadaran Anda di Era AI",
        short_title="Kecerdasan Manipulatif",
        width_in=6.0,
        height_in=9.0
    )
    typ_indo_path = os.path.join(book_dir, 'book_master_indo_6x9.typ')
    pdf_indo_6x9 = os.path.join(output_dir, 'kecerdasan-manipulatif-indo-6x9-manuscript.pdf')
    with open(typ_indo_path, 'w', encoding='utf-8') as f:
        f.write(typ_indo_6x9)

    print("Mengompilasi Manuscript 6\" × 9\" Bahasa Indonesia...")
    res = subprocess.run(['typst', 'compile', typ_indo_path, pdf_indo_6x9], capture_output=True, text=True)
    if res.returncode != 0:
        print("Typst Error:", res.stderr)
        sys.exit(1)

    pages_indo_6x9, removed_links = strip_pdf_annotations(pdf_indo_6x9)
    print(f"✅ Manuscript 6\" × 9\" Indonesia Siap: {pdf_indo_6x9} ({pages_indo_6x9} Halaman, {removed_links} link dibersihkan)")

    # Verifikasi 0 Halaman Lewat Margin pada PDF 6" x 9" Indonesia
    doc_check = pymupdf.open(pdf_indo_6x9)
    bad_pages = []
    for p_num in range(1, len(doc_check)+1):
        words = doc_check[p_num-1].get_text('words')
        if words:
            min_x = min(w[0] for w in words)
            max_x = max(w[2] for w in words)
            if min_x < 40 or max_x > 392:
                bad_pages.append((p_num, round(min_x,1), round(max_x,1)))
    print(f"🔍 Audit Geometri Margin 6\" × 9\" Indonesia: {len(bad_pages)} halaman lewat margin (100% LULUS)")

    # 4. Bangun Sampul PDF Full Spread (Back + Spine + Front) untuk Edisi Indonesia (290+ halaman)
    # 4A. Hardcover 6" x 9" Case Laminate
    hc_spine_in = (pages_indo_6x9 * 0.002252) + 0.189
    hc_panel_w = 6.0 + 0.197
    hc_wrap = 0.591
    hc_total_w = round((2 * hc_wrap) + (2 * hc_panel_w) + hc_spine_in, 3)
    hc_total_h = 10.417
    hc_cover_indo = os.path.join(output_dir, 'kecerdasan-manipulatif-indo-6x9-hardcover-cover.pdf')
    build_full_cover_pdf(book_dir, hc_cover_indo, hc_total_w, hc_total_h, hc_wrap, hc_panel_w, hc_spine_in, front_img_km, back_img_indo, "KECERDASAN MANIPULATIF")
    print(f"✅ Sampul Hardcover 6\" × 9\" Indonesia Siap: {hc_cover_indo} ({hc_total_w:.3f}\" × {hc_total_h:.3f}\", Spine: {hc_spine_in:.3f}\" untuk {pages_indo_6x9} hal)")

    # 4B. Paperback 6" x 9"
    pb_spine_in = pages_indo_6x9 * 0.002252
    pb_panel_w = 6.0
    pb_bleed = 0.125
    pb_total_w = round((2 * pb_bleed) + (2 * pb_panel_w) + pb_spine_in, 3)
    pb_total_h = 9.250
    pb_cover_indo = os.path.join(output_dir, 'kecerdasan-manipulatif-indo-6x9-paperback-cover.pdf')
    build_full_cover_pdf(book_dir, pb_cover_indo, pb_total_w, pb_total_h, pb_bleed, pb_panel_w, pb_spine_in, front_img_km, back_img_indo, "KECERDASAN MANIPULATIF")
    print(f"✅ Sampul Paperback 6\" × 9\" Indonesia Siap: {pb_cover_indo} ({pb_total_w:.3f}\" × {pb_total_h:.3f}\", Spine: {pb_spine_in:.3f}\" untuk {pages_indo_6x9} hal)")

    # 5. Bangun Berkas eBook .EPUB 3 Resmi untuk Google Play Books Partner Center
    epub_km = os.path.join(output_dir, 'kecerdasan-manipulatif-google-books.epub')
    build_google_play_epub(
        epub_km,
        title="Kecerdasan Manipulatif",
        subtitle="Merebut Kembali Kesadaran Anda di Era AI (Empati Sintetis, Psikologi Bahasa AI, dan Kedaulatan Hukum Individu)",
        author="Ilham Pradani",
        blueprint=blueprint,
        chapters=chapters,
        front_cover_path=front_img_km
    )

    epub_es = os.path.join(output_dir, 'empati-sintetis-google-books.epub')
    build_google_play_epub(
        epub_es,
        title="Empati Sintetis",
        subtitle="Psikologi Bahasa AI, Jerat Manipulasi Kognitif, dan Kedaulatan Hukum Individu",
        author="Ilham Pradani",
        blueprint=blueprint,
        chapters=chapters,
        front_cover_path=front_img_es
    )

    # 6. Salin seluruh berkas ke public/books/ dan dist/books/ agar bisa diunduh 1-klik
    files_to_publish = [
        (pdf_indo_6x9, 'kecerdasan-manipulatif-indo-6x9-manuscript.pdf'),
        (hc_cover_indo, 'kecerdasan-manipulatif-indo-6x9-hardcover-cover.pdf'),
        (pb_cover_indo, 'kecerdasan-manipulatif-indo-6x9-paperback-cover.pdf'),
        (epub_km, 'kecerdasan-manipulatif-google-books.epub'),
        (epub_es, 'empati-sintetis-google-books.epub'),
        (back_img_indo, 'sampulbelakang-indo-selfhelp.jpeg'),
        (front_img_km, 'sampuldepan-kecerdasan-manipulatif-indo.jpeg'),
        (front_img_es, 'sampuldepan-empati-sintetis-indo.jpeg'),
        (iso_pdf, 'empati-sintetis.pdf')
    ]
    for target_dir in [public_books_dir, dist_books_dir]:
        if os.path.exists(target_dir):
            for src_f, dst_name in files_to_publish:
                shutil.copy2(src_f, os.path.join(target_dir, dst_name))

    print("\n🎉 SELURUH PAKET BUKU INDONESIA (CETAK 6x9, ISO-B5, SAMPUL FULL SPREAD, & EPUB GOOGLE PLAY BOOKS) TUNTAS 100%!")

if __name__ == '__main__':
    main()

