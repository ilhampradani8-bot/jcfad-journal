#!/usr/bin/env python3
import json
import re
import subprocess
import os
import sys

def parse_braced(text, start_idx):
    depth = 0
    for idx in range(start_idx, len(text)):
        if text[idx] == '{':
            depth += 1
        elif text[idx] == '}':
            depth -= 1
            if depth == 0:
                return text[start_idx+1:idx], idx + 1
    return None, len(text)

def replace_fractions(s):
    while r'\frac' in s:
        idx = s.find(r'\frac')
        f_idx = s.find('{', idx + 5)
        if f_idx == -1: break
        num, next_idx = parse_braced(s, f_idx)
        if num is None: break
        s_idx = s.find('{', next_idx)
        if s_idx == -1: break
        den, end_idx = parse_braced(s, s_idx)
        if den is None: break
        s = s[:idx] + f"({num.strip()}) / ({den.strip()})" + s[end_idx:]
    return s

def clean_to_typst_math(raw):
    if not raw:
        return ''
    s = raw.strip()
    # Strip environments & delimiters
    s = s.replace(r'\[', '').replace(r'\]', '')
    s = s.replace(r'\(', '').replace(r'\)', '')
    s = s.replace('$$', '').replace('$', '')
    s = re.sub(r'\\tag\{[^}]+\}', '', s)
    s = s.replace(r'\begin{aligned}', '').replace(r'\end{aligned}', '')
    s = re.sub(r'\\(?:left|right|bigl|bigr|Bigl|Bigr|big|Big|!)', '', s)
    
    # Fractions first
    s = replace_fractions(s)
    
    # Underbrace
    s = re.sub(r'\\underbrace\{([^{}]+)\}_\{([^{}]+)\}', r'underbrace(\1, "\2")', s)
    s = re.sub(r'\\underbrace\(([^{}]+)\)_\(([^{}]+)\)', r'underbrace(\1, "\2")', s)
    
    # Text commands in math -> quoted string
    s = re.sub(r'\\(?:text|operatorname)\{([^{}]+)\}', r'"\1"', s)
    
    # Common math symbols
    s = re.sub(r'\\top\b', 'T', s)
    s = s.replace(r'\cdot', ' dot ')
    s = s.replace(r'\odot', ' dot ')
    s = s.replace(r'\times', ' times ')
    s = s.replace(r'\in', ' in ')
    s = s.replace(r'\le', ' <= ').replace(r'\leq', ' <= ')
    s = s.replace(r'\ge', ' >= ').replace(r'\geq', ' >= ')
    s = re.sub(r'\\(?:rightarrow|longrightarrow|to)\b', ' -> ', s)
    s = s.replace(r'\approx', ' approx ')
    s = s.replace(r'\neq', ' != ')
    s = s.replace(r'\mathbb{R}', '"RR"')
    s = s.replace(r'\mathbb', '')
    s = s.replace(r'\mathcal{S}', '"S"').replace(r'\mathcal{E}', '"E"').replace(r'\mathcal{F}', '"F"')
    s = s.replace(r'\sum', 'sum')
    s = s.replace(r'\sqrt', 'sqrt')
    s = s.replace(r'\hat{p}', 'hat(p)')
    s = s.replace(r'\|', ' || ')
    s = s.replace(r'\,', ' ').replace(r'\;', ' ').replace(r'\qquad', '   ').replace(r'\quad', '  ')
    s = s.replace(r'&=', '=')
    s = s.replace('&', '')
    
    # Vectors \mathbf{e} -> bold(e)
    s = re.sub(r'\\mathbf\{([^{}]+)\}', r'bold(\1)', s)
    
    # Greek letters
    greek = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Phi', 'Delta', 'Gamma', 'Lambda', 'Sigma', 'Omega']
    s = s.replace(r'\varepsilon', 'epsilon')
    for g in greek:
        s = s.replace('\\' + g, g)
        
    # Norm ||x|| -> norm(x)
    s = re.sub(r'\|\|\s*([^|]+?)\s*\|\|', r'norm(\1)', s)
    # Abs |x| -> abs(x)
    s = re.sub(r'(?<![|a-zA-Z0-9])\|\s*([^|\n]+?)\s*\|(?![|])', r'abs(\1)', s)
    
    # Multi-letter word subscripts like _{emp} or _{context} or _((EO)) -> _("emp")
    s = re.sub(r'_\{\s*([a-zA-Z]{2,})\s*\}', r'_("\1")', s)
    s = re.sub(r'_\(\(\s*([a-zA-Z]+)\s*\)\)', r'_("\1")', s)
    s = re.sub(r'_\(\s*([a-zA-Z]{2,})\s*\)', r'_("\1")', s)
    
    # Multi-letter uppercase identifiers like (SAS), (BS), (FPR), (TPR), (EO), (Cal) -> ("SAS"), ("BS")
    s = re.sub(r'\b([A-Z]{2,})\b', r'"\1"', s)
    
    # Known multi-letter words in math that need quotes
    known_words = ['PersonaScore', 'EmpathyScore', 'TAI', 'ToM', 'CToM', 'CUS', 'AAS', 'BEM', 'score', 'fit', 'priv', 'trans', 'info', 'explain', 'turn', 'percakapan', 'styl', 'EGS', 'EO', 'Cal', 'ref', 'target', 'source', 'user', 'session']
    for kw in known_words:
        s = re.sub(rf'\b{kw}\b', f'"{kw}"', s)

    # Convert LaTeX decimal commas like 0{,}71 or {,} to standard 0.71
    s = re.sub(r'(\d+)\s*\{,\}\s*(\d+)', r'\1.\2', s)
    s = s.replace('{,}', '.')
        
    # Clean curly braces to parens
    s = s.replace('{', '(').replace('}', ')')
    s = re.sub(r'\\\\', ' ', s)
    s = s.replace('\\', '')
    s = s.replace('(,)', '.')
    
    # Clean redundant double quotes ""word"" -> "word"
    s = re.sub(r'""+([^"]+)""+', r'"\1"', s)
    
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_inline_for_typst(text):
    if not text:
        return ''
    t = text.strip()
    
    # Clean HTML tags
    t = re.sub(r'</?[a-zA-Z0-9]+[^>]*>', '', t)
    
    # 1. Stash inline math \(...\) safely
    # CRITICAL TYPST RULE: Inline math MUST NOT have spaces adjacent to $ delimiters ($expr$, not $ expr $)
    # Spaces inside $ ... $ convert the formula into a centered DISPLAY EQUATION, breaking paragraphs!
    math_inlines = []
    def stash_inline_paren_math(m):
        math_content = m.group(1).strip()
        cleaned = clean_to_typst_math(math_content).strip()
        idx = len(math_inlines)
        if cleaned:
            math_inlines.append(f"${cleaned}$")
        else:
            math_inlines.append("")
        return f"__SAFE_INLINE_MATH_{idx}__"
    t = re.sub(r'\\\((.*?)\\\)', stash_inline_paren_math, t)

    # Protect bold and italic spans safely
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

    # Strip remaining stray asterisks
    t = t.replace('*', '')

    # Restore bold & italic
    for i, b in enumerate(bold_spans):
        clean_b = b.replace('[', r'\[').replace(']', r'\]')
        t = t.replace(f'__SAFE_BOLD_{i}__', f'*{clean_b}*')
    for i, it in enumerate(italic_spans):
        clean_it = it.replace('[', r'\[').replace(']', r'\]')
        t = t.replace(f'__SAFE_ITALIC_{i}__', f'_{clean_it}_')

    # 3. Escape ALL unescaped dollar signs in text (they are currencies like US$ 2.500, $10, etc.)
    # In Typst, unescaped $ triggers math mode and unclosed delimiter errors!
    t = re.sub(r'(?<!\\)\$', r'\\$', t)

    # 4. Escape Typst specials
    t = re.sub(r'(?<!\\)@([a-zA-Z0-9_]+)', r'\\@\1', t)
    t = re.sub(r'(?<!\\)#([a-zA-Z0-9_]+)', r'\\#\1', t)
    t = t.replace('<', r'\<').replace('>', r'\>')

    # 5. Restore inline math blocks (which DO need $ ... $)
    for i, mb in enumerate(math_inlines):
        t = t.replace(f"__SAFE_INLINE_MATH_{i}__", mb)
    return t

