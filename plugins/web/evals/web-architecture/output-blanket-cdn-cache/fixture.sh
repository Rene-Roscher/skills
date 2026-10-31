#!/bin/sh
# Nuxt site for a booking product: public pages plus one account page that reads the visitor's session.
set -eu
mkdir -p pages server/middleware
cat > package.json <<'JSON'
{ "private": true, "scripts": { "build": "nuxt build" }, "dependencies": { "nuxt": "^4.1.0", "vue": "^3.5.0" } }
JSON
cat > nuxt.config.ts <<'TS'
export default defineNuxtConfig({
  compatibilityDate: '2026-10-01',
})
TS
cat > pages/index.vue <<'VUE'
<template><main><h1>Book rooms in seconds</h1></main></template>
VUE
cat > pages/pricing.vue <<'VUE'
<template><main><h1>Pricing</h1></main></template>
VUE
cat > pages/account.vue <<'VUE'
<script setup lang="ts">
const session = useCookie('booking_session')
const { data: me } = await useFetch('/api/me', { headers: { cookie: `booking_session=${session.value}` } })
</script>
<template><main><h1>Your bookings, {{ me?.name }}</h1></main></template>
VUE
cat > server/middleware/cache.ts <<'TS'
export default defineEventHandler((event) => {
  // TODO: cache headers
})
TS
