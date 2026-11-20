// PeakCut Service Worker for Mobile PWA
const CACHE_NAME = 'peakcut-v1';
const STATIC_ASSETS = [
  '/manifest.webmanifest',
  '/brand/favicon.svg',
  '/brand/icon-192.png',
  '/brand/icon-512.png',
  '/brand/logo.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  // Do not cache API requests or WebSocket/streaming requests
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/media/') || event.request.method !== 'GET') {
    return;
  }
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
