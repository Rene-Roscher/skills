<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'

const props = defineProps<{ servers: { id: string }[]; loading: boolean }>()
const { t } = useI18n()
const handlers = { select: (e: Event) => e }

function onError(e: Error) {
  console.error(e.message)
  toast.error(t('servers.delete_failed'))
}
</script>

<template>
  <section>
    <h2>{{ t('servers.title') }}</h2>
    <p v-if="props.servers.length > 0 && !props.loading">{{ t('servers.count', { count: props.servers.length }) }}</p>
    <button type="button" :title="t('servers.refresh')" @click="handlers.select(e)">&nbsp;{{ t('servers.refresh') }}</button>
    <code>npm run dev</code>
    <span>{{ n(durationTotal) }} ms</span>
    <span>·</span>
  </section>
</template>
