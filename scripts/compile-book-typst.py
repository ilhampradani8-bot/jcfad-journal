#!/usr/bin/env python3
import json
import re
import subprocess
import os
import sys

def clean_text_for_typst(text):
    if not text:
        return ''
    
    # 1. Remove HTML tags
    t = re.sub(r'</?[a-zA-Z0-9]+[^>]*>', '', text)
    
    # 2. Normalize display math $$...$$ and \[...\] to raw code block
    def stash_math(m):
        eq = m.group(1).strip()
        eq = eq.replace(r'\{', '{').replace(r'\}', '}').replace(r'\_', '_')
        return f'\n#align(center)[#box(fill: luma(248), inset: 6pt, radius: 2pt, stroke: 0.4pt + luma(200))[#text(size: 8.5pt)[``` {eq} ```]]]\n'
    
    t = re.sub(r'\$\$(.*?)\$\$', stash_math, t, flags=re.DOTALL)
    t = re.sub(r'\\\[(.*?)\\\]', stash_math, t, flags=re.DOTALL)
    
    # 3. Inline math \(...\) to raw code backtick `...`
    t = re.sub(r'\\\((.*?)\\\)', r'`\1`', t)
    
    # 4. Escape ALL literal dollar signs to single backslash \$ so Typst never treats them as math mode
    # First protect genuine math blocks with LaTeX commands
    t = re.sub(r'\$([^$\n]*?\\[a-zA-Z]+[^$\n]*?)\$', r'`\1`', t)
    # Any other dollar signs (e.g. $10, $500M, prices, variables) escape to \$
    t = t.replace('\\$', '$')  # Normalize existing escapes
    t = t.replace('$', '\\$')  # Ensure exact single backslash escape
    
    # 5. Headings conversion
    t = re.sub(r'(?m)^####\s+(.*)$', r'==== \1', t)
    t = re.sub(r'(?m)^###\s+(.*)$', r'=== \1', t)
    t = re.sub(r'(?m)^##\s+(.*)$', r'== \1', t)
    t = re.sub(r'(?m)^#\s+Bab.*$', '', t)
    t = re.sub(r'(?m)^#\s+(.*)$', r'== \1', t)
    t = re.sub(r'(?m)^[#=]{1,5}\s*$', '', t)

    # 6. Bullets
    t = re.sub(r'(?m)^\*\s+', '- ', t)
    
    # 7. Safe Bold & Italic preservation (eliminate unclosed stray asterisks)
    bold_spans = []
    def stash_bold(m):
        inner = m.group(1).strip()
        idx = len(bold_spans)
        bold_spans.append(inner)
        return f'__SAFE_BOLD_{idx}__'

    t = re.sub(r'\*\*\*([^*\n]+)\*\*\*', stash_bold, t)
    t = re.sub(r'\*\*([^*\n]+)\*\*', stash_bold, t)

    italic_spans = []
    def stash_italic(m):
        inner = m.group(1).strip()
        idx = len(italic_spans)
        italic_spans.append(inner)
        return f'__SAFE_ITALIC_{idx}__'

    t = re.sub(r'(?<=\s)\*([^*\s\n][^*\n]*?[^*\s\n])\*(?=\s|[,\.;:\)])', stash_italic, t)

    # Strip ALL remaining unpaired asterisks from the text
    t = t.replace('*', '')

    # Restore balanced bold and italic
    for i, b in enumerate(bold_spans):
        clean_b = b.replace('[', r'\[').replace(']', r'\]')
        t = t.replace(f'__SAFE_BOLD_{i}__', f'*{clean_b}*')
    for i, it in enumerate(italic_spans):
        clean_it = it.replace('[', r'\[').replace(']', r'\]')
        t = t.replace(f'__SAFE_ITALIC_{i}__', f'_{clean_it}_')

    # 8. Escape Typst specials outside code blocks
    parts = re.split(r'(`[^`]*`|```.*?```)', t, flags=re.DOTALL)
    out_parts = []
    for p in parts:
        if p.startswith('`'):
            out_parts.append(p)
        else:
            s = p
            s = re.sub(r'(?<!\\)@([a-zA-Z0-9_]+)', r'\\@\1', s)
            s = re.sub(r'(?<!\\)#([a-zA-Z0-9_]+)', r'\\#\1', s)
            s = s.replace('<', r'\<').replace('>', r'\>')
            out_parts.append(s)
            
    return ''.join(out_parts)

