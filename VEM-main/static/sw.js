/* ══════════════════════════════════════════════
   Service Worker — VEM Transporte Universitário
   Estratégia: Cache-First para assets estáticos
   Garante funcionamento Offline-First (RNF02)
══════════════════════════════════════════════ */

const CACHE_NAME = 'vem-v1';
const ASSETS = [
    '/',
    '/index.html',
    '/manifest.json'
];

// ── Install: Cache core assets ──
self.addEventListener('install', function(event) {
    console.log('🔧 SW: Instalando cache v1...');
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(ASSETS);
        })
    );
    self.skipWaiting();
});

// ── Activate: Clean old caches ──
self.addEventListener('activate', function(event) {
    console.log('✅ SW: Ativado');
    event.waitUntil(
        caches.keys().then(function(names) {
            return Promise.all(
                names.filter(function(n) { return n !== CACHE_NAME; })
                     .map(function(n) { return caches.delete(n); })
            );
        })
    );
    self.clients.claim();
});

// ── Fetch: Cache-first for static, network-first for API ──
self.addEventListener('fetch', function(event) {
    const url = new URL(event.request.url);

    // API calls: always try network first
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request).catch(function() {
                return new Response(
                    JSON.stringify({ erro: 'Sem conexão. Tente novamente.' }),
                    { status: 503, headers: { 'Content-Type': 'application/json' } }
                );
            })
        );
        return;
    }

    // Static assets: cache-first
    event.respondWith(
        caches.match(event.request).then(function(cached) {
            return cached || fetch(event.request).then(function(response) {
                if (response.ok) {
                    var clone = response.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(event.request, clone);
                    });
                }
                return response;
            });
        })
    );
});