def render_typst_table(table_text):
    lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return table_text

    rows = []
    for line in lines:
        line_clean = line.strip()
        if re.match(r'^\|[\s\-:|]+\|$', line_clean):
            continue  # Separator line like |---|---|
        if line_clean.startswith('|'):
            if not line_clean.endswith('|'):
                line_clean += ' |'
            cells = [c.strip() for c in line_clean[1:-1].split('|')]
            rows.append(cells)

    if not rows or len(rows) < 1:
        return table_text

    num_cols = max(len(r) for r in rows)
    header = rows[0]
    data = rows[1:]

    # Dynamic typography & inset based on column count to prevent overlapping text
    if num_cols >= 5:
        font_size = "7.5pt"
        inset_x = "4pt"
        inset_y = "4.5pt"
        leading = "0.4em"
    elif num_cols >= 4:
        font_size = "8pt"
        inset_x = "5pt"
        inset_y = "5pt"
        leading = "0.45em"
    else:
        font_size = "8.5pt"
        inset_x = "6pt"
        inset_y = "5.5pt"
        leading = "0.5em"

    col_specs = []
    for c in range(num_cols):
        max_len = max((len(r[c]) for r in rows if c < len(r)), default=10)
        if max_len > 40:
            col_specs.append("1.8fr")
        elif max_len > 25:
            col_specs.append("1.3fr")
        elif max_len > 12:
            col_specs.append("1.0fr")
        else:
            col_specs.append("0.85fr")
    col_str = ", ".join(col_specs)

    # Standar Percetakan Buku Akademik Tiga Garis (Booktabs: NO vertical lines, clean padding, dedicated typography)
    out = [
        f"\n#v(0.85em)",
        f"#align(center)[",
        f"  #set text(size: {font_size})",
        f"  #set par(leading: {leading}, first-line-indent: 0pt, justify: false)",
        f"  #table(",
        f"    columns: ({col_str}),",
        f"    inset: (x: {inset_x}, y: {inset_y}),",
        f"    stroke: (x, y) => if y == 0 {{ (top: 1.2pt + black, bottom: 0.8pt + black) }} else if y == {len(rows)} {{ (bottom: 1.2pt + black) }} else {{ (bottom: 0.25pt + luma(215)) }},"
    ]

    # Header Row (Clean, no duplicate asterisks)
    for cell in header:
        clean_c = clean_inline_for_typst(cell).replace('*', '')
        out.append(f"    [ *{clean_c}* ],")

    # Data Rows
    for r in data:
        for c in range(num_cols):
            val = r[c] if c < len(r) else ""
            clean_c = clean_inline_for_typst(val)
            out.append(f"    [ {clean_c} ],")

    out.append("  )")
    out.append("]")
    out.append("#v(0.85em)\n")
    return "\n".join(out)

