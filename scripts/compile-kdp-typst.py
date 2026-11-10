#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - Amazon KDP Print-Ready Typst Compiler & Cover PDF Engine
Generates:
1. 6" × 9" KDP Manuscript PDF (Matches KDP Default Hardcover/Paperback Trim Size)
2. 7" × 10" KDP Manuscript PDF (Standard Scholarly Monograph Trim Size)
3. Full KDP Print-Ready Cover PDF for Hardcover 6" × 9" (Back + Spine + Front in 1 Single PDF)
4. Full KDP Print-Ready Cover PDF for Paperback 6" × 9" (Back + Spine + Front in 1 Single PDF)
"""

import json
import re
import subprocess
import os
import sys
import shutil
import importlib.util

spec = importlib.util.spec_from_file_location('compile_book_typst', '/root/journal/scripts/compile-book-typst.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

clean_to_typst_math = mod.clean_to_typst_math
clean_inline_for_typst = mod.clean_inline_for_typst
clean_chapter_markdown_to_typst = mod.clean_chapter_markdown_to_typst

def sanitize_english_typst(typ_text):
    # Replace Indonesian terms in diagram boxes or notes if any remained
    typ_text = typ_text.replace("Catatan Pemahaman Awam:", "Intuitive Conceptual Note:")
    typ_text = typ_text.replace("Bagan ", "Figure ")
    return typ_text

def build_typst_manuscript(blueprint, chapters, width_in, height_in, font_pt, inside_in, outside_in, top_in, bottom_in):
    typ_parts = []
    for i, ch in enumerate(chapters):
        cleaned = clean_chapter_markdown_to_typst(ch['contentMarkdown'])
        cleaned = sanitize_english_typst(cleaned)
        pb = "#pagebreak()\n" if i > 0 else ""
        ch_title_clean = clean_inline_for_typst(ch['chapterTitle'])
        ch_title_clean = re.sub(r'^(?:Bab|Chapter)\s+\d+:\s*', '', ch_title_clean, flags=re.IGNORECASE)
        typ_parts.append(f"""
{pb}#v(2.0em)
= Chapter {ch['chapterNumber']}: {ch_title_clean}
#v(1.2em)

{cleaned}

#v(1.6em)
""")

    preface_clean = sanitize_english_typst(clean_chapter_markdown_to_typst(blueprint.get('preface', '')))
    short_title = blueprint.get('shortTitle', 'Manipulative Intelligence')

    return f"""// Amazon KDP Print-Ready Manuscript ({width_in}" × {height_in}")
#set page(
  width: {width_in}in,
  height: {height_in}in,
  margin: (inside: {inside_in}in, outside: {outside_in}in, top: {top_in}in, bottom: {bottom_in}in),
  header: none,
  footer: none
)
#set text(font: "Libertinus Serif", size: {font_pt}pt, lang: "en")
#set par(justify: true, leading: 0.64em, first-line-indent: 1.25em)

// --- HEADING TYPOGRAPHY ---
#show heading.where(level: 1): it => block(above: 1.8em, below: 1.1em)[
  #set text(size: 13.5pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 2): it => block(above: 1.5em, below: 0.75em)[
  #set text(size: 10.8pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 3): it => block(above: 1.0em, below: 0.45em)[
  #set text(size: 9.5pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 4): it => block(above: 0.8em, below: 0.35em)[
  #set text(size: 8.8pt, weight: "bold", style: "italic", font: "Libertinus Serif")
  #it.body
]

// --- 1. HALF TITLE PAGE ---
#align(center + horizon)[
  #text(size: 17pt, weight: "bold", font: "Libertinus Serif")[MANIPULATIVE INTELLIGENCE]
  #v(0.8em)
  #text(size: 11pt, style: "italic", fill: luma(90))[Reclaiming Your Consciousness in the Age of AI]
]

#pagebreak()

