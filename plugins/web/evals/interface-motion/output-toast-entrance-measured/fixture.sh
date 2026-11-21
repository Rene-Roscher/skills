#!/bin/sh
set -eu
mkdir -p resources/js/components
cat > package.json <<'JSON'
{"private": true, "type": "module", "devDependencies": {"playwright": "^1.50.0"}, "dependencies": {"vue": "^3.5"}}
JSON
cat > resources/js/components/SavedToast.vue <<'VUE'
<template>
  <Transition name="toast" appear>
    <div class="toast" role="status">Booking saved</div>
  </Transition>
</template>

<style scoped>
.toast-enter-active { transition: translate 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s; }
.toast-enter-from { translate: 0 24px; opacity: 0; }
</style>
VUE
