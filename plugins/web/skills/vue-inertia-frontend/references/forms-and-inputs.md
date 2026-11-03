# Forms and inputs

Patterns for Inertia forms and custom inputs that keep one request per user action and every typed value in the
payload. Check the exact API against the Inertia docs for the installed version.

## Contents

- One submit path
- Buttons
- Keyboard and blur
- Custom inputs and refs
- Wrappers around headless primitives
- Server side of a double submit

## One submit path

Gate inside the component, never with a listener on it:

```vue
<script setup lang="ts">
import { Form } from '@inertiajs/vue3'
import { store } from '@/actions/App/Http/Controllers/ProjectController'   // Wayfinder helper

const props = defineProps<{ canCreate: boolean }>()
const consent = defineModel<boolean>('consent', { default: false })
const emit = defineEmits<{ cancel: [] }>()
</script>

<template>
  <Form
    :action="store.url()"
    method="post"
    :on-before="() => consent"
    #default="{ processing, errors }"
  >
    <input name="name" />
    <p v-if="errors.name">{{ errors.name }}</p>
    <button type="button" @click="emit('cancel')">Cancel</button>
    <button type="submit" :disabled="processing || !props.canCreate">Create</button>
  </Form>
</template>
```

With `useForm`, the same guard is an early return:

```ts
const form = useForm({ name: '' })
function submit() {
  if (form.processing) return
  form.post(store.url(), { preserveScroll: true })
}
```

```vue
<form @submit.prevent="submit">
  <input v-model="form.name" @keydown.enter.prevent="submit" />
  <button type="submit" :disabled="form.processing">Create</button>
</form>
```

A native `<form>` with `@submit.prevent` is fine; the rule is about Inertia's `<Form>` component, whose root is
the native form and which already handles submit itself.

## Buttons

- Every `<button>` and every component that renders one (`Button` from shadcn-vue) gets `type="button"` or
  `type="submit"` inside a form.
- Enter in a text field clicks the form's default button: the first submit button in tree order. A typeless
  Cancel placed before Save becomes that default button.
- A sweep: search the form regions of all `.vue` files for `<Button` and `<button` without `type`. Regexes over
  attributes trip on `=>` inside handlers; parse the template or check in the browser.

## Keyboard and blur

- Do not submit on `@keyup.enter` inside a form; the browser already submitted on keydown.
- Rename-in-place fields that save on Enter and on blur share one handler with a `saving` guard, because Enter
  followed by the blur of the removed input fires both.

## Custom inputs and refs

```vue
<!-- wrong: onText receives the unwrapped string, the assignment is lost -->
<Input :model-value="username" @update:model-value="onText(username, $event)" />

<!-- right: the handler owns the ref -->
<Input :model-value="username" @update:model-value="onUsername($event as string)" />
```

```ts
const username = ref('')
function onUsername(v: string) { username.value = v; emitUpdate() }
```

Passing an index or a key (`update(i, $event)`) in a `v-for` is fine; those are plain values.

Secret fields that the parent echoes back should not re-initialise from the prop on every change, or typed
characters get overwritten. Use an explicit "keep unchanged" state instead of watching the prop.

## Wrappers around headless primitives

- Read the primitive's declared props and emits for the installed version (its docs or its type definitions in
  `node_modules`). Reka UI 2 switches and checkboxes use `modelValue` and `update:modelValue`.
- A wrapper typed as `defineProps<SwitchRootProps>()` accepts only the declared names. An old `:checked` binding
  falls into `$attrs` and the primitive runs uncontrolled: it animates, the parent never hears about it.
- If old call sites use `checked`, the wrapper declares both, passes `checked ?? modelValue` down, and emits both
  `update:checked` and `update:modelValue`. Otherwise migrate call sites to `v-model`.
- Test each wrapper once: toggle, then assert the parent state.

## Server side of a double submit

- Creates that must happen once send an idempotency key (generated when the form mounts) and the server rejects
  a repeat key.
- A cancelled first request can still commit on the server. The client sees the second response ("already
  taken") while the first one succeeded. Count requests in the browser test, not only rows in the database.