// --- 2. TITLE PAGE ---
#align(center + horizon)[
  #text(size: 20pt, weight: "bold", font: "Libertinus Serif")[MANIPULATIVE INTELLIGENCE]
  #v(0.8em)
  #text(size: 12.5pt, weight: "bold", fill: luma(60))[Reclaiming Your Consciousness in the Age of AI]
  #v(1.0em)
  #text(size: 9.5pt, style: "italic", fill: luma(90))[{blueprint['subtitle']}]
  #v(2.8em)
  #line(length: 35%, stroke: 1.1pt + black)
  #v(2.2em)
  #text(size: 13pt, weight: "bold")[Ilham Pradani]
  #v(0.3em)
  #text(size: 8.5pt, fill: luma(80))[ORCID: 0009-0008-1310-6169]
  #v(0.6em)
  #text(size: 9pt, fill: luma(100))[PT CHAIN ASIA CONECT Research & Development Division]
  #v(4.5em)
  #text(size: 8.5pt, fill: luma(110))[Independently published]
]

#pagebreak()

// --- 3. COPYRIGHT & CIP NOTICE ---
#align(bottom)[
  #text(size: 8pt)[
    *MANIPULATIVE INTELLIGENCE: Reclaiming Your Consciousness in the Age of AI*\\
    {blueprint['subtitle']}\\
    Author: Ilham Pradani (ORCID: 0009-0008-1310-6169)\\
    Research Affiliation: PT CHAIN ASIA CONECT Research & Development Division\\
    \\
    Copyright © 2026 by Ilham Pradani. All Rights Reserved.\\
    Imprint: Independently published\\
    ISBN: 9798141548437 (979-8-1415-4843-7)\\
    Trim Size: {width_in}" × {height_in}" — No Bleed.\\
    \\
    No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without prior written permission from the author, except for brief quotations embodied in critical reviews and academic citations.\\
    \\
    Permanent Scholarly Repository Record: CERN Zenodo (DataCite DOI: 10.5281/zenodo.24106942).
  ]
]

#pagebreak()

// --- 4. PREFACE (Roman Numerals) ---
#set page(
  numbering: "i",
  header: context [
    #if counter(page).get().first() > 1 [
      #set text(font: "Libertinus Serif", size: 7.5pt, fill: luma(80))
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(style: "italic")[Preface]],
        [#text(size: 7.2pt, fill: luma(120))[Ilham Pradani]])
      #v(-2pt)
      #line(length: 100%, stroke: 0.35pt + luma(180))
    ]
  ],
  footer: context [
    #line(length: 100%, stroke: 0.25pt + luma(200))
    #v(2pt)
    #set text(font: "Libertinus Serif", size: 8pt, fill: luma(90))
    #align(center)[#counter(page).display("i")]
  ]
)
#counter(page).update(1)

#v(1.8em)
= Preface: Algorithmic Architecture and Human Vulnerability
#v(1.2em)

{preface_clean}

#v(1.6em)
#align(right)[
  *Ilham Pradani*\\
  Jakarta & Krui, Indonesia
]

#pagebreak()

// --- 5. TABLE OF CONTENTS ---
#show outline.entry.where(level: 1): it => {{
  v(0.5em, weak: true)
  text(weight: "bold", size: 8pt)[#it]
}}
#show outline.entry.where(level: 2): it => {{
  v(0.14em, weak: true)
  text(size: 7.2pt, fill: luma(65))[#it]
}}

#outline(title: [Table of Contents], indent: 1.2em, depth: 2)

#pagebreak()

