#!/usr/bin/env python3
"""
PT CHAIN ASIA CONECT - Amazon Kindle KDP Reflowable EPUB 3 Engine
Compiles:
1. Reflowable EPUB 3 with MathML, Clean Booktabs CSS, and Amazon KDP Compatibility
2. Standalone Cover JPEG for Kindle eBook Upload
"""

import json
import os
import re
import shutil
import subprocess
import html
import importlib.util

spec = importlib.util.spec_from_file_location('compile_kdp_typst', '/root/journal/scripts/compile-kdp-typst.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
get_english_math_explanation = mod.get_english_math_explanation

def clean_chapter_markdown_for_epub(md_content):
    if not md_content:
        return ''

    # 1. Process Codeblocks / Diagrams
    def format_codeblock(m):
        raw_code = m.group(1).strip()
        escaped_code = html.escape(raw_code)
        return f'\n\n<div class="diagram-box"><pre><code>{escaped_code}</code></pre></div>\n\n'

    t = re.sub(r'```(?:[a-zA-Z0-9_-]*\n)?([\s\S]*?)```', format_codeblock, md_content)

    # 2. Process Display Math and inject Intuitive Conceptual Note
    def format_display_math(m):
        raw_eq = (m.group(1) or m.group(2) or '').strip()
        explanation = get_english_math_explanation(raw_eq)
        exp_html = ""
        if explanation:
            # Clean "Intuitive Conceptual Note:" prefix for bold styling
            note_body = explanation.replace("Intuitive Conceptual Note:", "").strip()
            exp_html = f'\n\n<div class="math-note"><strong>Intuitive Conceptual Note:</strong> {note_body}</div>\n'
        return f'\n\n$$\n{raw_eq}\n$$\n{exp_html}\n'

    math_pattern = re.compile(r'\$\$(.*?)\$\$|\\\[(.*?)\\\]', re.DOTALL)
    t = math_pattern.sub(format_display_math, t)

    # 3. Clean Headings and Subheadings
    lines = t.split('\n')
    processed_lines = []
    for line in lines:
        s = line.strip()
        if not s:
            processed_lines.append('')
            continue

        if re.match(r'^[#=]{1,6}\s*', s):
            # Skip duplicate main chapter heading (we generate it uniformly)
            if re.match(r'^#\s+(?:Bab|Chapter)\s+\d+', s, re.IGNORECASE):
                continue

            m_h = re.match(r'^([#=]+)', s)
            h_len = len(m_h.group(1)) if m_h else 2
            raw_title = re.sub(r'^[#=\s]+', '', s).strip()
            raw_title = re.sub(r'[#=\s]+$', '', raw_title).strip()
            if not raw_title:
                continue

            # Strip brackets [ ... ] and prompt leaks
            clean_title = re.sub(r'\[(.*?)\]', r'\1', raw_title).strip()

            if h_len >= 4 or 'Selected References' in clean_title or 'Rujukan Terpilih' in clean_title:
                clean_title = re.sub(r'^\d+\.\d+\.\d+(?:\.\d+)?\s*', '', clean_title).strip()
                clean_title = clean_title.replace('Rujukan Terpilih Sub-bab', 'Selected References — Section')
                processed_lines.append(f'#### {clean_title}')
            elif h_len == 3:
                clean_title = re.sub(r'^\d+\.\d+\.\d+(?:\.\d+)?\s*', '', clean_title).strip()
                processed_lines.append(f'### {clean_title}')
            else:
                clean_title = re.sub(r'^(?:Sub-bab|Section)\s+\d+\.\d+:\s*', '', clean_title, flags=re.IGNORECASE).strip()
                processed_lines.append(f'## {clean_title}')
            continue

        processed_lines.append(line)

    return '\n'.join(processed_lines)

def build_epub_css():
    return """/* EPUB 3 Styling for Amazon Kindle & Reflowable Readers */
@namespace epub "http://www.idpf.org/2007/ops";

body {
  font-family: "Georgia", "Merriweather", "Times New Roman", serif;
  line-height: 1.65;
  color: #1a202c;
  margin: 4% 5%;
  text-align: justify;
}

h1, h2, h3, h4 {
  font-family: "Helvetica Neue", "Arial", sans-serif;
  font-weight: bold;
  line-height: 1.25;
  color: #111827;
  page-break-after: avoid;
  break-after: avoid;
}

h1 {
  font-size: 1.85em;
  margin-top: 2.2em;
  margin-bottom: 0.9em;
  text-align: center;
  page-break-before: always;
  break-before: page;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.4em;
}

h2 {
  font-size: 1.35em;
  margin-top: 1.8em;
  margin-bottom: 0.6em;
  color: #1f2937;
}

h3 {
  font-size: 1.15em;
  margin-top: 1.4em;
  margin-bottom: 0.4em;
  color: #374151;
}

h4 {
  font-size: 1.0em;
  margin-top: 1.2em;
  margin-bottom: 0.4em;
  font-style: italic;
  color: #4b5563;
}

p {
  margin-top: 0;
  margin-bottom: 0.85em;
  text-indent: 1.5em;
}

/* Remove indent for first paragraph after headings, math, or boxes */
h1 + p, h2 + p, h3 + p, h4 + p, div + p, table + p, blockquote + p {
  text-indent: 0;
}

/* Title Page & Front Matter */
.title-page-container {
  text-align: center;
  page-break-before: always;
  break-before: page;
  margin: 15% 0;
}

.main-title {
  font-size: 2.2em;
  font-weight: bold;
  letter-spacing: 0.05em;
  margin-bottom: 0.4em;
  color: #0f172a;
}

.main-subtitle {
  font-size: 1.3em;
  color: #334155;
  margin-bottom: 0.8em;
}

.main-tagline {
  font-size: 0.95em;
  font-style: italic;
  color: #64748b;
  margin-bottom: 2.5em;
  line-height: 1.45;
}

.author-name {
  font-size: 1.4em;
  font-weight: bold;
  margin-bottom: 0.2em;
  color: #0f172a;
}

.author-meta {
  font-size: 0.85em;
  color: #64748b;
  margin-bottom: 0.4em;
}

.publisher-name {
  font-size: 0.9em;
  color: #475569;
  margin-top: 3.5em;
}

/* Copyright Page */
.copyright-container {
  font-size: 0.85em;
  line-height: 1.5;
  color: #475569;
  margin-top: 25%;
  page-break-before: always;
  break-before: page;
}

.copyright-container p {
  text-indent: 0;
  margin-bottom: 0.6em;
}

/* Intuitive Conceptual Note Box */
.math-note {
  margin: 1.0em 0 1.4em 0;
  padding: 0.8em 1.2em;
  background-color: #f8fafc;
  border-left: 3.5px solid #3b82f6;
  border-radius: 0 4px 4px 0;
  font-size: 0.9em;
  color: #334155;
  line-height: 1.5;
  text-align: left;
}

.math-note strong {
  color: #1e40af;
}

/* Diagram Pre Box */
.diagram-box {
  margin: 1.5em 0;
  background-color: #0f172a;
  color: #f1f5f9;
  border-radius: 6px;
  padding: 0.8em 1.2em;
  overflow-x: auto;
}

.diagram-box pre {
  margin: 0;
  font-family: "Courier New", Courier, monospace;
  font-size: 0.82em;
  line-height: 1.35;
  white-space: pre;
}

/* Tables (Booktabs Standard) */
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.6em 0;
  font-size: 0.88em;
  border-top: 2px solid #0f172a;
  border-bottom: 2px solid #0f172a;
}

th {
  border-bottom: 1px solid #0f172a;
  padding: 0.6em 0.8em;
  font-weight: bold;
  text-align: left;
  background-color: #f8fafc;
}

td {
  padding: 0.5em 0.8em;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
  vertical-align: top;
}

tr:last-child td {
  border-bottom: none;
}

/* MathML Spacing */
math {
  font-size: 1.05em;
}

/* Epilogue / Author Bio */
.author-bio-box {
  margin-top: 2.5em;
  padding: 1.2em 1.5em;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.92em;
}

.author-bio-box h3 {
  margin-top: 0;
}
"""

def compile_kindle_epub():
    bundle_path = '/root/journal/books/cache/synthetic-empathy-english-edition/book_bundle.json'
    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle = json.load(f)

    blueprint = bundle['blueprint']
    chapters = bundle['chapters']

    book_dir = '/root/journal/books/cache/synthetic-empathy-english-edition'
    output_dir = '/root/journal/books/output'
    public_books_dir = '/root/journal/public/books'
    dist_books_dir = '/root/journal/dist/books'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(public_books_dir, exist_ok=True)
    if os.path.exists('/root/journal/dist'):
        os.makedirs(dist_books_dir, exist_ok=True)

    cover_img_path = '/root/journal/books/cover_assets/buku/sampulbukubahsaenglish for sell amazon.jpeg'

    # 1. Generate Custom CSS
    css_path = os.path.join(book_dir, 'kindle_epub.css')
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(build_epub_css())

    # 2. Build Markdown Document with YAML Metadata
    md_parts = []

    # Frontmatter YAML
    yaml_header = f"""---
title: "Manipulative Intelligence: Reclaiming Your Consciousness in the Age of AI"
subtitle: "{blueprint['subtitle']}"
author: "{blueprint['author']}"
publisher: "{blueprint['affiliation']}"
rights: "Copyright © {blueprint['year']} by {blueprint['author']}. All Rights Reserved."
lang: "en"
description: "A comprehensive interdisciplinary monograph exploring synthetic empathy, the cognitive psychology of AI language, manipulative engagement loops, and the emergence of cognitive liberty as a fundamental human right."
subject:
  - Artificial Intelligence
  - Cognitive Psychology
  - Cyberlaw
  - Cognitive Liberty
  - Technology and Society
---

"""
    md_parts.append(yaml_header)

    # Title Page Section
    title_page_html = f"""
<div class="title-page-container">
  <div class="main-title">MANIPULATIVE INTELLIGENCE</div>
  <div class="main-subtitle">Reclaiming Your Consciousness in the Age of AI</div>
  <div class="main-tagline">{blueprint['subtitle']}</div>
  <div class="author-name">{blueprint['author']}</div>
  <div class="author-meta">ORCID: {blueprint['orcid']}</div>
  <div class="author-meta">{blueprint['affiliation']}</div>
  <div class="publisher-name">Independently published &bull; First International Edition</div>
</div>

"""
    md_parts.append(title_page_html)

    # Copyright Page Section
    copyright_page_html = f"""
<div class="copyright-container">
  <p><strong>MANIPULATIVE INTELLIGENCE: Reclaiming Your Consciousness in the Age of AI</strong></p>
  <p><em>{blueprint['subtitle']}</em></p>
  <p>Author: {blueprint['author']} (ORCID: {blueprint['orcid']})</p>
  <p>Research Affiliation: {blueprint['affiliation']}</p>
  <p>Permanent Scholarly Record: CERN Zenodo (DataCite DOI: 10.5281/zenodo.24106942)</p>
  <p>Copyright &copy; {blueprint['year']} by {blueprint['author']}. All Rights Reserved.</p>
  <p>Imprint: Independently published.</p>
  <p>No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without prior written permission from the author, except for brief quotations embodied in critical reviews and academic citations.</p>
</div>

"""
    md_parts.append(copyright_page_html)

    # Preface
    preface_clean = clean_chapter_markdown_for_epub(blueprint.get('preface', ''))
    md_parts.append(f"""
# Preface: Algorithmic Architecture and Human Vulnerability

{preface_clean}

<p style="text-align: right; font-style: italic; margin-top: 2em;">
  <strong>{blueprint['author']}</strong><br/>
  Jakarta &amp; Krui, Indonesia
</p>

""")

    # Chapters 1 to 10
    for ch in chapters:
        ch_title_clean = re.sub(r'^(?:Bab|Chapter)\s+\d+:\s*', '', ch['chapterTitle'], flags=re.IGNORECASE).strip()
        cleaned_body = clean_chapter_markdown_for_epub(ch['contentMarkdown'])
        md_parts.append(f"""
# Chapter {ch['chapterNumber']}: {ch_title_clean}

{cleaned_body}

""")

    # About the Author & Epilogue
    md_parts.append(f"""
# About the Author

<div class="author-bio-box">
  <h3>Ilham Pradani</h3>
  <p><strong>Ilham Pradani</strong> (ORCID: <a href="https://orcid.org/0009-0008-1310-6169">0009-0008-1310-6169</a>) is an Indonesian researcher and technology analyst specializing in computational linguistics, cognitive psychology, algorithmic governance, and cyberlaw. He serves as lead researcher at the <strong>PT CHAIN ASIA CONECT Research &amp; Development Division</strong>, where he investigates the intersections of artificial intelligence architecture, contractual validity under civil law, and personal data sovereignty.</p>
  <p>His academic work spans empirical regional studies, cold-chain logistical modeling, and the formulation of <em>cognitive liberty</em> as a foundational right against algorithmic behavioral engineering. His research monographs and open-access working papers are indexed and archived in permanent scholarly repositories including CERN Zenodo, Open Science Framework (OSF), and the Journal of Coastal Frontiers &amp; Applied Development (JCFAD).</p>
</div>

""")

    full_md_path = os.path.join(book_dir, 'book_epub_master.md')
    with open(full_md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_parts))

    print(f"📖 Master Markdown ready: {full_md_path} ({len(md_parts)} parts)")

    # 3. Compile with Pandoc into EPUB 3
    epub_output_path = os.path.join(output_dir, 'manipulative-intelligence-kindle-ebook.epub')
    cover_output_path = os.path.join(output_dir, 'manipulative-intelligence-kindle-cover.jpeg')

    cmd = [
        'pandoc',
        '--from=markdown+yaml_metadata_block+smart',
        '--to=epub3',
        '--mathml',
        '--toc',
        '--toc-depth=2',
        f'--epub-cover-image={cover_img_path}',
        f'--css={css_path}',
        '--split-level=1',
        '-o', epub_output_path,
        full_md_path
    ]

    print("🚀 Compiling Amazon Kindle Reflowable EPUB 3...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("❌ Pandoc Error:", res.stderr)
        return False

    print(f"✅ Kindle EPUB 3 Generated: {epub_output_path} ({os.path.getsize(epub_output_path):,} bytes)")

    # 4. Copy standalone cover JPEG for KDP upload
    shutil.copy2(cover_img_path, cover_output_path)
    print(f"✅ Standalone Cover JPEG Ready: {cover_output_path}")

    # 5. Copy to public/books and dist/books
    for target_dir in [public_books_dir, dist_books_dir]:
        if os.path.exists(target_dir):
            shutil.copy2(epub_output_path, os.path.join(target_dir, 'manipulative-intelligence-kindle-ebook.epub'))
            shutil.copy2(cover_output_path, os.path.join(target_dir, 'manipulative-intelligence-kindle-cover.jpeg'))

    print("🌐 Kindle EPUB and Cover synced to /public/books/ and /dist/books/")
    return True

if __name__ == '__main__':
    compile_kindle_epub()

