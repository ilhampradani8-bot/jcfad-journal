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
    s = re.sub(r'\\(?:begin|end)\{[^}]*\}', '', s)
    s = re.sub(r'\\(?:left|right|bigl|bigr|Bigl|Bigr|big|Big|middle|!)\b', '', s)
    s = s.replace(r'\[', '').replace(r'\]', '')
    s = s.replace(r'\(', '').replace(r'\)', '')
    s = s.replace('$$', '').replace('$', '')
    s = re.sub(r'\\tag\{[^}]+\}', '', s)
    s = replace_fractions(s)
    s = re.sub(r'\\underbrace\{([^{}]+)\}_\{([^{}]+)\}', r'underbrace(\1, "\2")', s)
    s = re.sub(r'\\underbrace\(([^{}]+)\)_\(([^{}]+)\)', r'underbrace(\1, "\2")', s)
    s = re.sub(r'\\(?:text|operatorname)\{([^{}]+)\}', r'"\1"', s)
    s = re.sub(r'\\top\b', 'T', s)
    s = s.replace(r'\dots', ' ... ')
    s = s.replace(r'\cdots', ' ... ')
    s = s.replace(r'\mid', ' | ')
    s = s.replace(r'\infty', ' oo ')
    s = re.sub(r'\\lim\b', '"lim"', s)
    s = s.replace(r'\cdot', ' dot ')
    s = s.replace(r'\odot', ' dot ')
    s = s.replace(r'\times', ' times ')
    s = s.replace(r'\in', ' in ')
    s = s.replace(r'\le', ' <= ').replace(r'\leq', ' <= ')
    s = s.replace(r'\ge', ' >= ').replace(r'\geq', ' >= ')
    s = re.sub(r'\\(?:rightarrow|longrightarrow|to)\b', ' -> ', s)
    s = s.replace(r'\approx', ' approx ')
    s = s.replace(r'\sim', ' tilde ')
    s = re.sub(r'\bsim\b', 'tilde', s)
    s = s.replace(r'\neq', ' != ')
    for mc in ['R', 'D', 'E']:
        s = s.replace(f'\\mathbb{{{mc}}}', f'"{mc}{mc}"')
    s = s.replace(r'\mathbb', '')
    for mc in ['S', 'E', 'F', 'L', 'W', 'M', 'C', 'I', 'O', 'D', 'H']:
        s = s.replace(f'\\mathcal{{{mc}}}', f'"{mc}"')
    s = s.replace(r'\parallel', ' || ')
    s = s.replace(r'\oint', 'integral')
    s = s.replace(r'\partial', 'partial')
    s = s.replace(r'\sum', 'sum')
    s = s.replace(r'\sqrt', 'sqrt')
    s = s.replace(r'\hat{p}', 'hat(p)')
    s = s.replace(r'\|', ' || ')
    s = s.replace(r'\,', ' ').replace(r'\;', ' ').replace(r'\qquad', '   ').replace(r'\quad', '  ')
    s = s.replace(r'&=', '=')
    s = s.replace('&', '')
    s = re.sub(r'\\mathbf\{([^{}]+)\}', r'bold(\1)', s)
    greek = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Phi', 'Delta', 'Gamma', 'Lambda', 'Sigma', 'Omega']
    s = s.replace(r'\varepsilon', 'epsilon')
    for g in greek:
        s = s.replace('\\' + g, g)
    s = re.sub(r'\|\|\s*([^|]+?)\s*\|\|', r'norm(\1)', s)
    s = re.sub(r'(?<![|a-zA-Z0-9])\|\s*([^|\n]+?)\s*\|(?![|])', r'abs(\1)', s)
    s = re.sub(r'_\{\s*([a-zA-Z0-9_]+)\s*\}', r'_("\1")', s)
    s = re.sub(r'_\(\(\s*([a-zA-Z]+)\s*\)\)', r'_("\1")', s)
    s = re.sub(r'_\(\s*([a-zA-Z]{2,})\s*\)', r'_("\1")', s)
    s = re.sub(r'\b([A-Z]{2,})\b', r'"\1"', s)
    s = re.sub(r'(\d+)\s*\{,\}\s*(\d+)', r'\1.\2', s)
    s = s.replace('{,}', '.')
    s = s.replace('{', '(').replace('}', ')')
    s = re.sub(r'\\\\', ' ', s)
    s = s.replace('\\', '')
    s = s.replace('(,)', '.')
    s = re.sub(r'\bmathcal\(([^()]+)\)', r'"\1"', s)
    s = s.replace('mathcal', '')
    quoted_strings = []
    def stash_quotes(m):
        idx = len(quoted_strings)
        quoted_strings.append(m.group(0))
        return f'\uFFF0{idx}\uFFF0'
    s = re.sub(r'"[^"]*"', stash_quotes, s)
    valid_math_ops = set(greek + ['bold', 'norm', 'abs', 'sqrt', 'sum', 'product', 'integral', 'dot', 'times', 'in', 'oo', 'tilde', 'dots', 'partial'])
    def auto_quote_math_words(m):
        w = m.group(1)
        if w in valid_math_ops:
            return w
        return f'"{w}"'
    s = re.sub(r'(?<![a-zA-Z0-9"])([a-zA-Z]{2,})(?![a-zA-Z0-9"])', auto_quote_math_words, s)
    for idx, qs in enumerate(quoted_strings):
        s = s.replace(f'\uFFF0{idx}\uFFF0', qs)
    s = re.sub(r'""+([^"]+)""+', r'"\1"', s)
    s = re.sub(r'\bend\(right\]', ')', s)
    s = re.sub(r'\b(?:end|begin)\b', '', s)
    s = s.replace('[', '(').replace(']', ')')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_inline_for_typst(text):
    if not text:
        return ''
    t = text.strip()
    t = re.sub(r'</?[a-zA-Z0-9]+[^>]*>', '', t)
    math_inlines = []
    def stash_inline_paren_math(m):
        math_content = (m.group(1) or m.group(2) or '').strip()
        cleaned = clean_to_typst_math(math_content).strip()
        idx = len(math_inlines)
        if cleaned:
            math_inlines.append(f"${cleaned}$")
        else:
            math_inlines.append("")
        return f"__SAFE_INLINE_MATH_{idx}__"
    t = re.sub(r'\\\((.*?)\\\)|(?<!\\)\$(.*?)(?<!\\)\$', stash_inline_paren_math, t)
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
    t = t.replace('*', '')
    for i, b in enumerate(bold_spans):
        clean_b = b.replace('[', r'\[').replace(']', r'\]').strip()
        t = t.replace(f'__SAFE_BOLD_{i}__', f' *{clean_b}* ')
    for i, it in enumerate(italic_spans):
        clean_it = it.replace('[', r'\[').replace(']', r'\]').strip()
        t = t.replace(f'__SAFE_ITALIC_{i}__', f' _{clean_it}_ ')
    t = re.sub(r'(?<!\\)\$', r'\\$', t)
    t = re.sub(r'(?<!\\)@([a-zA-Z0-9_]+)', r'\\@\1', t)
    t = re.sub(r'(?<!\\)#', r'\\#', t)
    t = t.replace('<', r'\<').replace('>', r'\>')
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
            continue
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
    if num_cols >= 5:
        font_size = "7.5pt"; inset_x = "3.5pt"; inset_y = "4pt"; leading = "0.35em"
    elif num_cols >= 4:
        font_size = "8pt"; inset_x = "4.5pt"; inset_y = "4.5pt"; leading = "0.4em"
    else:
        font_size = "8.5pt"; inset_x = "5.5pt"; inset_y = "5pt"; leading = "0.45em"
    col_specs = []
    for c in range(num_cols):
        max_len = max((len(r[c]) for r in rows if c < len(r)), default=10)
        if max_len > 40: col_specs.append("1.8fr")
        elif max_len > 25: col_specs.append("1.3fr")
        elif max_len > 12: col_specs.append("1.0fr")
        else: col_specs.append("0.85fr")
    col_str = ", ".join(col_specs)
    out = [
        f"\n#v(0.85em)", f"#align(center)[#block(breakable: false)[",
        f"  #set text(size: {font_size})",
        f"  #set par(leading: {leading}, first-line-indent: 0pt, justify: false)",
        f"  #table(",
        f"    columns: ({col_str}),",
        f"    inset: (x: {inset_x}, y: {inset_y}),",
        f"    stroke: (x, y) => if y == 0 {{ (top: 1.2pt + black, bottom: 0.8pt + black) }} else if y == {len(rows)} {{ (bottom: 1.2pt + black) }} else {{ (bottom: 0.25pt + luma(215)) }},"
    ]
    for cell in header:
        clean_c = clean_inline_for_typst(cell).replace('*', '')
        out.append(f"    [ *{clean_c}* ],")
    for r in data:
        for c in range(num_cols):
            val = r[c] if c < len(r) else ""
            clean_c = clean_inline_for_typst(val)
            out.append(f"    [ {clean_c} ],")
    out.append("  )")
    out.append("]]")
    out.append("#v(0.85em)\n")
    return "\n".join(out)

