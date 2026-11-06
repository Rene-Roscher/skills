#!/bin/sh
set -eu
mkdir -p resources/js/components resources/css
cat > resources/js/components/ProjectSheet.vue <<'VUE'
<script setup lang="ts">
import { ref } from 'vue'
import ConfirmDelete from './ConfirmDelete.vue'

defineProps<{ open: boolean; projectName: string }>()
const emit = defineEmits<{ close: []; delete: [] }>()
const confirming = ref(false)
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 bg-black/40" @click.self="emit('close')">
    <aside class="fixed inset-y-0 right-0 z-50 w-[28rem] bg-white p-6 shadow-xl" role="dialog" aria-modal="true" aria-labelledby="sheet-title">
      <h2 id="sheet-title" class="text-lg font-semibold">{{ projectName }}</h2>
      <button type="button" class="mt-6 rounded-md border px-3 py-2 text-sm text-red-700" @click="confirming = true">Delete project</button>
    </aside>
    <ConfirmDelete v-if="confirming" :name="projectName" @cancel="confirming = false" @confirm="emit('delete')" />
  </div>
</template>
VUE
cat > resources/js/components/ConfirmDelete.vue <<'VUE'
<script setup lang="ts">
defineProps<{ name: string }>()
const emit = defineEmits<{ cancel: []; confirm: [] }>()
</script>

<template>
  <div class="fixed inset-0 z-40 grid place-items-center bg-black/40">
    <div class="w-96 rounded-xl bg-white p-6" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title">
      <h2 id="confirm-title" class="font-semibold">Delete {{ name }}?</h2>
      <div class="mt-6 flex justify-end gap-2">
        <button type="button" class="rounded-md border px-3 py-2 text-sm" @click="emit('cancel')">Cancel</button>
        <button type="button" class="rounded-md bg-red-700 px-3 py-2 text-sm text-white" @click="emit('confirm')">Delete</button>
      </div>
    </div>
  </div>
</template>
VUE
cat > resources/css/app.css <<'CSS'
@import "tailwindcss";
CSS
