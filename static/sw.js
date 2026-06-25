const CACHE_NAME = 'smart-ambulance-v1';
const ASSETS = [
  '/',
  '/login',
  '/dashboard',
  '/consultation',
  '/driver',
  '/hospital',
  '/admin',
  '/static/manifest.json',
  '/static/icon.png',
  '/static/icon_192.png',
  '/static/css/custom.css',
  '/static/js/api.js',
  '/static/js/auth.js',
  '/static/js/emergency.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS).catch((err) => {
        console.warn('Cache addAll failed', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cachedResponse) => {
      return cachedResponse || fetch(e.request).catch(() => {
        // Safe fallback for offline requests
      });
    })
  );
});
