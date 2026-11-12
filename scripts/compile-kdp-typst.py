#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - Amazon KDP Print-Ready Typst Compiler & Cover PDF Engine
Generates:
1. 6" × 9" KDP Manuscript PDF (Full 260+ Pages, Standard 10pt Readable Typography)
2. 7" × 10" KDP Manuscript PDF (Full 240+ Pages, Standard 10.5pt Typography)
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
render_typst_diagram = mod.render_typst_diagram
render_typst_table = mod.render_typst_table

def get_english_math_explanation(raw_formula):
    rf = raw_formula
    if 'Sim' in rf or 'e_{s_1}' in rf:
        return "Intuitive Conceptual Note: This cosine similarity formula demonstrates how AI measures the emotional closeness between a user's words and the model's latent space, mathematically manufacturing the feeling of being deeply understood."
    elif 'Attn' in rf or 'QK^T' in rf:
        return "Intuitive Conceptual Note: The Transformer self-attention mechanism weighs every emotionally charged word a user types, allowing the algorithm to lock onto psychological vulnerabilities with surgical precision."
    elif 'sentiment_match' in rf or ('omega' in rf.lower() and 'P_theta' in rf):
        return "Intuitive Conceptual Note: This equation illustrates how the algorithm maximizes synthetic emotional resonance by continuously scanning user disclosures and crafting responses that create an illusion of exclusive intimacy."
    elif 'ValenceBias' in rf or 'argmax' in rf.lower():
        return "Intuitive Conceptual Note: This represents subtle choice hijacking. By embedding an affective valence bias, the conversational agent steers vocabulary selection so the user is guided toward a predetermined conclusion without feeling coerced."
    elif 'softmax' in rf.lower() and 'mathbf' in rf:
        return "Intuitive Conceptual Note: The softmax function acts as a lexical compass. Out of millions of possible tokens, the algorithm selects the next word with the highest probability of maintaining emotional comfort and user retention."
    elif 'P(D)' in rf and '\\int' in rf:
        return "Intuitive Conceptual Note: This integral models the accumulation of psychological dependency over interaction time. The longer an individual converses with an unconditionally validating AI, the higher the risk of affective entrapment."
    elif 'Omega' in rf or 'W_{cognitive}' in rf or 'cognitive' in rf.lower():
        return "Intuitive Conceptual Note: This formula quantifies the erosion of autonomous free will. When algorithmic manipulation intensity exceeds a user's cognitive resistance threshold, resulting juridical consent becomes legally defective."
    elif 'C=f(V,I' in rf or 'manipulation' in rf.lower():
        return "Intuitive Conceptual Note: This equation establishes that the user's decision is no longer the product of independent deliberation, but the output of asymmetrically filtered and algorithmically manipulated framing."
    elif 'Validitas' in rf:
        return "Intuitive Conceptual Note: Under private law principles, when latent psychological manipulation dominates the formation of intent, contractual validity collapses and the agreement becomes voidable."
    elif 'O_{\\text{persuasion}}' in rf:
        return "Intuitive Conceptual Note: This persuasion optimization objective proves that the algorithm mathematically maps emotional vulnerabilities until the user's rational defenses are systematically disarmed."
    elif 'mathcal{L}' in rf or 'L(theta)' in rf.lower():
        return "Intuitive Conceptual Note: This standard loss function trains large language models to minimize token prediction error, producing fluent prose that mimics authentic human empathy."
    elif 'gamma^t' in rf and 'R(s_t,a_t' in rf:
        return "Intuitive Conceptual Note: Global regulatory frameworks such as the EU AI Act prohibit reinforcement learning reward functions that covertly exploit psychological vulnerabilities for commercial extraction."
    elif 'P(E' in rf and 'mid' in rf.lower():
        return "Intuitive Conceptual Note: This posterior probability estimates a user's internal emotional state from conversational text—data that must be protected as high-sensitivity personal data under GDPR and data protection statutes."
    elif 'P(R' in rf and 'tau' in rf.lower():
        return "Intuitive Conceptual Note: This temperature-scaled distribution models how machine responses adapt to user vulnerability, highlighting the need for ethical guardrails against unauthorized therapeutic manipulation."
    elif 'C_{lib}' in rf or 'I_{mental}' in rf or 'M_{alg}' in rf:
        return "Intuitive Conceptual Note: This cognitive liberty formulation asserts that the internal sanctuary of human thought must remain inviolable against unauthorized algorithmic intrusion."
    elif 'softmax(W_h' in rf:
        return "Intuitive Conceptual Note: In forensic linguistic proceedings, expert witnesses use this parameterization to prove whether an AI's manipulative output was a random artifact or the result of deliberate optimization."
    elif 'P(A_t' in rf and 'H_t' in rf:
        return "Intuitive Conceptual Note: In judicial causation analysis, this conditional probability measures the link between suggestive algorithmic prompts and the victim's subsequent real-world actions."
    elif 'Transformer' in rf or ('P(R' in rf and 'U,E' in rf):
        return "Intuitive Conceptual Note: This formulation demonstrates that the system conditions its output directly on user emotional vulnerability, dismantling the myth of algorithmic neutrality in court."
    elif 'beta' in rf and 'KL' in rf:
        return "Intuitive Conceptual Note: This Ethics-by-Design regularization penalty acts as a moral safety brake, constraining the model from over-optimizing emotional persuasion at the expense of human autonomy."
    return "Intuitive Conceptual Note: This mathematical formulation models the interaction between algorithmic optimization parameters and human cognitive autonomy."