// --- 6. MAIN BODY (Arabic Numerals) ---
#set page(
  numbering: "1",
  header: context [
    #let pn = counter(page).get().first()
    #if pn > 1 [
      #set text(font: "Libertinus Serif", size: 7.5pt, fill: luma(80))
      #if calc.even(pn) [
        #grid(columns: (1fr, auto), align: (left, right),
          [#text(style: "italic")[{short_title}]],
          [#text(size: 7pt, fill: luma(120))[Reclaiming Your Consciousness]])
      ] else [
        #grid(columns: (auto, 1fr), align: (left, right),
          [#text(size: 7pt, fill: luma(120))[Synthetic Empathy & Cognitive Liberty]],
          [#text(style: "italic")[*Ilham Pradani*]])
      ]
      #v(-2pt)
      #line(length: 100%, stroke: 0.35pt + luma(180))
    ]
  ],
  footer: context [
    #line(length: 100%, stroke: 0.25pt + luma(200))
    #v(2pt)
    #set text(font: "Libertinus Serif", size: 8pt, fill: luma(90))
    #if calc.even(counter(page).get().first()) [
      #grid(columns: (auto, 1fr), align: (left, right),
        [*#counter(page).display()*],
        [#text(size: 7pt, fill: luma(130))[ISBN 979-8-1415-4843-7]])
    ] else [
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(size: 7pt, fill: luma(130))[Ilham Pradani]],
        [*#counter(page).display()*])
    ]
  ]
)
#counter(page).update(1)

{''.join(typ_parts)}
"""

def build_full_cover_pdf(book_dir, output_pdf_path, total_w_in, total_h_in, wrap_in, panel_w_in, spine_w_in, front_img_path, back_img_path):
    """
    Uses Typst to assemble a crystal-clear, 100% vector-text + high-res cover spread PDF:
    [Wrap Left | Back Cover Panel | Spine (with rotated title + author) | Front Cover Panel | Wrap Right]
    """
    typ_cover = f"""#set page(
  width: {total_w_in:.4f}in,
  height: {total_h_in:.4f}in,
  margin: 0pt,
  fill: rgb(35, 36, 36)
)

// Back Cover Image placed in the Back Panel area
#place(
  top + left,
  dx: {wrap_in:.4f}in,
  dy: {wrap_in:.4f}in,
  image("{back_img_path}", width: {panel_w_in:.4f}in, height: {total_h_in - 2*wrap_in:.4f}in, fit: "stretch")
)

// Front Cover Image placed in the Front Panel area
#place(
  top + left,
  dx: {wrap_in + panel_w_in + spine_w_in:.4f}in,
  dy: {wrap_in:.4f}in,
  image("{front_img_path}", width: {panel_w_in:.4f}in, height: {total_h_in - 2*wrap_in:.4f}in, fit: "stretch")
)

