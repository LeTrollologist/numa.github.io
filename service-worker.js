// v5.7: bumped so every client drops the previously cached copy. Bump this on
// every deploy, otherwise cache-first installs keep serving the old index.html.
// v5.9: AI features removed from planner.html - bump so every client evicts the
// cached planner page and the old AI client code/data with it.
const CACHE_NAME = 'hollow-grove-v5.9';

const ASSETS = [
  'index.html',
  'sketch.html',
  'grove.html',
  'planner.html',
  'converter.html',
  'install.html',
  'credits.html',
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

// 3. RETRIEVAL: network-first for pages, cache-first for static assets
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Bypass Service Worker for localhost, Render APIs, or non-GET requests to prevent CORS/PNA blocks
  if (url.hostname === 'localhost' || url.hostname === '127.0.0.1' || url.hostname.includes('onrender.com') || url.pathname.startsWith('/api') || e.request.method !== 'GET') {
    return;
  }

  const isSameOrigin = url.origin === self.location.origin;
  const isPage = e.request.mode === 'navigate' ||
    /\.html?$/i.test(url.pathname) ||
    url.pathname.endsWith('/');

  // Pages must never be served stale: a cached index.html hides every deploy
  // (including fixes) until CACHE_NAME changes. Network-first, cache as fallback.
  if (isPage) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          if (res && res.ok && isSameOrigin) {
            const copy = res.clone();
            caches.open(CACHE_NAME)
              .then(cache => cache.put(e.request, copy))
              .catch(() => {});
          }
          return res;
        })
        .catch(() => caches.match(e.request).then(res => res || caches.match('index.html')))
    );
    return;
  }

  // Static assets: cache-first, then network, and remember successful responses.
  e.respondWith(
    caches.match(e.request).then(res => {
      if (res) return res;
      return fetch(e.request).then(net => {
        if (net && net.ok && isSameOrigin) {
          const copy = net.clone();
          caches.open(CACHE_NAME)
            .then(cache => cache.put(e.request, copy))
            .catch(() => {});
        }
        return net;
      });
    })
  );
});