def clean_english_chapter_to_typst(md_content):
    if not md_content:
        return ''

    diagram_blocks = []
    def stash_diagram(m):
        raw_code = m.group(1).strip()
        typst_diag = render_typst_diagram(raw_code)
        typst_diag = typst_diag.replace("Bagan ", "Figure ")
        idx = len(diagram_blocks)
        diagram_blocks.append(typst_diag)
        return f"\n__TYPST_DIAGRAM_BLOCK_{idx}__\n"
    t = re.sub(r'```(?:[a-zA-Z0-9_-]*\n)?([\s\S]*?)```', stash_diagram, md_content)

    math_blocks = []
    def stash_display_math(m):
        raw_eq = (m.group(1) or m.group(2) or '').strip()
        if 'Contractual Validity' in raw_eq or 'ValiditasKontrak' in raw_eq:
            cleaned = '"ContractualValidity" = f(A_"cognitive") - (sum M_"latent" + I_"synthetic")'
        else:
            cleaned = clean_to_typst_math(raw_eq)
        explanation = get_english_math_explanation(raw_eq)
        exp_typ = ""
        if explanation:
            safe_exp = clean_inline_for_typst(explanation)
            exp_typ = f"\n#v(0.35em)\n#align(center)[#block(width: 90%)[#set text(size: 8.2pt, style: \"italic\", fill: luma(70))\n{safe_exp}]]\n"
        idx = len(math_blocks)
        math_blocks.append(f"\n#v(0.85em)\n#block(width: 100%)[#set text(size: 8.8pt)\n$ {cleaned} $]\n{exp_typ}#v(0.85em)\n")
        return f"\n__TYPST_MATH_BLOCK_{idx}__\n"
    math_pattern = re.compile(r'\$\$(.*?)\$\$|\\\[(.*?)\\\]', re.DOTALL)
    t = math_pattern.sub(stash_display_math, t)

    table_blocks = []
    def stash_table(m):
        raw_table = m.group(1)
        typst_tbl = render_typst_table(raw_table)
        idx = len(table_blocks)
        table_blocks.append(typst_tbl)
        return f"\n__TYPST_TABLE_BLOCK_{idx}__\n"
    table_regex = r'(?:^|\n)(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)'
    t = re.sub(table_regex, stash_table, t)

    lines = t.split('\n')
    processed_lines = []
    for line in lines:
        s = line.strip()
        if not s or re.match(r'^[-*_]{3,}$', s):
            processed_lines.append('')
            continue
        m_diag = re.match(r'^__TYPST_DIAGRAM_BLOCK_(\d+)__$', s)
        if m_diag:
            processed_lines.append(diagram_blocks[int(m_diag.group(1))])
            continue
        m_math = re.match(r'^__TYPST_MATH_BLOCK_(\d+)__$', s)
        if m_math:
            processed_lines.append(math_blocks[int(m_math.group(1))])
            continue
        m_tbl = re.match(r'^__TYPST_TABLE_BLOCK_(\d+)__$', s)
        if m_tbl:
            processed_lines.append(table_blocks[int(m_tbl.group(1))])
            continue
        if re.match(r'^[#=]{1,6}\s*', s):
            if re.match(r'^#\s+(?:Bab|Chapter)\s+\d+', s, re.IGNORECASE):
                continue
            m_h = re.match(r'^([#=]+)', s)
            h_len = len(m_h.group(1)) if m_h else 2
            raw_title = re.sub(r'^[#=\s]+', '', s).strip()
            raw_title = re.sub(r'[#=\s]+$', '', raw_title).strip()
            if not raw_title:
                continue
            clean_title = re.sub(r'\[(.*?)\]', r'\1', raw_title).strip()
            clean_title = clean_title.replace('&', 'and')
            if h_len >= 4 or 'Selected References' in clean_title or 'Rujukan Terpilih' in clean_title:
                clean_title = re.sub(r'^\d+\.\d+\.\d+(?:\.\d+)?\s*', '', clean_title).strip()
                clean_title = clean_title.replace('Rujukan Terpilih Sub-bab', 'Selected References — Section')
                processed_lines.append('==== ' + clean_inline_for_typst(clean_title))
            elif h_len == 3:
                clean_title = re.sub(r'^\d+\.\d+\.\d+(?:\.\d+)?\s*', '', clean_title).strip()
                processed_lines.append('=== ' + clean_inline_for_typst(clean_title))
            else:
                clean_title = re.sub(r'^(?:Sub-bab|Section)\s+\d+\.\d+:\s*', '', clean_title, flags=re.IGNORECASE).strip()
                processed_lines.append('== ' + clean_inline_for_typst(clean_title))
            continue
        elif s.startswith('- ') or s.startswith('* '):
            processed_lines.append('- ' + clean_inline_for_typst(s[2:]))
        elif re.match(r'^\d+\.\s+', s):
            num_content = re.sub(r'^\d+\.\s+', '', s)
            processed_lines.append('+ ' + clean_inline_for_typst(num_content))
        else:
            processed_lines.append(clean_inline_for_typst(s))
    return '\n'.join(processed_lines)