// Spine Text (Rotated 90deg clockwise, standard US/Amazon KDP spine orientation)
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
            [#text(size: 11pt, weight: "bold", fill: white)[MANIPULATIVE INTELLIGENCE]],
            [#text(size: 8.5pt, fill: rgb(235, 60, 60))[•]],
            [#text(size: 10pt, weight: "regular", fill: rgb(220, 222, 225))[ILHAM PRADANI]]
          )
        ]
      ]
    ]
  )
)
"""
    cover_typ_path = os.path.join(book_dir, 'cover_spread_temp.typ')
    with open(cover_typ_path, 'w', encoding='utf-8') as f:
        f.write(typ_cover)
    res = subprocess.run(['typst', 'compile', '--root', '/', cover_typ_path, output_pdf_path], capture_output=True, text=True)
    if res.returncode != 0:
        print("Cover Typst Error:", res.stderr)
        sys.exit(1)

def compile_kdp_book():
    bundle_path = '/root/journal/books/cache/synthetic-empathy-english-edition/book_bundle.json'
    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle = json.load(f)

    blueprint = bundle['blueprint']
    chapters = bundle['chapters']

    book_dir = '/root/journal/books/cache/synthetic-empathy-english-edition'
    output_dir = '/root/journal/books/output'
    public_books_dir = '/root/journal/public/books'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(public_books_dir, exist_ok=True)

    import pymupdf

    # 1. Compile 6" x 9" Manuscript (Matches user's selected KDP Hardcover/Paperback Trim Size)
    typ_6x9 = build_typst_manuscript(blueprint, chapters, 6.0, 9.0, 8.8, 0.75, 0.55, 0.58, 0.58)
    typ_6x9_path = os.path.join(book_dir, 'book_master_6x9.typ')
    pdf_6x9_path = os.path.join(output_dir, 'manipulative-intelligence-kdp-6x9-manuscript.pdf')
    with open(typ_6x9_path, 'w', encoding='utf-8') as f:
        f.write(typ_6x9)
    print("Compiling Amazon KDP 6\" × 9\" Manuscript PDF...")
    res1 = subprocess.run(['typst', 'compile', typ_6x9_path, pdf_6x9_path], capture_output=True, text=True)
    if res1.returncode != 0:
        print("Typst 6x9 Error:", res1.stderr)
        sys.exit(1)
    doc_6x9 = pymupdf.open(pdf_6x9_path)
    pages_6x9 = len(doc_6x9)
    print(f"✅ 6\" × 9\" Manuscript Ready: {pdf_6x9_path} ({pages_6x9} pages)")

    # 2. Compile 7" x 10" Manuscript
    typ_7x10 = build_typst_manuscript(blueprint, chapters, 7.0, 10.0, 9.6, 0.80, 0.60, 0.68, 0.68)
    typ_7x10_path = os.path.join(book_dir, 'book_master.typ')
    pdf_7x10_path = os.path.join(output_dir, 'synthetic-empathy-amazon-kdp-print-ready.pdf')
    with open(typ_7x10_path, 'w', encoding='utf-8') as f:
        f.write(typ_7x10)
    print("Compiling Amazon KDP 7\" × 10\" Manuscript PDF...")
    res2 = subprocess.run(['typst', 'compile', typ_7x10_path, pdf_7x10_path], capture_output=True, text=True)
    if res2.returncode != 0:
        print("Typst 7x10 Error:", res2.stderr)
        sys.exit(1)
    doc_7x10 = pymupdf.open(pdf_7x10_path)
    pages_7x10 = len(doc_7x10)
    print(f"✅ 7\" × 10\" Manuscript Ready: {pdf_7x10_path} ({pages_7x10} pages)")

    # 3. Build Full KDP Cover PDFs (Back + Spine + Front)
    front_img = '/root/journal/books/cover_assets/buku/sampulbukubahsaenglish for sell amazon.jpeg'
    back_img = '/root/journal/books/cover_assets/buku/sampulbelakang_english_amazon_selfhelp.jpeg'

    # 3A. Hardcover 6" x 9" Case Laminate Cover PDF (Exact KDP Formula for pages_6x9)
    hc_spine_in = (pages_6x9 * 0.002252) + 0.189
    hc_panel_w = 6.0 + 0.197
    hc_panel_h = 9.0 + 0.236
    hc_wrap = 0.591
    hc_total_w = (2 * hc_wrap) + (2 * hc_panel_w) + hc_spine_in
    hc_total_h = (2 * hc_wrap) + hc_panel_h
    hc_cover_pdf = os.path.join(output_dir, 'manipulative-intelligence-kdp-6x9-hardcover-cover.pdf')
    build_full_cover_pdf(book_dir, hc_cover_pdf, hc_total_w, hc_total_h, hc_wrap, hc_panel_w, hc_spine_in, front_img, back_img)
    print(f"✅ Hardcover 6\" × 9\" Full Cover PDF Ready: {hc_cover_pdf} ({hc_total_w:.3f}\" × {hc_total_h:.3f}\", Spine: {hc_spine_in:.3f}\")")

    # 3B. Paperback 6" x 9" Cover PDF (Exact KDP Formula for pages_6x9)
    pb_spine_in = pages_6x9 * 0.002252
    pb_panel_w = 6.0
    pb_panel_h = 9.0
    pb_bleed = 0.125
    pb_total_w = (2 * pb_bleed) + (2 * pb_panel_w) + pb_spine_in
    pb_total_h = (2 * pb_bleed) + pb_panel_h
    pb_cover_pdf = os.path.join(output_dir, 'manipulative-intelligence-kdp-6x9-paperback-cover.pdf')
    build_full_cover_pdf(book_dir, pb_cover_pdf, pb_total_w, pb_total_h, pb_bleed, pb_panel_w, pb_spine_in, front_img, back_img)
    print(f"✅ Paperback 6\" × 9\" Full Cover PDF Ready: {pb_cover_pdf} ({pb_total_w:.3f}\" × {pb_total_h:.3f}\", Spine: {pb_spine_in:.3f}\")")

    # Copy all 4 PDFs to public/books/ for 1-click download
    shutil.copy2(pdf_6x9_path, os.path.join(public_books_dir, 'manipulative-intelligence-kdp-6x9-manuscript.pdf'))
    shutil.copy2(pdf_7x10_path, os.path.join(public_books_dir, 'manipulative-intelligence-kdp-7x10-manuscript.pdf'))
    shutil.copy2(hc_cover_pdf, os.path.join(public_books_dir, 'manipulative-intelligence-kdp-6x9-hardcover-cover.pdf'))
    shutil.copy2(pb_cover_pdf, os.path.join(public_books_dir, 'manipulative-intelligence-kdp-6x9-paperback-cover.pdf'))
    print("🌐 All KDP Manuscript & Cover PDFs copied to /root/journal/public/books/")

if __name__ == '__main__':
    compile_kdp_book()