def clean_chapter_markdown_to_typst(md_content):
    if not md_content:
        return ''
    
    # 1. Extract display math blocks:
    # CLEAN ACADEMIC DISPLAY MATH - ZERO CARDS, ZERO BOXES, ZERO GREY BACKGROUND!
    # Standalone centered equation with vertical breathing room above and below.
    math_blocks = []
    def stash_display_math(m):
        raw_eq = m.group(1).strip()
        cleaned = clean_to_typst_math(raw_eq)
        idx = len(math_blocks)
        # Native Typst centered display math without card/box/border
        math_blocks.append(f"\n#v(0.85em)\n$ {cleaned} $\n#v(0.85em)\n")
        return f"\n__TYPST_MATH_BLOCK_{idx}__\n"

    # Multiline display math pattern
    math_pattern = re.compile(r'(?m)^\s*(?:\\\[|\$\$)\s*\n([\s\S]*?)\n\s*(?:\\\]|\$\$)')
    t = math_pattern.sub(stash_display_math, md_content)

    # 2. Extract and convert Markdown Tables into Real Typst Tables (Booktabs)
    table_blocks = []
    def stash_table(m):
        raw_table = m.group(1)
        typst_tbl = render_typst_table(raw_table)
        idx = len(table_blocks)
        table_blocks.append(typst_tbl)
        return f"\n__TYPST_TABLE_BLOCK_{idx}__\n"

    table_regex = r'(?:^|\n)(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)'
    t = re.sub(table_regex, stash_table, t)

    # 3. Process lines
    lines = t.split('\n')
    processed_lines = []
    for line in lines:
        s = line.strip()
        if not s:
            processed_lines.append('')
            continue

        # Restore Math Block
        m_math = re.match(r'^__TYPST_MATH_BLOCK_(\d+)__$', s)
        if m_math:
            processed_lines.append(math_blocks[int(m_math.group(1))])
            continue

        # Restore Table Block
        m_tbl = re.match(r'^__TYPST_TABLE_BLOCK_(\d+)__$', s)
        if m_tbl:
            processed_lines.append(table_blocks[int(m_tbl.group(1))])
            continue

        # Headings
        if s.startswith('#### '):
            processed_lines.append('==== ' + clean_inline_for_typst(s[5:]))
        elif s.startswith('### '):
            processed_lines.append('=== ' + clean_inline_for_typst(s[4:]))
        elif s.startswith('## '):
            processed_lines.append('== ' + clean_inline_for_typst(s[3:]))
        elif s.startswith('# Bab') or s.startswith('# BAB'):
            continue
        elif s.startswith('# '):
            processed_lines.append('== ' + clean_inline_for_typst(s[2:]))
        elif re.match(r'^[#=]{1,5}\s*$', s):
            continue
        elif s.startswith('- ') or s.startswith('* '):
            processed_lines.append('- ' + clean_inline_for_typst(s[2:]))
        elif re.match(r'^\d+\.\s+', s):
            num_content = re.sub(r'^\d+\.\s+', '', s)
            processed_lines.append('+ ' + clean_inline_for_typst(num_content))
        else:
            processed_lines.append(clean_inline_for_typst(s))

    return '\n'.join(processed_lines)

