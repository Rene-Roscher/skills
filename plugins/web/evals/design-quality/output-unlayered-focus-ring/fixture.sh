#!/bin/sh
set -eu
mkdir -p resources/css resources/js/components
cat > resources/css/app.css <<'CSS'
@import "tailwindcss";

:focus-visible {
  outline: 2px solid var(--color-zinc-400);
  outline-offset: 2px;
}

input {
  border-color: var(--color-zinc-300);
}
CSS
cat > resources/js/components/TextField.vue <<'VUE'
<script setup lang="ts">
defineProps<{ label: string; id: string }>()
const model = defineModel<string>()
</script>

<template>
  <label :for="id" class="text-sm text-zinc-700">{{ label }}</label>
  <input
    :id="id"
    v-model="model"
    class="h-9 rounded-md border border-zinc-200 px-3 text-sm outline-none focus-visible:border-zinc-900 focus-visible:ring-2 focus-visible:ring-zinc-900/20"
  />
</template>
VUE
