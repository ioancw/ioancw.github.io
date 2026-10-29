// Sky chart service worker: keeps the page itself available offline.
// Same-origin requests go to the network first so updates show straight away,
// falling back to the cached copy. Forecast APIs are not intercepted; the page
// keeps its own copy of the last forecast.
const CACHE = "skychart-v1";
const SHELL = ["./", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        if (res.ok) {
          const copy = res.clone();
          // Store the page under "./" whatever its query string, so any saved site opens offline.
          const key = e.request.mode === "navigate" ? "./" : e.request;
          caches.open(CACHE).then((c) => c.put(key, copy));
        }
        return res;
      })
      .catch(() => caches.match(e.request.mode === "navigate" ? "./" : e.request, { ignoreSearch: true })
        .then((r) => r ?? Response.error())),
  );
});