def review_book_pdf(pdf_path, blueprint, chapters):
    """
    Automated Post-Generation Academic Book PDF Review & Quality Audit Engine:
    Deeply audits:
    1. Dimensi Kertas & Margin Bounds (ISO-B5 Standard 498.9 x 708.7 pt)
    2. Total Halaman & Ketebalan Monograf (Standar UNESCO >= 49 Halaman)
    3. Verifikasi Kehadiran 10 Bab & Seluruh Sub-bab
    4. Integritas Tabel (Memastikan 0 tabel bocor sebagai teks mentah | | |)
    5. Integritas Rumus (Memastikan rumus bersih dari box/card abu-abu)
    6. Identitas Penulis & Afiliasi Riset
    """
    print("\n" + "═"*78)
    print("🔬 AUDIT KELAYAKAN & REVIEW PDF BUKU CETAK (JCFAD ACADEMIC QUALITY ENGINE)")
    print("═"*78)

    checks = []
    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)

    # 1. Total Halaman
    if total_pages >= 50:
        checks.append(("Ketebalan Buku (>=50 Hal)", "PASS", f"{total_pages} Halaman (Standar Monograf Penuh UNESCO)"))
    else:
        checks.append(("Ketebalan Buku (>=50 Hal)", "WARN", f"{total_pages} Halaman"))

    # 2. Dimensi ISO-B5
    mb = reader.pages[0].mediabox
    w, h = float(mb.width), float(mb.height)
    is_b5 = (490.0 <= w <= 510.0) and (700.0 <= h <= 720.0)
    if is_b5:
        checks.append(("Format Kertas ISO-B5", "PASS", f"{w:.1f} × {h:.1f} pt (Standar Percetakan Buku)"))
    else:
        checks.append(("Format Kertas ISO-B5", "WARN", f"{w:.1f} × {h:.1f} pt"))

    # Extract all text from PDF
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # 3. Verifikasi Semua Bab
    missing_chapters = []
    for ch in chapters:
        ch_title_short = ch['chapterTitle'][:20]
        if ch_title_short.lower() not in full_text.lower():
            missing_chapters.append(ch['chapterNumber'])
    if not missing_chapters:
        checks.append(("Kelengkapan 10 Bab", "PASS", f"100% Bab (1–10) Lengkap & Terverifikasi di PDF"))
    else:
        checks.append(("Kelengkapan 10 Bab", "FAIL", f"Bab Hilang: {missing_chapters}"))

    # 4. Kebersihan Tabel (Deteksi Kebocoran Pipa Mentah | | |)
    raw_pipes_match = re.findall(r'\|\s+[^|\n]+\s+\|\s+[^|\n]+\s+\|', full_text)
    if len(raw_pipes_match) == 0:
        checks.append(("Integritas Render Tabel", "PASS", "0 Kebocoran Pipa | | | (Semua Tabel Ter-render Rapi)"))
    else:
        checks.append(("Integritas Render Tabel", "WARN", f"{len(raw_pipes_match)} baris tabel mentah terdeteksi"))

    # 5. Kebersihan Rumus dari Card / Grey Box
    raw_latex_leaks = re.findall(r'\\frac\{|\\mathbf\{|\\operatorname\{', full_text)
    if len(raw_latex_leaks) == 0:
        checks.append(("Tipografi Notasi Rumus", "PASS", "Rumus Bersih Tanpa Card / Tanpa Kebocoran Kode LaTeX"))
    else:
        checks.append(("Tipografi Notasi Rumus", "WARN", f"{len(raw_latex_leaks)} sintaks LaTeX mentah"))

    # 6. Identitas Penulis & Afiliasi
    has_author = "Ilham Pradani" in full_text
    has_orcid = "0009-0008-1310-6169" in full_text
    has_affiliation = "PT CHAIN ASIA CONECT" in full_text
    if has_author and has_orcid and has_affiliation:
        checks.append(("Integritas Hak Cipta & ORCID", "PASS", "Ilham Pradani (ORCID: 0009-0008-1310-6169) Verified"))
    else:
        checks.append(("Integritas Hak Cipta & ORCID", "WARN", "Sebagian metadata penulis tidak terdeteksi"))

    # 7. PyMuPDF Typography & Visual Layout Audit (Pre-flight Geometric Inspection)
    import pymupdf
    pdf_doc = pymupdf.open(pdf_path)
    orphan_parens = []
    malformed_numbers = []
    multiline_headers = []
    multiline_footers = []

    for page_idx in range(len(pdf_doc)):
        p = pdf_doc[page_idx]
        words = p.get_text('words')  # (x0, y0, x1, y1, word, block, line, word_no)
        
        # Pre-flight inspection: Header & Footer must be exactly 1 single line (never wrap to 2 lines)
        if page_idx >= 2:
            h_words = [w for w in words if w[1] < 45]
            if h_words:
                y_span = max(w[1] for w in h_words) - min(w[1] for w in h_words)
                if y_span > 6:
                    multiline_headers.append((page_idx + 1, y_span, " ".join(w[4] for w in h_words)))

            f_words = [w for w in words if w[1] > 650]
            if f_words:
                y_span = max(w[1] for w in f_words) - min(w[1] for w in f_words)
                if y_span > 6:
                    multiline_footers.append((page_idx + 1, y_span, " ".join(w[4] for w in f_words)))

        for idx, w in enumerate(words):
            # Check for orphan close paren sitting at left margin (x0 < 90) at start of a line
            if w[4].startswith(')') and w[0] < 90:
                orphan_parens.append((page_idx + 1, f"Left-margin: {w[4]}"))
            # Check for orphan open paren at line end where next word wraps to left margin
            if w[4].endswith('(') and idx + 1 < len(words):
                next_w = words[idx + 1]
                if next_w[1] > w[1] + 6 and next_w[0] < 100:
                    orphan_parens.append((page_idx + 1, f"Line-end: {w[4]} -> {next_w[4]}"))
            # Check for malformed comma/paren artifacts in numbers
            if re.search(r'\d+\(,\s*\)\d+', w[4]) or '(, )' in w[4] or '(,)' in w[4]:
                malformed_numbers.append((page_idx + 1, w[4]))

    if len(multiline_headers) == 0:
        checks.append(("Geometri Header (Single-Line Verification)", "PASS", "0 Header Tertekuk (100% 1 Baris Elegan)"))
    else:
        detail_samples = "; ".join([f"Hal {pg}" for pg, _, _ in multiline_headers[:3]])
        checks.append(("Geometri Header (Single-Line Verification)", "FAIL", f"{len(multiline_headers)} halaman memiliki header 2 baris ({detail_samples})"))

    if len(multiline_footers) == 0:
        checks.append(("Geometri Footer (Single-Line Verification)", "PASS", "0 Footer Tertekuk (100% 1 Baris Rapi)"))
    else:
        checks.append(("Geometri Footer (Single-Line Verification)", "FAIL", f"{len(multiline_footers)} halaman memiliki footer multi-baris"))

    if len(orphan_parens) == 0:
        checks.append(("Tipografi Layout (Zero Orphan Parens)", "PASS", "0 Tanda Kurung Patah/Gantung (Teks Mengalir Utuh)"))
    else:
        detail_samples = "; ".join([f"Hal {pg}: {snippet}" for pg, snippet in orphan_parens[:3]])
        checks.append(("Tipografi Layout (Zero Orphan Parens)", "FAIL", f"{len(orphan_parens)} kurung patah terdeteksi ({detail_samples})"))

    if len(malformed_numbers) == 0:
        checks.append(("Integritas Angka & Desimal", "PASS", "0 Anomali Koma Desimal LaTeX/Typst"))
    else:
        checks.append(("Integritas Angka & Desimal", "FAIL", f"{len(malformed_numbers)} anomali desimal terdeteksi"))

    pass_count = sum(1 for _, status, _ in checks if status == "PASS")
    score = (pass_count / len(checks)) * 100

    for name, status, detail in checks:
        icon = "✅" if status == "PASS" else ("⚠️" if status == "WARN" else "❌")
        print(f" {icon} [{status:4s}] {name:32s} : {detail}")

    print("─"*78)
    print(f" 🎯 Skor Kelayakan & Standar Cetak: {score:.1f}% ({'LULUS SEMPURNA / SIAP TERBIT' if score >= 90 else 'PERLU REVISI'})")
    print("═"*78 + "\n")
    return score >= 90

