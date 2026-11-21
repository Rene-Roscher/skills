#!/bin/sh
set -eu
mkdir -p resources/js/components resources/css
cat > package.json <<'JSON'
{"private": true, "type": "module", "dependencies": {"vue": "^3.5"}}
JSON
cat > resources/js/components/FilterDrawer.vue <<'VUE'
<script setup lang="ts">
defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <aside class="drawer" :class="{ 'is-open': open }" aria-label="Filters">
    <button type="button" @click="emit('close')">Close</button>
    <slot />
  </aside>
</template>

<style scoped>
.drawer {
  position: fixed;
  inset-block: 0;
  right: 0;
  width: 22rem;
  transform: translateX(100%);
  transition: all 0.5s ease-in;
}
.drawer.is-open {
  transform: translateX(0);
}
</style>
VUE
cat > resources/css/app.css <<'CSS'
:root { color-scheme: light dark; }
CSS