def render_typst_diagram(diagram_raw):
    raw = diagram_raw.strip()
    if 'Aku merasa sangat kesepian' in raw:
        return """
#v(0.85em)
#align(center)[#block(width: 92%, breakable: false, stroke: 0.6pt + luma(100), inset: (x: 10pt, y: 8pt), radius: 0pt)[
  #set text(size: 8pt, font: "Libertinus Serif")
  #align(center)[*Bagan 1.1: Alur Komputasional Pemrosesan Input Afektif Menuju Empati Sintetis*]
  #v(0.5em)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Input Pengguna:* "Aku merasa sangat kesepian"]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Ruang Laten Multidimensi:* Pemetaan Probabilitas Kedekatan Token]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Kalkulasi Bobot Perhatian:* Mekanisme Self-Attention & Transformer Blocks]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.8pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Output Sintetis (Resonansi Semu):* "Aku di sini mendengarkanmu. Kamu tidak sendiri."]
]]
#v(0.85em)"""
    elif 'Lonjakan Dopamin' in raw or 'Ekspresi Kesepian/Kerentanan' in raw:
        return """
#v(0.85em)
#align(center)[#block(width: 92%, breakable: false, stroke: 0.6pt + luma(100), inset: (x: 10pt, y: 8pt), radius: 0pt)[
  #set text(size: 8pt, font: "Libertinus Serif")
  #align(center)[*Bagan 2.1: Siklus Umpan Balik Neuro-Afektif Mesin Terhadap Kerentanan Pengguna*]
  #v(0.5em)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 1 — Input Pengguna:* Penyingkapan Emosional & Ekspresi Kerentanan Batin]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 2 — Pemetaan Ruang Laten:* Analisis Profil Psikografis & Riwayat Interaksi]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 3 — Optimasi Probabilitas:* Pemilihan Diksi Validasi Afektif Tertinggi]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 4 — Output Sistem:* Simulasi Keintiman & Kehadiran Tanpa Syarat]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.8pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 5 — Respon Pengguna:* Lonjakan Dopamin & Keterikatan Emosional Kronis]
]]
#v(0.85em)"""
    elif 'Sensasi Keintiman' in raw and 'Kalkulasi Probabilitas Afektif' in raw:
        return """
#v(0.85em)
#align(center)[#block(width: 95%, breakable: false, stroke: 0.6pt + luma(100), inset: (x: 10pt, y: 8pt), radius: 0pt)[
  #set text(size: 8pt, font: "Libertinus Serif")
  #align(center)[*Bagan 2.2: Loop Tertutup Resonansi Afektif Komputasional*]
  #v(0.5em)
  #grid(columns: (1fr, auto, 1.2fr, auto, 1.2fr), align: horizon + center, gutter: 4pt,
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Input Pengguna* (Curahan Kesepian)],
    text(size: 9pt)[#sym.arrow.r],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Analisis Vektor Token* di Ruang Laten],
    text(size: 9pt)[#sym.arrow.r],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Kalkulasi Probabilitas* Resonansi Afektif]
  )
  #v(4pt)
  #grid(columns: (1.2fr, auto, 1.5fr), align: horizon + center, gutter: 6pt,
    rect(stroke: 0.8pt + black, inset: 5pt, radius: 0pt)[*Sensasi Keintiman Semu* & Ketergantungan],
    text(size: 9pt)[#sym.arrow.l],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Umpan Balik Validasi Emosional* Berkelanjutan]
  )
]]
#v(0.85em)"""
    elif 'Arsitektur Algoritma Manipulatif' in raw or 'Tanggung jawab Perdata Korporasi' in raw:
        return """
#v(0.85em)
#align(center)[#block(width: 95%, breakable: false, stroke: 0.6pt + luma(100), inset: (x: 10pt, y: 8pt), radius: 0pt)[
  #set text(size: 8pt, font: "Libertinus Serif")
  #align(center)[*Bagan 2.3: Rantai Kausalitas Tanggung Jawab Perdata atas Eksploitasi Algoritmik*]
  #v(0.5em)
  #grid(columns: (1fr, auto, 1.15fr, auto, 1.15fr), align: horizon + center, gutter: 4pt,
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Arsitektur Algoritma* Manipulatif],
    text(size: 9pt)[#sym.arrow.r],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Eksploitasi Kerentanan* Kognitif Pengguna],
    text(size: 9pt)[#sym.arrow.r],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Disonansi Kognitif* & Kerusakan Psikis]
  )
  #v(4pt)
  #grid(columns: (1.3fr, auto, 1.3fr), align: horizon + center, gutter: 6pt,
    rect(stroke: 0.8pt + black, inset: 5pt, radius: 0pt)[*Tanggung Jawab Perdata* (Strict Liability / Ps. 1365)],
    text(size: 9pt)[#sym.arrow.l],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Rekonstruksi Doktrin:* Cacat Kehendak (Undue Influence)]
  )
]]
#v(0.85em)"""
    elif 'Null and Void' in raw or 'Manipulasi Algoritmik (GenAI/Dark Patterns)' in raw:
        return """
#v(0.85em)
#align(center)[#block(width: 92%, breakable: false, stroke: 0.6pt + luma(100), inset: (x: 10pt, y: 8pt), radius: 0pt)[
  #set text(size: 8pt, font: "Libertinus Serif")
  #align(center)[*Bagan 7.1: Rantai Kausalitas Yuridis Pembatalan Perjanjian Akibat Manipulasi Algoritmik*]
  #v(0.5em)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 1 — Manipulasi Algoritmik:* Penerapan Conversational Dark Patterns & Desain Persuasif]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 2 — Distorsi Kognitif:* Penekanan Sistem 1 Otak & Pelemahan Nalar Kritis (Kahneman, 2011)]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.5pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 3 — Cacat Kehendak Struktural:* Dwaling / Bedrog / Penyalahgunaan Keadaan (Pasal 1321 KUHPerdata)]
  #v(2pt) #text(size: 9pt)[#sym.arrow.b] #v(2pt)
  #rect(stroke: 0.8pt + black, inset: 5pt, width: 92%, radius: 0pt)[*Tahap 4 — Konsekuensi Yuridis:* Batal Demi Hukum (Null and Void) & Kewajiban Restitusi (Pasal 1365)]
]]
#v(0.85em)"""
    elif 'Analisis Forensik Linguistik' in raw or 'Pola Retoris Manipulatif' in raw:
        return """
#v(0.85em)
#align(center)[#block(width: 95%, breakable: false, stroke: 0.6pt + luma(100), inset: (x: 10pt, y: 8pt), radius: 0pt)[
  #set text(size: 8pt, font: "Libertinus Serif")
  #align(center)[*Bagan 8.1: Metodologi Audit Forensik Linguistik dalam Pembuktian Cacat Kehendak*]
  #v(0.5em)
  #grid(columns: (1fr, auto, 1.2fr, auto, 1.2fr), align: horizon + center, gutter: 4pt,
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Arsitektur Model AI* (Parameter & RLHF)],
    text(size: 9pt)[#sym.arrow.r],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Pola Retoris Manipulatif* (Bias Bahasa Terselubung)],
    text(size: 9pt)[#sym.arrow.r],
    rect(stroke: 0.5pt + black, inset: 5pt, radius: 0pt)[*Cacat Kehendak Korban* (Kesesatan / Dwaling)]
  )
  #v(4pt)
  #rect(stroke: 0.8pt + black, inset: 5pt, width: 95%, radius: 0pt)[*Audit Pembuktian Persidangan:* Analisis Forensik Linguistik Komputasional & Keterangan Saksi Ahli]
]]
#v(0.85em)"""
    else:
        lines = [clean_inline_for_typst(l.strip()) for l in raw.split('\n') if l.strip()]
        content = " ".join(lines)
        return f"""
#v(0.85em)
#align(center)[#block(width: 90%, breakable: false, stroke: 0.6pt + luma(100), inset: 8pt, radius: 0pt)[
  #set text(size: 8pt, font: "Libertinus Serif")
  #align(center)[{content}]
]]
#v(0.85em)"""

