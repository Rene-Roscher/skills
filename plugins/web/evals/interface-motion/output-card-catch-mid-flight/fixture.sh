#!/bin/sh
set -eu
mkdir -p resources/js/components
cat > resources/js/components/SwipeCard.vue <<'VUE'
<script setup lang="ts">
import { ref } from 'vue'

const offset = ref(0)
const dragging = ref(false)
let startX = 0

function down(event: PointerEvent) {
  startX = event.clientX
  ;(event.currentTarget as HTMLElement).setPointerCapture(event.pointerId)
}

function move(event: PointerEvent) {
  if (!(event.buttons & 1)) return
  dragging.value = true
  offset.value = event.clientX - startX
}

function up() {
  dragging.value = false
  offset.value = 0
}
</script>

<template>
  <div
    class="card"
    :class="{ dragging }"
    :style="{ translate: `${offset}px 0` }"
    @pointerdown="down"
    @pointermove="move"
    @pointerup="up"
  >
    <slot />
  </div>
</template>

<style scoped>
.card {
  touch-action: pan-y;
  transition: translate 0.45s cubic-bezier(0.2, 0, 0, 1);
}
.card.dragging {
  transition: none;
}
</style>
VUE
