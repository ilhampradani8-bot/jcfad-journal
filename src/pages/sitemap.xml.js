import { fetchAllNews, formatImageUrl, parseDateToISO, isAcademicItem } from '../lib/news';

function escapeXml(unsafe) {
  if (!unsafe) return '';
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export async function GET() {
  const { news } = await fetchAllNews();
  const today = new Date().toISOString().split('T')[0];

  // Filter khusus naskah ilmiah / artikel jurnal JCFAD
  const academicPapers = news.filter((item) => isAcademicItem(item));

  const journalStaticUrls = [
    {
      loc: 'https://journal.chainasiaconnect.co.id/',
      lastmod: today,
      changefreq: 'daily',
      priority: '1.0',
      images: [
        {
          loc: 'https://journal.chainasiaconnect.co.id/images/jcfad-seal.png',
          title: 'Journal of Coastal Frontiers & Applied Development (JCFAD) Official Seal'
        }
      ]
    },
    {
      loc: 'https://journal.chainasiaconnect.co.id/editorial-board',
      lastmod: today,
      changefreq: 'monthly',
      priority: '0.9',
      images: []
    },
    {
      loc: 'https://journal.chainasiaconnect.co.id/focus-scope',
      lastmod: today,
      changefreq: 'monthly',
      priority: '0.9',
      images: []
    },
    {
      loc: 'https://journal.chainasiaconnect.co.id/indexing',
      lastmod: today,
      changefreq: 'weekly',
      priority: '0.9',
      images: []
    },
    {
      loc: 'https://journal.chainasiaconnect.co.id/ethics',
      lastmod: today,
      changefreq: 'monthly',
      priority: '0.85',
      images: []
    },
    {
      loc: 'https://journal.chainasiaconnect.co.id/submissions',
      lastmod: today,
      changefreq: 'monthly',
      priority: '0.9',
      images: []
    }
  ];

  const paperUrls = [];
  for (const article of academicPapers) {
    const imgUrl = formatImageUrl(article.imageUrl);
    const images = imgUrl ? [{ loc: imgUrl, title: escapeXml(article.title) }] : [];
    const articleDate = parseDateToISO(article.date).split('T')[0] || today;

    // 1. Halaman Utama Artikel Jurnal (HTML Landing Page - tanpa /newsroom/)
    paperUrls.push({
      loc: `https://journal.chainasiaconnect.co.id/${article.slug}`,
      lastmod: articleDate,
      changefreq: 'monthly',
      priority: '0.95',
      images
    });

    // 2. Dokumen Galley PDF Resmi pada Subdomain Jurnal yang Sama (Syarat Wajib Google Scholar)
    paperUrls.push({
      loc: `https://journal.chainasiaconnect.co.id/docs/${article.slug}.pdf`,
      lastmod: articleDate,
      changefreq: 'monthly',
      priority: '0.90',
      images: []
    });
  }

  const allUrls = [...journalStaticUrls, ...paperUrls];

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${allUrls
  .map(
    (u) => `  <url>
    <loc>${u.loc}</loc>
    <lastmod>${u.lastmod}</lastmod>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
${u.images
  .map(
    (img) => `    <image:image>
      <image:loc>${img.loc}</image:loc>
      <image:title>${img.title}</image:title>
    </image:image>`
  )
  .join('\n')}
  </url>`
  )
  .join('\n')}
</urlset>`;

  return new Response(xml, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}