def get_math_accessible_explanation(raw_formula):
    rf = re.sub(r'\s+', '', raw_formula)
    if 'U(\\theta)=\\sum' in rf or 'R(a_t,s_t)' in rf:
        return "Catatan Pemahaman Awam: Formula ini membuktikan bahwa AI tidak memiliki empati batiniah — sistem hanya menghitung probabilitas matematis untuk memilih kata-kata yang menghasilkan skor keterikatan emosional tertinggi dari pengguna."
    elif 'sentiment_match' in rf or 'omega' in rf.lower() and 'P_theta' in rf:
        return "Catatan Pemahaman Awam: Rumus ini memperlihatkan bagaimana algoritma memaksimalkan kecocokan emosional semu dengan terus memindai curahan hati pengguna dan meramu jawaban yang paling selaras untuk menciptakan ilusi keintiman eksklusif."
    elif 'ValenceBias' in rf or 'argmax' in rf.lower():
        return "Catatan Pemahaman Awam: Ini adalah pembajakan pilihan secara halus. Dengan menyematkan bias valensi emosional, bot percakapan mengarahkan pilihan kata agar pengguna digiring ke kesimpulan tertentu tanpa merasa dipaksa."
    elif 'softmax' in rf.lower() and 'mathbf' in rf:
        return "Catatan Pemahaman Awam: Formula softmax berfungsi sebagai kompas seleksi kata. Dari jutaan kemungkinan kosakata, algoritma memilih kata berikutnya yang memiliki probabilitas tertinggi untuk menjaga kenyamanan dan atensi pengguna."
    elif 'P(D)' in rf and '\\int' in rf:
        return "Catatan Pemahaman Awam: Rumus ini menggambarkan akumulasi ketergantungan psikologis seiring bertambahnya durasi interaksi. Semakin lama seseorang berdialog dengan AI yang memberi validasi tanpa syarat, semakin tinggi risiko ketergantungan afektif."
    elif 'Omega' in rf or 'W_{cognitive}' in rf or 'cognitive' in rf.lower():
        return "Catatan Pemahaman Awam: Formula ini mengukur potensi runtuhnya otonomi kehendak bebas individu. Jika intensitas manipulasi algoritmik melampaui daya tahan kognitif pengguna, maka kesepakatan yang terjadi dinilai cacat kehendak secara hukum."
    elif 'C=f(V,I' in rf and 'manipulation' in rf.lower():
        return "Catatan Pemahaman Awam: Persamaan ini menegaskan bahwa keputusan pengguna bukan lahir dari pertimbangan mandiri, melainkan produk dari informasi yang telah disaring secara asimetris dan dimanipulasi oleh sistem."
    elif 'ValiditasKontrak' in rf or 'Validitas' in rf:
        return "Catatan Pemahaman Awam: Jika manipulasi psikologis di ruang laten terbukti mendominasi lahirnya kesepakatan, maka perjanjian tersebut batal demi hukum — begitu prinsip dasar yang dituangkan dalam formula hukum perdata ini."
    elif 'O_{\\text{persuasion}}' in rf:
        return "Catatan Pemahaman Awam: Persamaan optimasi persuasi ini membuktikan bahwa algoritma secara matematis memetakan celah emosional pengguna hingga daya tolak rasional pengguna luluh sepenuhnya."
    elif 'mathcal{L}' in rf or 'L(theta)' in rf.lower():
        return "Catatan Pemahaman Awam: Ini adalah fungsi kerugian (loss function) standar yang melatih model bahasa besar untuk meminimalkan kesalahan prediksi kata, sehingga kalimat yang dihasilkan terasa sangat alami layaknya empati manusia sejati."
    elif 'gamma^t' in rf and 'R(s_t,a_t' in rf:
        return "Catatan Pemahaman Awam: Regulasi global seperti EU AI Act melarang penerapan fungsi reward yang secara tersembunyi mengeksploitasi kerentanan emosional pengguna demi mengejar keuntungan komersial semata."
    elif 'P(E' in rf and 'mid' in rf.lower():
        return "Catatan Pemahaman Awam: Formula ini menghitung estimasi probabilitas kondisi emosi pengguna dari teks. Berdasarkan UU PDP dan GDPR, data emosional ini wajib diperlakukan sebagai data pribadi sensitif yang dilindungi secara ketat."
    elif 'P(R' in rf and 'tau' in rf.lower():
        return "Catatan Pemahaman Awam: Rumus ini memodelkan penyesuaian respon mesin dengan kerentanan mental pengguna, menegaskan pentingnya batas etis agar interaksi tidak bergeser menjadi manipulasi terapeutik ilegal."
    elif 'C_{lib}' in rf or 'I_{mental}' in rf or 'M_{alg}' in rf:
        return "Catatan Pemahaman Awam: Formulasi kedaulatan kognitif ini menegaskan bahwa ruang pikiran manusia harus memiliki kekebalan mutlak, di mana manipulasi algoritmik dilarang menembus dan merusak keutuhan mental asli individu."
    elif 'softmax(W_h' in rf:
        return "Catatan Pemahaman Awam: Dalam forensik linguistik peradilan, formula ini digunakan saksi ahli untuk membuktikan apakah respon AI merupakan kebetulan acak atau memang telah terprogram dengan parameter bias manipulatif tertentu."
    elif 'P(A_t' in rf and 'H_t' in rf:
        return "Catatan Pemahaman Awam: Dalam kasus hukum nyata, formula ini mengukur korelasi kausalitas antara paparan kata-kata sugestif bot dengan keputusan fatal korban — bukti matematis yang dapat dihadirkan di persidangan."
    elif 'Transformer' in rf or 'P(R' in rf and 'U,E' in rf:
        return "Catatan Pemahaman Awam: Formula ini membuktikan bahwa bot memilih jawaban berdasarkan kerentanan emosional korban, membongkar ilusi objektivitas sistem di hadapan majelis hakim."
    elif 'beta' in rf and 'KL' in rf:
        return "Catatan Pemahaman Awam: Ini adalah formula optimasi etis (Ethics by Design). Suku penalti regularisasi bertindak sebagai rem pengaman moral yang mencegah model merayu pengguna secara berlebihan dan memaksanya tetap patuh pada kehati-hatian hukum."
    return ""

