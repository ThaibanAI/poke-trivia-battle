const CACHE_NAME = "poke-trivia-v2";
const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./css/style.css",
  "./js/pokemon.js",
  "./js/storage.js",
  "./js/battle.js",
  "./js/app.js",
  "./data/questions.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for everything: always try to get the freshest copy when
// online (so a new deploy shows up on the very next load), and only fall
// back to the cached copy when the network request fails (i.e. offline).
// This trades a few extra bytes on each load for never getting stuck
// showing a stale cached build after an update.
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  event.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
        return res;
      })
      .catch(() => caches.match(req))
  );
});
