const CACHE_NAME = 'hollow-grove-v2.1';
const ASSETS = [
  'index.html',
  'sketch.html',      // Prod link
  'sketchin.html',    // Dev link
  'grove.html',       // Prod link
  'grovein.html',     // Dev link
  'planner.html',
  'converter.html',
  'install.html',
  'gamein.html',      // Dev link
  'game.html',        // Prod link (if renamed)
  'compute-optimizer.js',
  'mobile-optimizer.js',
  'apple-optimizer.js',
  'manifest.json',
  'favicon/favicon.svg',
  'favicon/favicon-96x96.png',
  'favicon/web-app-manifest-192x192.png',
  'favicon/web-app-manifest-512x512.png',
  'favicon/apple-touch-icon.png',
  'favicon/favicon.ico'
];

// 1. INSTALLATION: Cache static assets with fail-safe resilience
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        // Use Promise.allSettled so the service worker installs successfully
        // in both development (local) and production (GitHub Pages) environments!
        const cachePromises = ASSETS.map(url => {
          return cache.add(url).catch(err => {
            console.warn(`⚠️ Offline Cache skipped asset: ${url} (expected in some environments)`, err);
          });
        });
        return Promise.allSettled(cachePromises);
      })
      .then(() => self.skipWaiting()) // Force active immediately
  );
});

// 2. ACTIVATION: Automatically sweep and evict deprecated caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log('🧹 Evicting old cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim()) // Claim control of active clients immediately
  );
});

// 3. RETRIEVAL: Serve cached assets first, with network fallback
self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(res => {
      return res || fetch(e.request);
    })
  );
});