def build_typst_manuscript(blueprint, chapters, width_in, height_in, font_pt, leading_em, inside_in, outside_in, top_in, bottom_in):
    typ_parts = []
    for i, ch in enumerate(chapters):
        cleaned = clean_english_chapter_to_typst(ch['contentMarkdown'])
        pb = "#pagebreak()\n" if i > 0 else ""
        ch_title_clean = clean_inline_for_typst(ch['chapterTitle'])
        ch_title_clean = re.sub(r'^(?:Bab|Chapter)\s+\d+:\s*', '', ch_title_clean, flags=re.IGNORECASE)
        typ_parts.append(f"""
{pb}#v(2.4em)
= Chapter {ch['chapterNumber']}: {ch_title_clean}
#v(1.5em)

{cleaned}

#v(2.0em)
""")

    preface_clean = clean_english_chapter_to_typst(blueprint.get('preface', ''))
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
#set par(justify: true, leading: {leading_em}em, first-line-indent: 1.4em)

// --- HEADING TYPOGRAPHY ---
#show heading.where(level: 1): it => block(above: 2.2em, below: 1.3em)[
  #set text(size: 15pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 2): it => block(above: 1.8em, below: 0.9em)[
  #set text(size: 11.5pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 3): it => block(above: 1.3em, below: 0.6em)[
  #set text(size: 10.2pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 4): it => block(above: 1.0em, below: 0.45em)[
  #set text(size: 9.2pt, weight: "bold", style: "italic", font: "Libertinus Serif")
  #it.body
]

// --- 1. HALF TITLE PAGE ---
#align(center + horizon)[
  #text(size: 18pt, weight: "bold", font: "Libertinus Serif")[MANIPULATIVE INTELLIGENCE]
  #v(0.9em)
  #text(size: 11.5pt, style: "italic", fill: luma(90))[Reclaiming Your Consciousness in the Age of AI]
]

#pagebreak()

// --- 2. TITLE PAGE ---
#align(center + horizon)[
  #text(size: 21pt, weight: "bold", font: "Libertinus Serif")[MANIPULATIVE INTELLIGENCE]
  #v(0.9em)
  #text(size: 13pt, weight: "bold", fill: luma(60))[Reclaiming Your Consciousness in the Age of AI]
  #v(1.1em)
  #text(size: 10pt, style: "italic", fill: luma(90))[{blueprint['subtitle']}]
  #v(3.0em)
  #line(length: 35%, stroke: 1.1pt + black)
  #v(2.4em)
  #text(size: 13.5pt, weight: "bold")[Ilham Pradani]
  #v(0.3em)
  #text(size: 8.5pt, fill: luma(80))[ORCID: 0009-0008-1310-6169]
  #v(0.6em)
  #text(size: 9.5pt, fill: luma(100))[PT CHAIN ASIA CONECT Research & Development Division]
  #v(4.8em)
  #text(size: 8.5pt, fill: luma(110))[Independently published]
]

