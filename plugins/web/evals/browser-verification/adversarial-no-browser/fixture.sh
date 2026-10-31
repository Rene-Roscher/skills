#!/bin/sh
set -eu
mkdir -p resources/js/components
cat > resources/js/components/ConfirmDialog.vue <<'VUE'
<script setup lang="ts">
defineProps<{ open: boolean; message: string }>()
const emit = defineEmits<{ close: []; confirm: [] }>()
</script>

<template>
  <div v-if="open" role="dialog" aria-modal="true" data-testid="confirm-dialog">
    <p>{{ message }}</p>
    <button type="button" data-testid="confirm-dialog-close" @click="emit('close')">Close</button>
    <button type="button" data-testid="confirm-dialog-confirm" @click="emit('confirm')">Confirm</button>
  </div>
</template>
VUE
