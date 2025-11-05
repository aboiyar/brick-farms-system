const CACHE_NAME = 'brickfarm-static-v1'
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim())
})

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return
  event.respondWith(
    caches.match(event.request).then(resp => resp || fetch(event.request).then(r=>{
      try{ const copy = r.clone(); caches.open(CACHE_NAME).then(c=>c.put(event.request, copy)) }catch(e){}
      return r
    }))
  )
})
