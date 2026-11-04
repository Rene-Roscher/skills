#!/bin/sh
set -eu
mkdir -p resources/js/pages/Servers resources/js/locales/de resources/js/locales/en app/Http/Controllers
cat > resources/js/pages/Servers/Index.vue <<'VUE'
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { router } from '@inertiajs/vue3'

const props = defineProps<{ servers: { id: string; name: string }[]; expiring: number }>()
const { t } = useI18n()

function removeAll() {
  router.delete('/servers', {
    onError: (e) => toast.error(e.message),
  })
}
</script>

<template>
  <section>
    <h1>{{ t('servers.title') }}</h1>
    <p>{{ props.servers.length }} Server(s)</p>
    <p v-if="props.expiring">{{ `${props.expiring} ` + t('servers.certificates_expiring') }}</p>
    <button type="button" @click="removeAll">Alle löschen</button>
  </section>
</template>
VUE
cat > resources/js/locales/de/servers.json <<'JSON'
{
  "servers": {
    "title": "Server",
    "certificates_expiring": "Zertifikat(e) laufen bald ab"
  }
}
JSON
cat > resources/js/locales/en/servers.json <<'JSON'
{
  "servers": {
    "title": "Servers",
    "certificates_expiring": "certificate(s) expiring soon"
  }
}
JSON
cat > app/Http/Controllers/ServerController.php <<'PHP'
<?php

namespace App\Http\Controllers;

use App\Services\ServerService;
use Illuminate\Http\Request;

class ServerController
{
    public function __construct(private ServerService $servers) {}

    public function destroyAll(Request $request)
    {
        try {
            $count = $this->servers->deleteAllFor($request->user());
        } catch (\Throwable $e) {
            return back()->with('error', $e->getMessage());
        }

        return back()->with('status', $count . ' Server gelöscht');
    }
}
PHP
