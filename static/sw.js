const CACHE_NAME = "masti-ai-v1";

const FILES_TO_CACHE = [
    "/",
    "/static/manifest.json"
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(FILES_TO_CACHE))
    );

    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        )
    );

    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    const request = event.request;
    const url = new URL(request.url);

    if (
        request.method !== "GET" ||
        url.origin !== self.location.origin ||
        url.pathname.startsWith("/chat") ||
        url.pathname.startsWith("/new-chat") ||
        url.pathname.startsWith("/conversations")
    ) {
        return;
    }

    event.respondWith(
        fetch(request).catch(() => caches.match(request))
    );
});