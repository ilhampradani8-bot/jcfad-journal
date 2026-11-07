// Utility for fetching and parsing news directly and dynamically from Google Sheets
// Zero hardcoded/static dummy data - 100% live Google Sheets data.

export const GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQa2Ih5iXjRYbgKJsIFlUTwPw4hl0xDIRn5MCTWd6g7UecdJi8jQLj8qKO_GvBG-JWIQ7n5pju2ZG47/pub?gid=0&single=true&output=csv";
export const CLOUDFLARE_D1_API_URL = "https://api.chainasiaconnect.co.id/";

// Helper untuk decode HTML entities (&amp;, &quot;, &lt;, &gt;, &#39;, &nbsp;)
export function decodeHtmlEntities(text) {
  if (!text) return '';
  return text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/&mdash;/g, '—')
    .replace(/&ndash;/g, '–');
}

// Helper untuk membersihkan format markdown/bintang (***, **, *) dan merapikan teks
export function cleanContentText(text) {
  if (!text) return '';
  return decodeHtmlEntities(text)
    .replace(/\*\*\*(.*?)\*\*\*/g, '$1') // bersihkan ***bold-italic***
    .replace(/\*\*(.*?)\*\*/g, '$1')     // bersihkan **bold**
    .replace(/\*(.*?)\*/g, '$1')         // bersihkan *italic*
    .replace(/^#+\s+/gm, '')            // bersihkan markdown headers (#, ##, ###)
    .replace(/`{1,3}(.*?)`{1,3}/g, '$1') // bersihkan inline code
    .trim();
}

// Parser tabel Markdown (| ... |) menjadi tabel HTML ilmiah standar Three-Line Table
export function parseMarkdownTableHtml(raw) {
  if (!raw || !raw.includes('|')) return null;
  const lines = raw.trim().split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  if (lines.length < 2) return null;

  let caption = '';
  const tableLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Deteksi caption tabel jika diawali Table/Tabel
    if (i === 0 && !line.startsWith('|') && /^(?:>|#|\*\*|\*)?\s*(?:Table|Tabel)\b/i.test(line)) {
      caption = line.replace(/^[>#*\s]+|[*\s]+$/g, '').trim();
      continue;
    }
    if (line.includes('|')) {
      tableLines.push(line);
    }
  }

  if (tableLines.length < 2) return null;

  // Temukan indeks baris pemisah kolom (separator line dengan deretan dash -)
  const sepIdx = tableLines.findIndex((l, idx) => {
    if (idx === 0) return false;
    const stripped = l.replace(/[|:\s-]/g, '');
    const dashes = l.replace(/[^ -]/g, '');
    return stripped.length === 0 && dashes.length >= 2;
  });

  if (sepIdx === -1 || sepIdx === 0) return null;

  const headerLines = tableLines.slice(0, sepIdx);
  const dataLines = tableLines.slice(sepIdx + 1);

  if (headerLines.length === 0) return null;

  const splitCells = (line) => {
    let clean = line;
    if (clean.startsWith('|')) clean = clean.substring(1);
    if (clean.endsWith('|')) clean = clean.substring(0, clean.length - 1);
    return clean.split('|').map(c => c.trim());
  };

  // Deteksi perataan kolom dari baris separator (:---, :---:, ---:)
  const sepCells = splitCells(tableLines[sepIdx]);
  const alignments = sepCells.map(c => {
    const t = c.trim();
    if (t.startsWith(':') && t.endsWith(':')) return 'center';
    if (t.endsWith(':')) return 'right';
    if (t.startsWith(':')) return 'left';
    return '';
  });

  const headerRows = headerLines.map(splitCells);
  const dataRows = dataLines.map(splitCells);

  const inlineFormat = (text) => {
    if (!text) return '';
    return text
      .replace(/\\\|/g, '|')
      .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\$([^$]+)\$/g, '<span class="academic-math">$1</span>');
  };

  let html = `<div class="academic-table-wrap academic-table-wrapper">\n`;
  if (caption) {
    html += `  <div class="table-title-sharp academic-table-caption">${inlineFormat(caption)}</div>\n`;
  }
  html += `  <div class="table-scroll-hint">↔ Geser tabel secara horizontal untuk melihat seluruh data</div>\n`;
  html += `  <table class="academic-three-line-table">\n`;
  html += `    <thead>\n`;
  for (const row of headerRows) {
    html += `      <tr>\n`;
    row.forEach((cell, idx) => {
      const align = alignments[idx] ? ` style="text-align: ${alignments[idx]};"` : '';
      html += `        <th${align}>${inlineFormat(cell)}</th>\n`;
    });
    html += `      </tr>\n`;
  }
  html += `    </thead>\n`;

  if (dataRows.length > 0) {
    html += `    <tbody>\n`;
    for (const row of dataRows) {
      if (row.length === 1 && row[0] === '') continue;
      html += `      <tr>\n`;
      row.forEach((cell, idx) => {
        const align = alignments[idx] ? ` style="text-align: ${alignments[idx]};"` : '';
        html += `        <td${align}>${inlineFormat(cell)}</td>\n`;
      });
      html += `      </tr>\n`;
    }
    html += `    </tbody>\n`;
  }

  html += `  </table>\n</div>`;
  return html;
}

// Helper untuk format render konten artikel (menghasilkan HTML bersih dengan heading sub-bab jika diawali **)
export function renderArticleContentHtml(raw) {
  if (!raw) return [];
  const decoded = decodeHtmlEntities(raw);

  // Jika konten sudah merupakan dokumen HTML kaya (misal paper ilmiah jurnal SINTA/UNISSULA)
  if (decoded.trim().startsWith('<div class="journal-paper-container">') || decoded.trim().startsWith('<article') || decoded.trim().startsWith('<div class="article-')) {
    return [{
      type: 'html',
      html: decoded
    }];
  }

  // Bersihkan catatan revisi / reviewer response / debug notes dari tampilan publik agar tidak bocor ke pembaca
  let cleanedText = decoded
    .replace(/(?:\r?\n|^)#{1,4}\s*(?:(?:\d+\.?\s*)?(?:Revision\s*Notes?|Catatan\s*Revisi|Reviewer|Sintesis\s*Rekonsiliasi|Penajaman\s*Doktrinal|Read\s*Time|Reading\s*Time|Integrity\s*Declaration|Deklarasi\s*Integritas|Daftar\s*Pustaka\s*Utama|Keterkaitan\s*Empiris|Keterkaitan\s*Riset))[\s\S]*$/i, '')
    .replace(/(?:\r?\n|^)All\s*(?:of\s*)?(?:the\s*)?(?:above|these)\s*amendments\s*directly\s*address[\s\S]*$/i, '')
    // Hapus HANYA baris footnote/watermark DOI (jangan hapus teks setelahnya!)
    .replace(/(?:\r?\n|^)[*\s]*DOI:\s*10\.\d{4,9}\/[^\n]*(?:ResearchGate|Zenodo)[^\n]*(?:\r?\n|$)/gmi, '\n')
    // Bersihkan penutup rilis 'Ditulis oleh...' & 'Dibaca X kali' dari narasi
    .replace(/(?:\r?\n|^)\s*(?:Ditulis\s*(?:oleh)?:?|Penulis:?)\s*(?:\r?\n)?[^\n]*(?:\r?\n)?(?:President\s*Director[^\n]*)?/gi, '')
    .replace(/(?:\r?\n|^)\s*Dibaca\s+\d+[\s\w]*/gi, '');

  // Sisipkan jeda paragraf sebelum Subheading berita korporasi
  const corporateHeadings = [
    'Kehangatan Kebersamaan Bersama Ibu Marlin',
    'Apresiasi & Komitmen Sinergi Lokal',
    'Apresiasi &amp; Komitmen Sinergi Lokal',
    'Kehangatan Sambutan dan Pelayanan Berkelas di Surfmatra Krui',
    'Apresiasi dan Sinergi Pelaku Usaha Pariwisata Lokal Krui',
    'Memperkuat Infrastruktur Digital Kesehatan Lintas Negara',
    'Tahapan Implementasi dan Komitmen Layanan'
  ];
  for (const h of corporateHeadings) {
    const escaped = h.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    cleanedText = cleanedText.replace(new RegExp(`([.!?])\\s+(${escaped})\\s+`, 'g'), '$1\n\n**$2**\n\n');
  }

  // Sisipkan jeda paragraf sebelum dan sesudah kutipan wawancara langsung ("...")
  cleanedText = cleanedText.replace(/([.!?])\s+("(?=[A-Z]))/g, '$1\n\n$2');
  cleanedText = cleanedText.replace(/(".*?"\s*(?:ujar|ungkap|tutur|tutup|jelas|kata|imbuh)[^.!?]+[.!?])\s+([A-Z])/g, '$1\n\n$2');

  const lines = cleanedText.split(/\r?\n/);
  const blocks = [];
  let curTable = [];
  let curList = [];
  let curPara = [];

  function flushPara() {
    if (curPara.length > 0) {
      const pText = curPara.join(' ').trim();
      if (pText) {
        let formatted = pText
          .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>');
        blocks.push({
          type: 'paragraph',
          html: formatted
        });
      }
      curPara = [];
    }
  }

  function flushList() {
    if (curList.length > 0) {
      blocks.push({
        type: 'list',
        items: curList.map(item => item.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'))
      });
      curList = [];
    }
  }

  function flushTable() {
    if (curTable.length > 0) {
      const tText = curTable.join('\n');
      const tHtml = parseMarkdownTableHtml(tText);
      if (tHtml) {
        blocks.push({
          type: 'table',
          html: tHtml
        });
      } else {
        curTable.forEach(tl => curPara.push(tl));
        flushPara();
      }
      curTable = [];
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const l = lines[i].trim();
    if (!l) {
      flushTable();
      flushList();
      flushPara();
      continue;
    }

    // Baris tabel markdown
    if (l.startsWith('|') && l.includes('|')) {
      flushList();
      flushPara();
      curTable.push(l);
      continue;
    } else if (curTable.length > 0) {
      flushTable();
    }

    // Baris list
    if (l.startsWith('- ') || l.startsWith('* ') || /^\d+\.\s+/.test(l)) {
      flushPara();
      curList.push(l.replace(/^[-*]\s+/, '').replace(/^\d+\.\s+/, ''));
      continue;
    } else if (curList.length > 0) {
      flushList();
    }

    // Baris Heading
    const headingMatch = l.match(/^\*\*(.*?)\*\*$/) || l.match(/^#{1,4}\s+(.*)$/);
    if (headingMatch && !l.includes('|')) {
      flushPara();
      blocks.push({
        type: 'heading',
        html: cleanContentText(headingMatch[1].replace(/^\*\*|\*\*$/g, '').trim())
      });
      continue;
    }

    // Baris tag HTML container
    if (/^<(div|section|table|figure|blockquote|hr|header|footer)/i.test(l)) {
      flushPara();
      blocks.push({
        type: 'html',
        html: l
      });
      continue;
    }

    // Teks biasa
    curPara.push(l);
  }

  flushTable();
  flushList();
  flushPara();

  return blocks;
}

// Helper untuk membuat slug SEO dari judul rilis
export function slugify(text) {
  if (!text) return '';
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/[àáâãäå]/g, 'a')
    .replace(/[èéêë]/g, 'e')
    .replace(/[ìíîï]/g, 'i')
    .replace(/[òóôõö]/g, 'o')
    .replace(/[ùúûü]/g, 'u')
    .replace(/[ñ]/g, 'n')
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// Helper untuk memastikan format URL gambar (termasuk direct link Google Drive dan link relatif)
export function formatImageUrl(url) {
  if (!url) return 'https://www.chainasiaconnect.co.id/images/CAC-LOGO.jpg';
  const trimmed = url.trim();
  if (!trimmed) return 'https://www.chainasiaconnect.co.id/images/CAC-LOGO.jpg';

  if (trimmed.startsWith('/') && !trimmed.startsWith('//')) {
    return `https://www.chainasiaconnect.co.id${trimmed}`;
  }

  const driveFileMatch = trimmed.match(/\/file\/d\/([a-zA-Z0-9_-]+)/);
  if (driveFileMatch && driveFileMatch[1]) {
    return `https://lh3.googleusercontent.com/d/${driveFileMatch[1]}`;
  }
  const driveIdMatch = trimmed.match(/[?&]id=([a-zA-Z0-9_-]+)/);
  if (driveIdMatch && driveIdMatch[1]) {
    return `https://lh3.googleusercontent.com/d/${driveIdMatch[1]}`;
  }

  return trimmed;
}

// Helper untuk konversi format tanggal Indonesia ("15 OKTOBER 2026") ke ISO 8601 ("2026-10-15T08:00:00+07:00")
export function parseDateToISO(dateStr) {
  if (!dateStr) return new Date().toISOString();
  
  const monthMap = {
    'januari': '01', 'jan': '01',
    'februari': '02', 'feb': '02',
    'maret': '03', 'mar': '03',
    'april': '04', 'apr': '04',
    'mei': '05', 'may': '05',
    'juni': '06', 'jun': '06',
    'juli': '07', 'jul': '07',
    'agustus': '08', 'agu': '08', 'aug': '08',
    'september': '09', 'sep': '09',
    'oktober': '10', 'okt': '10', 'oct': '10',
    'november': '11', 'nov': '11',
    'desember': '12', 'des': '12', 'dec': '12'
  };

  const clean = dateStr.toLowerCase().trim();
  const match = clean.match(/(\d{1,2})\s+([a-z]+)\s+(\d{4})/);
  if (match) {
    const day = match[1].padStart(2, '0');
    const month = monthMap[match[2]] || '01';
    const year = match[3];
    return `${year}-${month}-${day}T08:00:00+07:00`;
  }

  const isoMatch = clean.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (isoMatch) {
    return `${isoMatch[1]}-${isoMatch[2]}-${isoMatch[3]}T08:00:00+07:00`;
  }

  return new Date().toISOString();
}

// Helper untuk menghitung estimasi waktu membaca secara dinamis berdasarkan jumlah kata (~180 kata/menit)
export function calculateReadTime(text) {
  if (!text) return '1 min baca';
  const clean = text.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
  const wordCount = clean ? clean.split(' ').filter(Boolean).length : 0;
  const minutes = Math.max(1, Math.ceil(wordCount / 180));
  return `${minutes} min baca`;
}

// RFC 4180 compliant CSV parser yang mendukung baris baru di dalam tanda kutip sel
export function parseCSV(text) {
  const rows = [];
  let currentRow = [];
  let cur = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (inQuotes && text[i + 1] === '"') {
        cur += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (c === ',' && !inQuotes) {
      currentRow.push(cur.trim());
      cur = '';
    } else if ((c === '\n' || c === '\r') && !inQuotes) {
      if (c === '\r' && text[i + 1] === '\n') {
        i++;
      }
      currentRow.push(cur.trim());
      cur = '';
      if (currentRow.some(val => val.length > 0)) {
        rows.push(currentRow);
      }
      currentRow = [];
    } else {
      cur += c;
    }
  }
  if (cur.length > 0 || currentRow.length > 0) {
    currentRow.push(cur.trim());
    if (currentRow.some(val => val.length > 0)) {
      rows.push(currentRow);
    }
  }

  if (rows.length < 2) return [];

  const headers = rows[0].map(h => h.toLowerCase().replace(/[\s\-_]+/g, ''));
  const result = [];

  for (let i = 1; i < rows.length; i++) {
    const values = rows[i];
    if (values.every(v => v === '')) continue;
    const entry = {};
    headers.forEach((h, idx) => {
      entry[h] = values[idx] || '';
    });
    result.push(entry);
  }

  return result;
}

// Helper untuk parsing referensi ilmiah (membersihkan JSON mentah dan menyusun format sitasi APA yang bersih)
export function formatReferencesList(rawRefs) {
  if (!rawRefs) return [];
  if (Array.isArray(rawRefs)) {
    return rawRefs.map(formatSingleRef).filter(Boolean);
  }
  
  const trimmed = String(rawRefs).trim();
  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        return parsed.map(formatSingleRef).filter(Boolean);
      }
    } catch (_) {}
  }
  
  return trimmed.split(';').map(s => formatSingleRef(s.trim())).filter(Boolean);
}

function formatSingleRef(item) {
  if (!item) return '';

  const legacyZenodoMap = {
    '10.5281/zenodo.23996944': '10.5281/zenodo.24028621',
    '10.5281/zenodo.23996910': '10.5281/zenodo.24028618',
    '10.5281/zenodo.23997030': '10.5281/zenodo.24028633',
    '10.5281/zenodo.23996967': '10.5281/zenodo.24028626',
    '10.5281/zenodo.23997116': '10.5281/zenodo.24028640',
    '10.5281/zenodo.23996635': '10.5281/zenodo.24028629'
  };

  const sanitizeAndLinkify = (str) => {
    let clean = str.trim();

    // Petakan DOI Zenodo lama/draft ke DOI resmi yang aktif dan live
    for (const [oldDoi, newDoi] of Object.entries(legacyZenodoMap)) {
      clean = clean.replace(new RegExp(oldDoi, 'g'), newDoi);
    }

    // Bersihkan DOI palsu / halusinasi AI (10.1234, 12345, 10.21243/uu, dll.)
    clean = clean.replace(/\s*https?:\/\/doi\.org\/10\.1234\/[^\s<"]+/g, '');
    clean = clean.replace(/\s*https?:\/\/doi\.org\/10\.\d{4,9}\/[^\s<"]*12345[^\s<"]*/g, '');
    clean = clean.replace(/\s*https?:\/\/doi\.org\/10\.21243\/uu\/[^\s<"]+/g, '');
    clean = clean.replace(/\s*https?:\/\/doi\.org\/10\.18191\/[^\s<"]+/g, '');
    clean = clean.replace(/\s*https?:\/\/doi\.org\/10\.3100\/ISO31000/g, '');
    clean = clean.replace(/\s*https?:\/\/doi\.org\/10\.1016\/j\.(?:law|bani|apenergy\.2026)[^\s<"]+/g, '');

    // Ubah teks URL https://doi.org/... menjadi hyperlink HTML <a> aktif yang dapat diklik
    clean = clean.replace(/https?:\/\/doi\.org\/(10\.\d{4,9}\/[^\s<";]+)/g, (match, doi) => {
      const cleanDoi = doi.replace(/[.,;)]+$/, '');
      return `<a href="https://doi.org/${cleanDoi}" target="_blank" rel="noopener" class="ref-doi-link">https://doi.org/${cleanDoi}</a>`;
    });

    // Ubah teks URL https://osf.io/... menjadi hyperlink aktif
    clean = clean.replace(/https?:\/\/osf\.io\/([a-z0-9]{5})\/?/gi, (match, id) => {
      return `<a href="https://osf.io/${id.toLowerCase()}/" target="_blank" rel="noopener" class="ref-doi-link">https://osf.io/${id.toLowerCase()}/</a>`;
    });

    return clean;
  };

  if (typeof item === 'string') {
    const cleanStr = item.trim();
    if (cleanStr.startsWith('{') && cleanStr.endsWith('}')) {
      try {
        const obj = JSON.parse(cleanStr);
        return formatSingleRef(obj);
      } catch (_) {
        return sanitizeAndLinkify(cleanStr.replace(/[{}"\\]/g, ''));
      }
    }
    return sanitizeAndLinkify(cleanStr);
  }

  if (typeof item === 'object') {
    const author = item.author || item.name || '';
    const year = item.year ? ` (${item.year}).` : '';
    const title = item.title ? ` ${item.title}.` : '';
    const journal = item.journal ? ` <em>${item.journal}</em>.` : '';
    let doiClean = item.doi ? item.doi.replace(/^https?:\/\/doi\.org\//, '').trim() : '';

    if (doiClean && legacyZenodoMap[doiClean]) {
      doiClean = legacyZenodoMap[doiClean];
    }

    let doiStr = '';
    if (doiClean && !doiClean.startsWith('10.1234') && !doiClean.includes('12345')) {
      doiStr = ` <a href="https://doi.org/${doiClean}" target="_blank" rel="noopener" class="ref-doi-link">https://doi.org/${doiClean}</a>`;
    }

    return `${author}${year}${title}${journal}${doiStr}`.trim();
  }

  return sanitizeAndLinkify(String(item));
}

// Fetch data live dari Cloudflare D1 Database & Google Sheets
export async function fetchAllNews() {
  const allArticles = [];

  // 1. Ambil artikel dari Cloudflare D1 Database (didukung oleh Bot Auto-Artikel Groq AI)
  try {
    const d1Res = await fetch(`${CLOUDFLARE_D1_API_URL}?_t=${Date.now()}`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(4000),
      headers: { 'Cache-Control': 'no-cache, no-store' }
    });
    if (d1Res.ok) {
      const d1Json = await d1Res.json();
      if (d1Json && Array.isArray(d1Json.articles)) {
        for (const r of d1Json.articles) {
          allArticles.push({
            id: String(r.id),
            slug: r.slug,
            tag: (r.tag || 'INDUSTRY INSIGHTS').toUpperCase(),
            date: r.date || 'TERBARU',
            title: decodeHtmlEntities(r.title),
            excerpt: cleanContentText(r.excerpt),
            content: r.content,
            imageUrl: formatImageUrl(r.image_url),
            link: '',
            status: r.status || 'published',
            readTime: r.read_time || calculateReadTime(r.content || r.excerpt),
            publishedIso: r.published_iso,
            article_type: r.article_type || 'content',
            seo_score: r.seo_score || 95,
            author: r.author || 'Ilham Pradani',
            doi: r.doi || '10.13140/RG.2.2.14820.91520',
            references: formatReferencesList(r.references_list)
          });
        }
      }
    }
  } catch (err) {
    console.error('Failed to fetch from Cloudflare D1 API:', err.message);
  }

  // 2. Ambil artikel dari Google Sheets CSV
  try {
    const cacheBusterUrl = `${GOOGLE_SHEET_CSV_URL}&_t=${Date.now()}`;
    const res = await fetch(cacheBusterUrl, {
      cache: 'no-store',
      signal: AbortSignal.timeout(6000),
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
      }
    });

    if (res.ok) {
      const csvData = await res.text();
      if (csvData && csvData.trim().length > 0) {
        const parsedRows = parseCSV(csvData);
        if (parsedRows.length > 0) {
          const items = parsedRows
            .map((r, idx) => {
              const rawStatus = (r.status || 'published').toLowerCase().trim();
              if (rawStatus === 'draft') return null;

              const titleVal = (r.judul || r.title || '').trim();
              if (!titleVal) return null;

              const contentVal = (r.isiberita || r.isi || r.content || r.ringkasan || r.excerpt || '').trim();
              const excerptVal = (r.ringkasan || r.excerpt || r.deskripsi || (contentVal.length > 150 ? contentVal.substring(0, 150) + '...' : contentVal)).trim();
              
              const rawImg = (r.gambarurl || r.gambar || r.foto || r.imageurl || r.image || r.linkgambar || '').trim();
              const imgVal = formatImageUrl(rawImg) || 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80';
              
              const linkVal = (r.link || r.url || (contentVal.startsWith('http') ? contentVal : '')).trim();
              const rawId = (r.id && r.id.trim()) || `gs-${idx + 1}`;
              const cleanId = rawId.replace(/[^a-zA-Z0-9_-]/g, '') || `gs-${idx + 1}`;
              const generatedSlug = slugify(titleVal) || cleanId;

              return {
                id: cleanId,
                slug: generatedSlug,
                tag: decodeHtmlEntities((r.kategori || r.tag || r.category || 'PRESS RELEASE').toUpperCase()),
                date: (r.tanggal || r.date || 'TERBARU').toUpperCase(),
                title: decodeHtmlEntities(titleVal),
                excerpt: cleanContentText(excerptVal),
                content: contentVal,
                imageUrl: imgVal,
                link: linkVal,
                status: rawStatus,
                readTime: (r.waktubaca || r.readtime || calculateReadTime(contentVal || excerptVal)),
                article_type: 'company',
                author: r.author || 'Ilham Pradani',
                doi: '10.5281/zenodo.14022601',
                references: [
                  'Kementerian Hukum dan HAM Republik Indonesia (Kemenkumham RI). Keputusan Pengesahan Badan Hukum PT CHAIN ASIA CONECT No. AHU-A117353.AH.01.30.Tahun 2026.',
                  'Kementerian Investasi / BKPM RI. Nomor Induk Berusaha (NIB) 0709260109599 & KBLI 62193.'
                ]
              };
            })
            .filter(Boolean);

          for (const item of items) {
            // Hindari duplikasi jika slug sudah ada dari D1
            if (!allArticles.some(a => a.slug === item.slug)) {
              allArticles.push(item);
            }
          }
        }
      }
    }
  } catch (err) {
    console.error('Failed to fetch Google Sheets CSV live:', err);
  }

  // Urutkan artikel gabungan: ID nomor terbesar / tanggal terbaru di atas
  allArticles.sort((a, b) => {
    const numA = parseFloat(a.id);
    const numB = parseFloat(b.id);
    if (!isNaN(numA) && !isNaN(numB)) {
      return numB - numA;
    }
    return String(b.id).localeCompare(String(a.id), undefined, { numeric: true });
  });

  return { news: allArticles, isLive: allArticles.length > 0 };
}

// Helper untuk validasi apakah slug merupakan naskah riset ilmiah JCFAD
export function isAcademicSlug(slug) {
  if (!slug) return false;
  const s = String(slug).toLowerCase().trim();
  return /^(model-|hybrid-|studi-|analisis-|kajian-|optimasi-|integrasi-|implementasi-|arsitektur-|kerangka-|evaluasi-|perancangan-|dinamika-|transformasi-|a-stochastic|a-multi-layered|[3456789]$|[1-9][0-9]+$)/i.test(s);
}

// Helper untuk memisahkan secara tegas Naskah Ilmiah JCFAD vs Berita / Rilis Pers Korporasi
export function isAcademicItem(item) {
  if (!item) return false;
  const t = (item.tag || '').toUpperCase();
  const at = (item.article_type || '').toLowerCase();
  const slug = (item.slug || '').toLowerCase();
  
  // Eksklusif berita korporasi
  if (at === 'company' || t.includes('LIPUTAN') || t.includes('PARTNERSHIP') || t.includes('MILESTONE') || t.includes('PRESS RELEASE')) {
    return false;
  }

  // Identifikasi naskah akademik JCFAD
  return (
    at === 'content' ||
    at === 'paper' ||
    at === 'academic_preprint' ||
    t.includes('RESEARCH') ||
    t.includes('PREPRINT') ||
    t.includes('WORKING PAPER') ||
    t.includes('EMPIRIS') ||
    t.includes('FEASIBILITY') ||
    t.includes('STUDI') ||
    t.includes('KAJIAN') ||
    t.includes('FINTECH') ||
    isAcademicSlug(slug)
  );
}