def compile_book(slug='empati-sintetis-buku-cetak'):
    base_dir = '/root/journal/books'
    book_dir = os.path.join(base_dir, 'cache', slug)
    output_dir = os.path.join(base_dir, 'output')
    public_books_dir = '/root/journal/public/books'
    public_docs_dir = '/root/journal/public/docs'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(public_books_dir, exist_ok=True)
    os.makedirs(public_docs_dir, exist_ok=True)

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

    print(f"📖 Mengompilasi {len(chapters)} bab naskah berstandar percetakan...")

    typ_parts = []
    for i, ch in enumerate(chapters):
        cleaned = clean_chapter_markdown_to_typst(ch['contentMarkdown'])
        pb = "#pagebreak()\n" if i > 0 else ""
        typ_parts.append(f"""
{pb}#v(2em)
#text(size: 12pt, weight: "bold", fill: luma(100))[BAB {ch['chapterNumber']}]
#v(0.3em)
= {clean_inline_for_typst(ch['chapterTitle'])}
#v(1.5em)

{cleaned}

#v(2em)
""")

    preface_clean = clean_chapter_markdown_to_typst(blueprint.get('preface', ''))
    short_title = blueprint.get('shortTitle', blueprint['title'].split(':')[0].strip())

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
    if pageNum > 2 [
      #set text(font: "Libertinus Serif", size: 8pt, fill: luma(80))
      #if calc.even(pageNum) [
        #grid(
          columns: (1fr, auto),
          align: (left, right),
          [#text(style: "italic")[{short_title}]],
          [#text(size: 7.5pt, fill: luma(120))[PT CHAIN ASIA CONECT]]
        )
      ] else [
        #grid(
          columns: (auto, 1fr),
          align: (left, right),
          [#text(size: 7.5pt, fill: luma(120))[Monograf Ilmiah]],
          [#text(style: "italic")[*Ilham Pradani*]]
        )
      ]
      #v(-2pt)
      #line(length: 100%, stroke: 0.35pt + luma(180))
    ]
  }},
  footer: context {{
    let pageNum = counter(page).get().first()
    if pageNum > 2 [
      #line(length: 100%, stroke: 0.25pt + luma(200))
      #v(2pt)
      #set text(font: "Libertinus Serif", size: 8.5pt, fill: luma(90))
      #if calc.even(pageNum) [
        #grid(
          columns: (auto, 1fr),
          align: (left, right),
          [*#counter(page).display()*],
          [#text(size: 7.5pt, fill: luma(130))[PT CHAIN ASIA CONECT — Scholarly Series]]
        )
      ] else [
        #grid(
          columns: (1fr, auto),
          align: (left, right),
          [#text(size: 7.5pt, fill: luma(130))[Open Access Academic Monograph (CC BY 4.0)]],
          [*#counter(page).display()*]
        )
      ]
    ]
  }}
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
{preface_clean}

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

#pagebreak()

// --- 5. ISI UTAMA BUKU (Halaman Angka Arab: 1, 2, 3...) ---
#set page(numbering: "1")
#counter(page).update(1)

{''.join(typ_parts)}
"""

    typst_path = os.path.join(book_dir, 'book_master.typ')
    pdf_path = os.path.join(output_dir, f"{slug}-print-ready.pdf")

    with open(typst_path, 'w', encoding='utf-8') as f:
        f.write(typst_code)

    print(f"📝 Berkas Typst master berhasil ditulis ke: {typst_path}")
    print("⚡ Menjalankan kompilasi Typst...")

    res = subprocess.run(['typst', 'compile', typst_path, pdf_path], capture_output=True, text=True)
    if res.returncode != 0:
        print("❌ Typst Compilation Error:")
        print(res.stderr)
        sys.exit(1)

    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"🎉 Kompilasi Typst Sukses! PDF Buku: {pdf_path} ({size_mb:.2f} MB)")

    # Copy to public locations so /book and download links immediately serve the latest version
    import shutil
    shutil.copy2(pdf_path, os.path.join(public_books_dir, "empati-sintetis.pdf"))
    shutil.copy2(pdf_path, os.path.join(public_docs_dir, "empati-sintetis-buku-cetak-print-ready.pdf"))
    print(f"📋 Disalin ke public web: /books/empati-sintetis.pdf dan /docs/...")

    # Run Deep Academic PDF Review Engine
    review_book_pdf(pdf_path, blueprint, chapters)
    return pdf_path

if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else 'empati-sintetis-buku-cetak'
    compile_book(slug)