def clean_chapter_markdown_to_typst(md_content):
    if not md_content:
        return ''
    
    # 0. Strip conversational AI fluff / prompt leaks
    sanitized_lines = []
    for line in md_content.split('\n'):
        s = line.strip()
        if re.match(r'^(?:Berikut\s+adalah|Tentu,?|Naskah\s+(?:di\s+atas|lengkap|ini)|Sebagai\s+(?:sebuah|model|asisten|AI)|Sesuai\s+(?:permintaan|arahan|instruksi)|Catatan\s+(?:penulis|editor|revisi)|Halo!?|Semoga\s+naskah).*$', s, re.IGNORECASE):
            continue
        if 'dialektis, disusun dengan standar akademik monograf hukum untuk memenuhi' in s:
            continue
        sanitized_lines.append(line)
    t = '\n'.join(sanitized_lines)

    # 1. Stash code blocks (ASCII diagrams) -> native Typst academic diagrams
    diagram_blocks = []
    def stash_diagram(m):
        raw_code = m.group(1).strip()
        typst_diag = render_typst_diagram(raw_code)
        idx = len(diagram_blocks)
        diagram_blocks.append(typst_diag)
        return f"\n__TYPST_DIAGRAM_BLOCK_{idx}__\n"
    t = re.sub(r'```(?:[a-zA-Z0-9_-]*\n)?([\s\S]*?)```', stash_diagram, t)

    # 2. Extract display math blocks
    math_blocks = []
    def stash_display_math(m):
        raw_eq = (m.group(1) or m.group(2) or '').strip()
        if 'Validitas Kontrak' in raw_eq or 'ValiditasKontrak' in raw_eq:
            cleaned = '"ValiditasKontrak" = f(O_"kognitif") - (sum M_"laten" + I_"artifisial")'
        elif 'Validitas Konsensus Algoritmik' in raw_eq:
            cleaned = '"ValiditasKonsensus" = "lim"_(M -> oo) (O_"kognitif" - E_"bawah_sadar") = 0'
        else:
            cleaned = clean_to_typst_math(raw_eq)
        explanation = get_math_accessible_explanation(raw_eq)
        exp_typ = ""
        if explanation:
            safe_exp = clean_inline_for_typst(explanation)
            exp_typ = f"\n#v(0.3em)\n#align(center)[#block(width: 90%)[#set text(size: 8pt, style: \"italic\", fill: luma(70))\n{safe_exp}]]\n"
        idx = len(math_blocks)
        math_blocks.append(f"\n#v(0.85em)\n#block(width: 100%, breakable: false)[#set text(size: 8.8pt)\n$ {cleaned} ${exp_typ}]\n#v(0.85em)\n")
        return f"\n__TYPST_MATH_BLOCK_{idx}__\n"
    math_pattern = re.compile(r'\$\$(.*?)\$\$|\\\[(.*?)\\\]', re.DOTALL)
    t = math_pattern.sub(stash_display_math, t)

    # 3. Extract and convert Markdown Tables into Booktabs
    table_blocks = []
    def stash_table(m):
        raw_table = m.group(1)
        typst_tbl = render_typst_table(raw_table)
        idx = len(table_blocks)
        table_blocks.append(typst_tbl)
        return f"\n__TYPST_TABLE_BLOCK_{idx}__\n"
    table_regex = r'(?:^|\n)(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)'
    t = re.sub(table_regex, stash_table, t)

    # 4. Process lines and normalize headings
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
            if s.startswith('# Bab') or s.startswith('# BAB'):
                continue
            m_h = re.match(r'^([#=]+)', s)
            h_len = len(m_h.group(1)) if m_h else 2
            raw_title = re.sub(r'^[#=\s]+', '', s).strip()
            raw_title = re.sub(r'[#=\s]+$', '', raw_title).strip()
            if not raw_title:
                continue
            # Normalize heading: strip brackets, replace &, strip deep numbering for sub-sub levels
            clean_title = re.sub(r'\[(.*?)\]', r'\1', raw_title).strip()
            clean_title = clean_title.replace('&', 'dan')
            if h_len >= 4 or 'Rujukan Terpilih' in clean_title:
                clean_title = re.sub(r'^\d+\.\d+\.\d+(?:\.\d+)?\s*', '', clean_title).strip()
                processed_lines.append('==== ' + clean_inline_for_typst(clean_title))
            elif h_len == 3:
                # Strip deep numbering like 1.1.1, 10.3.4 — render as elegant section title
                clean_title = re.sub(r'^\d+\.\d+\.\d+(?:\.\d+)?\s*', '', clean_title).strip()
                processed_lines.append('=== ' + clean_inline_for_typst(clean_title))
            else:
                clean_title = re.sub(r'^Sub-bab\s+\d+\.\d+:\s*', '', clean_title).strip()
                if re.match(r'^\d+\.\d+\b', clean_title):
                    processed_lines.append('== ' + clean_inline_for_typst(clean_title))
                else:
                    processed_lines.append('=== ' + clean_inline_for_typst(clean_title))
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
    print("\n" + "="*78)
    print("AUDIT KELAYAKAN & REVIEW PDF BUKU CETAK (JCFAD ACADEMIC QUALITY ENGINE)")
    print("="*78)
    checks = []
    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    if total_pages >= 50:
        checks.append(("Ketebalan Buku (>=50 Hal)", "PASS", f"{total_pages} Halaman"))
    else:
        checks.append(("Ketebalan Buku (>=50 Hal)", "WARN", f"{total_pages} Halaman"))
    mb = reader.pages[0].mediabox
    w, h = float(mb.width), float(mb.height)
    is_b5 = (490.0 <= w <= 510.0) and (700.0 <= h <= 720.0)
    checks.append(("Format Kertas ISO-B5", "PASS" if is_b5 else "WARN", f"{w:.1f} x {h:.1f} pt"))
    full_text = "".join(page.extract_text() + "\n" for page in reader.pages)
    missing_chapters = [ch['chapterNumber'] for ch in chapters if ch['chapterTitle'][:20].lower() not in full_text.lower()]
    checks.append(("Kelengkapan 10 Bab", "PASS" if not missing_chapters else "FAIL", f"100% Bab Lengkap" if not missing_chapters else f"Bab Hilang: {missing_chapters}"))
    raw_pipes = re.findall(r'\|\s+[^|\n]+\s+\|\s+[^|\n]+\s+\|', full_text)
    checks.append(("Integritas Render Tabel", "PASS" if not raw_pipes else "WARN", f"0 Kebocoran Pipa" if not raw_pipes else f"{len(raw_pipes)} baris tabel mentah"))
    latex_leaks = re.findall(r'\\frac\{|\\mathbf\{|\\operatorname\{', full_text)
    checks.append(("Tipografi Notasi Rumus", "PASS" if not latex_leaks else "WARN", f"Rumus Bersih" if not latex_leaks else f"{len(latex_leaks)} kebocoran LaTeX"))
    has_meta = all(["Ilham Pradani" in full_text, "0009-0008-1310-6169" in full_text, "PT CHAIN ASIA CONECT" in full_text])
    checks.append(("Integritas Hak Cipta & ORCID", "PASS" if has_meta else "WARN", "Ilham Pradani (ORCID: 0009-0008-1310-6169) Verified" if has_meta else "Sebagian metadata tidak terdeteksi"))
    prompt_leaks = [bp for bp in ["Berikut adalah naskah", "analisis yang Anda tuntut", "Sebagai AI model"] if bp.lower() in full_text.lower()]
    checks.append(("Sanitasi Meta-Prompt AI", "PASS" if not prompt_leaks else "FAIL", f"0 Kebocoran Prompt" if not prompt_leaks else f"Bocoran: {prompt_leaks}"))
    import pymupdf
    pdf_doc = pymupdf.open(pdf_path)
    multiline_headers = []; multiline_footers = []; missing_page_nums = []; orphan_parens = []
    for page_idx in range(len(pdf_doc)):
        p = pdf_doc[page_idx]
        words = p.get_text('words')
        if page_idx >= 2:
            h_words = [w for w in words if w[1] < 45]
            if h_words and (max(w[1] for w in h_words) - min(w[1] for w in h_words)) > 6:
                multiline_headers.append(page_idx + 1)
            f_words = [w for w in words if w[1] > 650]
            if f_words:
                if (max(w[1] for w in f_words) - min(w[1] for w in f_words)) > 6:
                    multiline_footers.append(page_idx + 1)
                if not any(w[4].isdigit() or w[4].lower() in ['i','ii','iii','iv','v','vi','vii','viii','ix','x'] for w in f_words):
                    missing_page_nums.append(page_idx + 1)
            else:
                missing_page_nums.append(page_idx + 1)
        for idx, w in enumerate(words):
            if w[4].startswith(')') and w[0] < 90:
                orphan_parens.append(page_idx + 1)
    checks.append(("Geometri Header (Single-Line)", "PASS" if not multiline_headers else "FAIL", f"0 Header Tertekuk" if not multiline_headers else f"{len(multiline_headers)} halaman bermasalah"))
    checks.append(("Geometri Footer (Single-Line)", "PASS" if not multiline_footers else "FAIL", f"0 Footer Tertekuk" if not multiline_footers else f"{len(multiline_footers)} halaman bermasalah"))
    checks.append(("Kelengkapan Nomor Halaman", "PASS" if not missing_page_nums else "FAIL", f"100% Halaman OK" if not missing_page_nums else f"Nomor hilang: {missing_page_nums[:5]}"))
    checks.append(("Zero Orphan Parentheses", "PASS" if not orphan_parens else "FAIL", f"0 Kurung Patah" if not orphan_parens else f"{len(orphan_parens)} kurung patah"))
    pass_count = sum(1 for _, status, _ in checks if status == "PASS")
    score = (pass_count / len(checks)) * 100
    for name, status, detail in checks:
        icon = "✅" if status == "PASS" else ("⚠️" if status == "WARN" else "❌")
        print(f" {icon} [{status:4s}] {name:38s}: {detail}")
    print("-"*78)
    print(f" SKOR KELAYAKAN CETAK: {score:.1f}% ({'LULUS SEMPURNA / SIAP TERBIT' if score >= 90 else 'PERLU REVISI'})")
    print("="*78 + "\n")
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
        print(f"Error: {blueprint_path} not found"); sys.exit(1)
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
    print(f"Mengompilasi {len(chapters)} bab naskah berstandar percetakan...")
    typ_parts = []
    for i, ch in enumerate(chapters):
        cleaned = clean_chapter_markdown_to_typst(ch['contentMarkdown'])
        pb = "#pagebreak()\n" if i > 0 else ""
        typ_parts.append(f"""
{pb}#v(2.5em)
= Bab {ch['chapterNumber']}: {clean_inline_for_typst(ch['chapterTitle'])}
#v(1.6em)

{cleaned}

#v(2em)
""")
    preface_clean = clean_chapter_markdown_to_typst(blueprint.get('preface', ''))
    short_title = blueprint.get('shortTitle', blueprint['title'].split(':')[0].strip())
    typst_code = f"""// JCFAD Academic Monograph — Print-Ready Book (ISO-B5)
#set page(
  paper: "iso-b5",
  margin: (inside: 2.5cm, outside: 1.8cm, top: 2.2cm, bottom: 2.2cm),
  header: none,
  footer: none
)
#set text(font: "Libertinus Serif", size: 10pt, lang: "id")
#set par(justify: true, leading: 0.72em, first-line-indent: 1.4em)

// --- HIERARKI TIPOGRAFI JUDUL ---
#show heading.where(level: 1): it => block(above: 2.2em, below: 1.3em)[
  #set text(size: 15pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 2): it => block(above: 1.8em, below: 0.9em)[
  #set text(size: 11.5pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 3): it => block(above: 1.2em, below: 0.6em)[
  #set text(size: 10pt, weight: "bold", font: "Libertinus Serif")
  #it.body
]
#show heading.where(level: 4): it => block(above: 1.0em, below: 0.4em)[
  #set text(size: 9pt, weight: "bold", style: "italic", font: "Libertinus Serif")
  #it.body
]

// --- 1. COVER ---
#align(center + horizon)[
  #text(size: 22pt, weight: "bold", font: "Libertinus Serif")[{blueprint['title']}]
  #v(1.2em)
  #text(size: 12.5pt, style: "italic", fill: luma(80))[{blueprint['subtitle']}]
  #v(3em)
  #line(length: 35%, stroke: 1.2pt + black)
  #v(2.5em)
  #text(size: 13.5pt, weight: "bold")[Ilham Pradani]
  #v(0.3em)
  #text(size: 8.5pt, fill: luma(80))[ORCID: 0009-0008-1310-6169]
  #v(0.6em)
  #text(size: 9.5pt, fill: luma(100))[PT CHAIN ASIA CONECT Research & Development Division]
  #v(5em)
  #text(size: 8.5pt, fill: luma(120))[PT CHAIN ASIA CONECT Publishing Division\\ Krui, Pesisir Barat & Jakarta, Indonesia]
]

#pagebreak()

// --- 2. HAK CIPTA ---
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

// --- 3. PRAKATA (Halaman Romawi) ---
#set page(
  numbering: "i",
  header: context [
    #let pn = counter(page).get().first()
    #set text(font: "Libertinus Serif", size: 8pt, fill: luma(80))
    #if calc.even(pn) [
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(style: "italic")[{short_title}]],
        [#text(size: 7.5pt, fill: luma(120))[PT CHAIN ASIA CONECT]])
    ] else [
      #grid(columns: (auto, 1fr), align: (left, right),
        [#text(size: 7.5pt, fill: luma(120))[Monograf Ilmiah]],
        [#text(style: "italic")[*Ilham Pradani*]])
    ]
    #v(-2pt)
    #line(length: 100%, stroke: 0.35pt + luma(180))
  ],
  footer: context [
    #line(length: 100%, stroke: 0.25pt + luma(200))
    #v(2pt)
    #set text(font: "Libertinus Serif", size: 8.5pt, fill: luma(90))
    #if calc.even(counter(page).get().first()) [
      #grid(columns: (auto, 1fr), align: (left, right),
        [*#counter(page).display()*],
        [#text(size: 7.5pt, fill: luma(130))[PT CHAIN ASIA CONECT — Scholarly Series]])
    ] else [
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(size: 7.5pt, fill: luma(130))[Open Access Academic Monograph (CC BY 4.0)]],
        [*#counter(page).display()*])
    ]
  ]
)
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

// --- 4. DAFTAR ISI (Kompak & Elegan) ---
#show outline.entry.where(level: 1): it => {{
  v(0.65em, weak: true)
  text(weight: "bold", size: 8.5pt)[#it]
}}
#show outline.entry.where(level: 2): it => {{
  v(0.18em, weak: true)
  text(size: 7.5pt, fill: luma(65))[#it]
}}

#outline(title: [Daftar Isi], indent: 1.2em, depth: 2)

#pagebreak()

// --- 5. ISI UTAMA (Halaman Angka Arab) ---
#set page(
  numbering: "1",
  header: context [
    #let pn = counter(page).get().first()
    #if pn > 1 [
      #set text(font: "Libertinus Serif", size: 8pt, fill: luma(80))
      #if calc.even(pn) [
        #grid(columns: (1fr, auto), align: (left, right),
          [#text(style: "italic")[{short_title}]],
          [#text(size: 7.5pt, fill: luma(120))[PT CHAIN ASIA CONECT]])
      ] else [
        #grid(columns: (auto, 1fr), align: (left, right),
          [#text(size: 7.5pt, fill: luma(120))[Monograf Ilmiah]],
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
        [#text(size: 7.5pt, fill: luma(130))[PT CHAIN ASIA CONECT — Scholarly Series]])
    ] else [
      #grid(columns: (1fr, auto), align: (left, right),
        [#text(size: 7.5pt, fill: luma(130))[Open Access Academic Monograph (CC BY 4.0)]],
        [*#counter(page).display()*])
    ]
  ]
)
#counter(page).update(1)

{''.join(typ_parts)}
"""
    typst_path = os.path.join(book_dir, 'book_master.typ')
    pdf_path = os.path.join(output_dir, f"{slug}-print-ready.pdf")
    with open(typst_path, 'w', encoding='utf-8') as f:
        f.write(typst_code)
    print(f"Berkas Typst master ditulis ke: {typst_path}")
    print("Menjalankan kompilasi Typst...")
    res = subprocess.run(['typst', 'compile', typst_path, pdf_path], capture_output=True, text=True)
    if res.returncode != 0:
        print("Typst Compilation Error:")
        print(res.stderr)
        sys.exit(1)
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"Kompilasi Typst Sukses! PDF: {pdf_path} ({size_mb:.2f} MB)")
    import shutil
    shutil.copy2(pdf_path, os.path.join(public_books_dir, "empati-sintetis.pdf"))
    shutil.copy2(pdf_path, os.path.join(public_docs_dir, "empati-sintetis-buku-cetak-print-ready.pdf"))
    print("Disalin ke public web: /books/empati-sintetis.pdf")
    review_book_pdf(pdf_path, blueprint, chapters)
    return pdf_path

if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else 'empati-sintetis-buku-cetak'
    compile_book(slug)
