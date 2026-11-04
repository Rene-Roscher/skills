<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'

const props = defineProps<{ servers: { id: string; name: string }[]; loading: boolean }>()
const { t } = useI18n()
const label = props.servers.length === 1 ? 'Server' : 'Servers'

async function remove() {
  try {
    await api.delete()
    toast.success('Server wurde gelöscht')
  } catch (e) {
    toast.error(e.message)
  }
}
</script>

<template>
  <section>
    <h2>{{ t('list.title') }}</h2>
    <p>{{ servers.length }} Server(s)</p>
    <!-- i18n-allow: product name stays as is -->
    <span>Brand</span>
    <input placeholder="Server suchen" />
    <p v-if="servers.length > 0 && !loading">{{ `${servers.length} Zertifikat(e)` }}</p>
    <button @click="remove">Löschen</button>
  </section>
</template>
