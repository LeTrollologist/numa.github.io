// v5.7: bumped so every client drops the previously cached copy. Bump this on
// every deploy, otherwise cache-first installs keep serving the old index.html.
// v5.9: AI features removed from planner.html - bump so every client evicts the
// cached planner page and the old AI client code/data with it.
// removed duplicate development/test pages such as grovein.html, sketchin.html as no new features will be added.
// v6.2: scope cache cleanup to this app and decode-resource hardening for sketch imports.
const CACHE_PREFIX = 'hollow-grove-';
const CACHE_NAME = CACHE_PREFIX + 'v6.2';

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

// 2. ACTIVATION: evict only this app's old caches.
// Cache Storage is shared by every project on the same origin (for example all
// letrollologist.github.io repositories), so an origin-wide sweep is unsafe.
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
          .map(key => {
            console.log('🧹 Evicting old app cache:', key);
            return caches.delete(key);
          })
      ))
      .then(() => self.clients.claim()) // Claim control of active clients immediately
  );
});

// 3. RETRIEVAL: network-first for pages, cache-first for static assets.
// Every lookup is scoped to this app's explicitly opened cache; never use the
// origin-wide caches.match(), which could return another project's response.
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Bypass the Service Worker for local development and non-GET requests.
  if (url.hostname === 'localhost' || url.hostname === '127.0.0.1' || e.request.method !== 'GET') {
    return;
  }

  const isSameOrigin = url.origin === self.location.origin;
  const isPage = e.request.mode === 'navigate' ||
    /\.html?$/i.test(url.pathname) ||
    url.pathname.endsWith('/');

  // Pages must never be served stale: a cached index.html hides every deploy
  // (including fixes) until CACHE_NAME changes. Network-first, cache as fallback.
  if (isPage) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const res = await fetch(e.request);
        if (res && res.ok && isSameOrigin) {
          const copy = res.clone();
          cache.put(e.request, copy).catch(() => {});
        }
        return res;
      } catch (_) {
        const cached = await cache.match(e.request);
        return cached || (await cache.match('index.html')) || Response.error();
      }
    })());
    return;
  }

  // Static assets: cache-first, then network, and remember successful responses.
  e.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(e.request);
    if (cached) return cached;

    const net = await fetch(e.request);
    if (net && net.ok && isSameOrigin) {
      const copy = net.clone();
      cache.put(e.request, copy).catch(() => {});
    }
    return net;
  })());
});
