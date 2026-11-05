#!/bin/sh
set -eu
mkdir -p resources/js/components
cat > resources/js/components/PinToggle.vue <<'VUE'
<script setup lang="ts">
import { Toggle, TooltipContent, TooltipPortal, TooltipProvider, TooltipRoot, TooltipTrigger } from 'reka-ui'
import { Pin } from 'lucide-vue-next'

const pinned = defineModel<boolean>({ default: false })
</script>

<template>
  <TooltipProvider>
    <TooltipRoot>
      <TooltipTrigger as-child>
        <Toggle
          v-model="pinned"
          aria-label="Pin project"
          class="inline-flex size-8 items-center justify-center rounded-md text-zinc-600 hover:bg-zinc-100 data-[state=on]:bg-zinc-900 data-[state=on]:text-white"
        >
          <Pin class="size-4" aria-hidden="true" />
        </Toggle>
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent class="rounded px-2 py-1 text-xs">Pin project</TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>
VUE
