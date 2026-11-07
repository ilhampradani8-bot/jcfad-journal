import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://journal.chainasiaconnect.co.id',
  compressHTML: true,
  server: {
    host: true,
  },
  vite: {
    server: {
      allowedHosts: true,
    },
  },
});