def compile_book(slug='empati-sintetis-buku-cetak'):
    base_dir = '/root/journal/books'
    book_dir = os.path.join(base_dir, 'cache', slug)
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    blueprint_path = os.path.join(book_dir, 'blueprint.json')
    if not os.path.exists(blueprint_path):
        print(f"Error: {blueprint_path} not found")
        sys.exit(1)
        
    with open(blueprint_path, 'r', encoding='utf-8') as f:
        blueprint = json.load(f)
        
    chapters = []
    for ch_meta in blueprint['chapters']:
        ch_num = ch_meta['number']
        f_name = f"chapter-{ch_num:02d}-final.json"
        ch_file = os.path.join(book_dir, f_name)
        if os.path.exists(ch_file):
            with open(ch_file, 'r', encoding='utf-8') as f:
                chapters.append(json.load(f))
        else:
            print(f"Warning: {ch_file} missing, skipped")
            
    print(f"Compiling {len(chapters)} chapters...")
    
    typ_parts = []
    for ch in chapters:
        cleaned = clean_text_for_typst(ch['contentMarkdown'])
        typ_parts.append(f"""
#pagebreak(to: "odd")
#v(2em)
#text(size: 12pt, weight: "bold", fill: luma(100))[BAB {ch['chapterNumber']}]
#v(0.3em)
= {clean_text_for_typst(ch['chapterTitle'])}
#v(1.5em)

{cleaned}

#v(2em)
""")

    typst_code = f"""// ==============================================================================
// TYPST ACADEMIC MONOGRAPH / PRINT-READY BOOK TEMPLATE (ISO-B5)
// ==============================================================================
#set page(
  paper: "iso-b5",
  margin: (
    inside: 2.5cm,
    outside: 1.8cm,
    top: 2.2cm,
    bottom: 2.2cm
  ),
  header: context {{
    let pageNum = counter(page).get().first()
    if pageNum > 4 [
      #set text(font: "Libertinus Serif", size: 8pt, fill: luma(90))
      #if calc.even(pageNum) [
        #align(left)[*{blueprint['title']}*]
      ] else [
        #align(right)[*Ilham Pradani*]
      ]
      #v(-2pt)
      #line(length: 100%, stroke: 0.3pt + luma(180))
    ]
  }},
  footer: context [
    #if counter(page).get().first() > 2 [
      #align(center)[#text(size: 9pt, font: "Libertinus Serif")[#counter(page).display()]]
    ]
  ]
)

#set text(
  font: "Libertinus Serif",
  size: 10pt,
  lang: "id"
)

#set par(
  justify: true,
  leading: 0.75em,
  first-line-indent: 1.5em
)

// --- 1. COVER / HALAMAN JUDUL BUKU CETAK ---
#align(center + horizon)[
  #text(size: 24pt, weight: "bold", font: "Libertinus Serif")[{blueprint['title']}]
  
  #v(1em)
  #text(size: 13pt, style: "italic", fill: luma(80))[{blueprint['subtitle']}]
  
  #v(3em)
  #line(length: 40%, stroke: 1.5pt + black)
  #v(2em)
  
  #text(size: 14pt, weight: "bold")[Ilham Pradani]
  #v(0.3em)
  #text(size: 8.5pt, fill: luma(80))[ORCID: 0009-0008-1310-6169]
  
  #v(0.5em)
  #text(size: 10pt, fill: luma(100))[PT CHAIN ASIA CONECT Research & Development Division]
  
  #v(5em)
  #text(size: 9pt, fill: luma(120))[PT CHAIN ASIA CONECT Publishing Division\\ Krui, Pesisir Barat & Jakarta, Indonesia]
]

#pagebreak()

// --- 2. HALAMAN HAK CIPTA & METADATA PENERBIT ---
#align(bottom)[
  #text(size: 8.5pt)[
    *{blueprint['title']}*\\
    {blueprint['subtitle']}\\
    Penulis: Ilham Pradani (ORCID: 0009-0008-1310-6169)\\
    Afiliasi: PT CHAIN ASIA CONECT Research & Development Division\\
    \\
    Hak Cipta Dilindungi Undang-Undang (All Rights Reserved).\\
    Diterbitkan oleh PT CHAIN ASIA CONECT Research & Monograph Series.\\
    Preprint & Scholarly Registry: CERN Zenodo Open Science Repository.\\
    \\
    Cetakan Pertama, 2026\\
    Format Buku: Standar ISO-B5 Percetakan Offset & Print-on-Demand (POD).\\
    Dilarang memperbanyak sebagian atau seluruh isi buku ini tanpa izin tertulis dari penerbit.
  ]
]

#pagebreak()

// --- 3. PRAKATA & KATA PENGANTAR (Halaman Romawi) ---
#set page(numbering: "i")
#counter(page).update(3)

== Prakata Penulis
#v(1em)
{clean_text_for_typst(blueprint['preface'])}

#v(2em)
#align(right)[
  *Ilham Pradani*\\
  Krui, Pesisir Barat & Jakarta
]

#pagebreak()

// --- 4. DAFTAR ISI OTOMATIS (TABLE OF CONTENTS) ---
#outline(
  title: [Daftar Isi],
  indent: 1.5em,
  depth: 2
)

#pagebreak(to: "odd")

// --- 5. ISI UTAMA BUKU (Halaman Angka Arab: 1, 2, 3...) ---
#set page(numbering: "1")
#counter(page).update(1)

{''.join(typ_parts)}
"""

    typst_path = os.path.join(book_dir, 'book_master.typ')
    pdf_path = os.path.join(output_dir, f"{slug}-print-ready.pdf")
    
    with open(typst_path, 'w', encoding='utf-8') as f:
        f.write(typst_code)
        
    print(f"Typst markup written to: {typst_path}")
    print("Compiling with Typst...")
    
    res = subprocess.run(['typst', 'compile', typst_path, pdf_path], capture_output=True, text=True)
    if res.returncode != 0:
        print("Typst Compilation Error:")
        print(res.stderr)
        sys.exit(1)
        
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"🎉 SUKSES BESAR! PDF Buku Cetak Selesai Dikompilasi:")
    print(f"📂 File : {pdf_path}")
    print(f"📊 Ukuran: {size_mb:.2f} MB")
    return pdf_path

if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else 'empati-sintetis-buku-cetak'
    compile_book(slug)