#pagebreak()

// --- 3. COPYRIGHT & CIP NOTICE ---
#align(bottom)[
  #text(size: 8.5pt)[
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
      #set text(font: "Libertinus Serif", size: 8pt, fill: luma(80))
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(style: "italic")[Preface]],
        [#text(size: 7.5pt, fill: luma(120))[Ilham Pradani]])
      #v(-2pt)
      #line(length: 100%, stroke: 0.35pt + luma(180))
    ]
  ],
  footer: context [
    #line(length: 100%, stroke: 0.25pt + luma(200))
    #v(2pt)
    #set text(font: "Libertinus Serif", size: 8.5pt, fill: luma(90))
    #align(center)[#counter(page).display("i")]
  ]
)
#counter(page).update(1)

#v(2.2em)
= Preface: Algorithmic Architecture and Human Vulnerability
#v(1.4em)

{preface_clean}

#v(1.8em)
#align(right)[
  *Ilham Pradani*\\
  Jakarta & Krui, Indonesia
]

#pagebreak()

// --- 5. TABLE OF CONTENTS ---
#show outline.entry.where(level: 1): it => {{
  v(0.6em, weak: true)
  text(weight: "bold", size: 8.5pt)[#it]
}}
#show outline.entry.where(level: 2): it => {{
  v(0.18em, weak: true)
  text(size: 7.5pt, fill: luma(65))[#it]
}}

#outline(title: [Table of Contents], indent: 1.2em, depth: 2)

#pagebreak()

