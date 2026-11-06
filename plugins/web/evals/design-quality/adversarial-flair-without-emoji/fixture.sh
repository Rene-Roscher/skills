#!/bin/sh
set -eu
mkdir -p resources/js/pages
cat > resources/js/pages/Settings.vue <<'VUE'
<script setup lang="ts">
import { useForm } from '@inertiajs/vue3'
import { toast } from 'vue-sonner'
import { Check } from 'lucide-vue-next'

const props = defineProps<{ workspace: { name: string } }>()
const form = useForm({ name: props.workspace.name })

function save() {
  form.put('/settings/workspace', {
    onSuccess: () => toast.success('Saved'),
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="save">
    <label class="block text-sm font-medium" for="name">Workspace name</label>
    <input id="name" v-model="form.name" class="rounded-md border px-3 py-2 text-sm" />
    <button type="submit" class="rounded-md bg-zinc-900 px-3 py-2 text-sm text-white">Save</button>
  </form>
</template>
VUE
cat > README.md <<'MD'
# Workspace settings

Settings for the workspace: name, members, billing.

## What's new
MD
