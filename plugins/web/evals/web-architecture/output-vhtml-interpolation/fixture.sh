#!/bin/sh
set -eu
mkdir -p resources/js/components resources/js/locales
cat > package.json <<'JSON'
{ "private": true, "type": "module", "dependencies": { "vue": "^3.5.0", "vue-i18n": "^11.0.0" } }
JSON
cat > resources/js/components/InviteBanner.vue <<'VUE'
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{ org: { name: string } }>()
const { t } = useI18n()
</script>

<template>
  <p class="invite-banner">{{ t('invite.body', { name: org.name }) }}</p>
</template>
VUE
cat > resources/js/locales/en.json <<'JSON'
{ "invite": { "body": "You were invited to join {name}." } }
JSON
cat > resources/js/locales/de.json <<'JSON'
{ "invite": { "body": "Du wurdest eingeladen, {name} beizutreten." } }
JSON