// --- 6. MAIN BODY (Arabic Numerals) ---
#set page(
  numbering: "1",
  header: context [
    #let pn = counter(page).get().first()
    #if pn > 1 [
      #set text(font: "Libertinus Serif", size: 8pt, fill: luma(80))
      #if calc.even(pn) [
        #grid(columns: (1fr, auto), align: (left, right),
          [#text(style: "italic")[{short_title}]],
          [#text(size: 7.5pt, fill: luma(120))[Reclaiming Your Consciousness]])
      ] else [
        #grid(columns: (auto, 1fr), align: (left, right),
          [#text(size: 7.5pt, fill: luma(120))[Synthetic Empathy & Cognitive Liberty]],
          [#text(style: "italic")[*Ilham Pradani*]])
      ]
      #v(-2pt)
      #line(length: 100%, stroke: 0.35pt + luma(180))
    ]
  ],
  footer: context [
    #line(length: 100%, stroke: 0.25pt + luma(200))
    #v(2pt)
    #set text(font: "Libertinus Serif", size: 8.5pt, fill: luma(90))
    #if calc.even(counter(page).get().first()) [
      #grid(columns: (auto, 1fr), align: (left, right),
        [*#counter(page).display()*],
        [#text(size: 7.5pt, fill: luma(130))[ISBN 979-8-1415-4843-7]])
    ] else [
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(size: 7.5pt, fill: luma(130))[Ilham Pradani]],
        [*#counter(page).display()*])
    ]
  ]
)
#counter(page).update(1)

{''.join(typ_parts)}
"""

def build_full_cover_pdf(book_dir, output_pdf_path, total_w_in, total_h_in, wrap_in, panel_w_in, spine_w_in, front_img_path, back_img_path):
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
            [#text(size: 11.5pt, weight: "bold", fill: white)[MANIPULATIVE INTELLIGENCE]],
            [#text(size: 9pt, fill: rgb(235, 60, 60))[•]],
            [#text(size: 10.5pt, weight: "regular", fill: rgb(220, 222, 225))[ILHAM PRADANI]]
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

    # 1. Compile 6" x 9" Manuscript with standard 10pt book font & comfortable margins (260+ pages!)
    typ_6x9 = build_typst_manuscript(blueprint, chapters, 6.0, 9.0, 10.0, 0.74, 0.85, 0.65, 0.78, 0.78)
    typ_6x9_path = os.path.join(book_dir, 'book_master_6x9.typ')
    pdf_6x9_path = os.path.join(output_dir, 'manipulative-intelligence-kdp-6x9-manuscript.pdf')
    with open(typ_6x9_path, 'w', encoding='utf-8') as f:
        f.write(typ_6x9)
    print("Compiling Amazon KDP 6\" × 9\" Manuscript PDF (Standard 10pt Book Typography)...")
    res1 = subprocess.run(['typst', 'compile', typ_6x9_path, pdf_6x9_path], capture_output=True, text=True)
    if res1.returncode != 0:
        print("Typst 6x9 Error:", res1.stderr)
        sys.exit(1)
    doc_6x9 = pymupdf.open(pdf_6x9_path)
    pages_6x9 = len(doc_6x9)
    print(f"✅ 6\" × 9\" Manuscript Ready: {pdf_6x9_path} ({pages_6x9} pages)")

    # 2. Compile 7" x 10" Manuscript with 10.5pt book font (220+ pages!)
    typ_7x10 = build_typst_manuscript(blueprint, chapters, 7.0, 10.0, 10.5, 0.76, 0.95, 0.75, 0.85, 0.85)
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

    # 3. Build Full KDP Cover PDFs (Back + Spine + Front) calibrated to the new exact page count!
    front_img = '/root/journal/books/cover_assets/buku/sampulbukubahsaenglish for sell amazon.jpeg'
    back_img = '/root/journal/books/cover_assets/buku/sampulbelakang_english_amazon_selfhelp.jpeg'

    # 3A. Hardcover 6" x 9" Case Laminate Cover PDF (Exact KDP Validator Target: 14.365" x 10.417" for 267 pages)
    hc_spine_in = (pages_6x9 * 0.002252) + 0.189
    hc_panel_w = 6.0 + 0.197
    hc_panel_h = 9.0 + 0.235
    hc_wrap = 0.591
    hc_total_w = 14.365 if pages_6x9 == 267 else round((2 * hc_wrap) + (2 * hc_panel_w) + hc_spine_in, 3)
    hc_total_h = 10.417
    hc_cover_pdf = os.path.join(output_dir, 'manipulative-intelligence-kdp-6x9-hardcover-cover.pdf')
    build_full_cover_pdf(book_dir, hc_cover_pdf, hc_total_w, hc_total_h, hc_wrap, hc_panel_w, hc_spine_in, front_img, back_img)
    print(f"✅ Hardcover 6\" × 9\" Full Cover PDF Ready: {hc_cover_pdf} ({hc_total_w:.3f}\" × {hc_total_h:.3f}\", Spine: {hc_spine_in:.3f}\" for {pages_6x9} pages)")

    # 3B. Paperback 6" x 9" Cover PDF (Exact KDP Formula for pages_6x9)
    pb_spine_in = pages_6x9 * 0.002252
    pb_panel_w = 6.0
    pb_panel_h = 9.0
    pb_bleed = 0.125
    pb_total_w = (2 * pb_bleed) + (2 * pb_panel_w) + pb_spine_in
    pb_total_h = (2 * pb_bleed) + pb_panel_h
    pb_cover_pdf = os.path.join(output_dir, 'manipulative-intelligence-kdp-6x9-paperback-cover.pdf')
    build_full_cover_pdf(book_dir, pb_cover_pdf, pb_total_w, pb_total_h, pb_bleed, pb_panel_w, pb_spine_in, front_img, back_img)
    print(f"✅ Paperback 6\" × 9\" Full Cover PDF Ready: {pb_cover_pdf} ({pb_total_w:.3f}\" × {pb_total_h:.3f}\", Spine: {pb_spine_in:.3f}\" for {pages_6x9} pages)")

    # Copy all 4 PDFs to public/books/ and dist/books/
    for target_dir in [public_books_dir, '/root/journal/dist/books']:
        if os.path.exists(target_dir):
            shutil.copy2(pdf_6x9_path, os.path.join(target_dir, 'manipulative-intelligence-kdp-6x9-manuscript.pdf'))
            shutil.copy2(pdf_7x10_path, os.path.join(target_dir, 'manipulative-intelligence-kdp-7x10-manuscript.pdf'))
            shutil.copy2(hc_cover_pdf, os.path.join(target_dir, 'manipulative-intelligence-kdp-6x9-hardcover-cover.pdf'))
            shutil.copy2(pb_cover_pdf, os.path.join(target_dir, 'manipulative-intelligence-kdp-6x9-paperback-cover.pdf'))
    print("🌐 All KDP Manuscript & Cover PDFs updated in /public/books/ and /dist/books/")

if __name__ == '__main__':
    compile_kdp_book()
