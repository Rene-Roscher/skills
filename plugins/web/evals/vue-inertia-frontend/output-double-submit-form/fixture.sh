#!/bin/sh
set -eu
mkdir -p resources/js/pages/Projects
cat > package.json <<'JSON'
{ "private": true, "dependencies": { "vue": "^3.5.0", "@inertiajs/vue3": "^2.1.0", "reka-ui": "^2.6.0" } }
JSON
cat > resources/js/pages/Projects/Create.vue <<'VUE'
<script setup lang="ts">
import { Form, router } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Button } from '@/components/ui/button'

const accepted = ref(false)

function onSubmit() {
  if (!accepted.value) return
}

function cancel() {
  router.visit('/projects')
}
</script>

<template>
  <Form action="/projects" method="post" @submit.prevent="onSubmit" #default="{ processing, errors }">
    <input name="name" @keyup.enter="onSubmit" />
    <p v-if="errors.name">{{ errors.name }}</p>
    <label><input v-model="accepted" type="checkbox" /> I accept the terms</label>
    <Button @click="cancel">Cancel</Button>
    <Button>Create</Button>
  </Form>
</template>
VUE
