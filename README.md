# Journal of Coastal Frontiers & Applied Development (JCFAD)

Official independent open-access scholarly journal portal hosted at **[https://journal.chainasiaconnect.co.id](https://journal.chainasiaconnect.co.id)**.

- **Publisher**: PT CHAIN ASIA CONECT Research & Development Division
- **Focus & Scope**: Empirical Regional Studies, Supply Chain Finance, Cold-Chain Logistics, Indonesian Civil Code (KUHPerdata) Contract Law, and Applied Development in 3T Frontiers (Krui, Pesisir Barat Regency, Lampung, Indonesia).
- **Indexing & Repositories**: Scopus Standard, CERN Zenodo (DOI Prefix `10.5281/zenodo.*`), Open Science Framework (OSF, DOI Prefix `10.17605/OSF.IO/*`), Crossref, Google Scholar, SINTA Kemendikbudristek, ORCID.
- **Licensing**: Creative Commons Attribution 4.0 International (CC BY 4.0 Open Access).
- **Architecture**: 100% Serverless on Cloudflare Pages Edge, zero VPS/hardware dependency, 24/7 global uptime.

## 🛠️ Development & Deployment

```bash
# Build static site
npm run build

# Deploy directly to Cloudflare Pages Edge
npx wrangler pages deploy dist --project-name=jcfad-journal
```
