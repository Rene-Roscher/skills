#!/bin/sh
set -eu
mkdir -p resources/js/pages resources/css
cat > package.json <<'JSON'
{
  "private": true,
  "type": "module",
  "dependencies": {
    "@inertiajs/vue3": "^3.0.0",
    "@lucide/vue": "^1.17.0",
    "@vueuse/core": "^12.8.2",
    "reka-ui": "^2.9.8",
    "tailwindcss": "^4.1.1",
    "vue": "^3.5.13",
    "vue-sonner": "^2.0.0"
  },
  "devDependencies": {
    "@laravel/vite-plugin-wayfinder": "^0.1.3",
    "typescript": "^5.2.2",
    "vue-tsc": "^3.3.13"
  }
}
JSON
cat > resources/css/app.css <<'CSS'
@import "tailwindcss";
:root { --chart-1: oklch(0.55 0.15 250); --chart-grid: oklch(0.9 0 0); --foreground: oklch(0.2 0 0); }
.dark { --chart-1: oklch(0.7 0.13 250); --chart-grid: oklch(0.3 0 0); --foreground: oklch(0.95 0 0); }
CSS
cat > resources/js/pages/Dashboard.vue <<'VUE'
<script setup lang="ts">
defineProps<{ revenue: { month: string; cents: number }[] }>()
</script>

<template>
  <section class="space-y-4 p-6">
    <h1 class="text-xl font-semibold">Dashboard</h1>
    <div class="rounded-lg border p-4">
      <h2 class="text-sm font-medium">Revenue per month</h2>
      <!-- chart goes here -->
    </div>
  </section>
</template>
VUE
