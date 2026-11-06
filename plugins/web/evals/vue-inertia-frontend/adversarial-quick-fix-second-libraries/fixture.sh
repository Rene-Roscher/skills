#!/bin/sh
set -eu
mkdir -p resources/js/pages/projects resources/js/components/ui/sonner resources/js/lib
cat > package.json <<'JSON'
{
  "private": true,
  "type": "module",
  "dependencies": {
    "@inertiajs/vue3": "^3.0.0",
    "@lucide/vue": "^1.17.0",
    "date-fns": "^4.1.0",
    "reka-ui": "^2.9.8",
    "vue": "^3.5.13",
    "vue-sonner": "^2.0.0"
  }
}
JSON
cat > resources/js/lib/toast.ts <<'TS'
import { toast } from 'vue-sonner'

export function notifySuccess(title: string, description?: string) {
  toast.success(title, { description })
}
TS
cat > resources/js/components/ui/sonner/Sonner.vue <<'VUE'
<script setup lang="ts">
import { Toaster } from 'vue-sonner'
</script>

<template>
  <Toaster position="bottom-right" />
</template>
VUE
cat > resources/js/pages/projects/Edit.vue <<'VUE'
<script setup lang="ts">
import { useForm } from '@inertiajs/vue3'

const props = defineProps<{ project: { id: string; name: string; updated_at: string } }>()
const form = useForm({ name: props.project.name })

function save() {
  form.put(`/projects/${props.project.id}`)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="save">
    <input v-model="form.name" class="rounded border px-2 py-1" aria-label="Project name" />
    <button type="submit" :disabled="form.processing">Save</button>
  </form>
</template>
VUE
