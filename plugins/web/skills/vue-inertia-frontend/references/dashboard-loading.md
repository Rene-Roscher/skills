# Dashboard loading

How a page that reads several sources loads each widget on its own. Example: a project dashboard with an open-task
count, overdue tasks per member, a throughput chart and an activity feed. APIs checked against Inertia 3
(https://inertiajs.com/docs/v3/data-props/deferred-props, `load-when-visible`, `partial-reloads`, `polling`, and
https://inertiajs.com/docs/v3/advanced/testing, verified 2026-11-06). The server side (cache, rollups, cost
measurement) is in `laravel-architecture`, references/dashboard-data.md.

## Plan per widget first

Before code, one row per widget:

| Widget | Source and cost (cold, warm) | Loads | Group | Fresh within | Poll |
|---|---|---|---|---|---|
| Open tasks | one indexed count, 3 ms | first response | | 60 s | 60 s, background pause |
| Overdue per member | aggregate over tasks, 400 ms cold | deferred | `team` | 5 min | none |
| Throughput chart | rollup table, 15 ms | deferred | `charts` | 1 h | none |
| Activity feed | joined events, 120 ms | when visible | | 30 s | 30 s while visible |

- First response: what the layout and the first glance need, and only when it is cheap.
- One deferred group per source or cost class. Props without a group share the `default` group, which is one
  request, so the slowest source decides when all of them appear. Separate groups load in parallel.
- Below the fold: an optional prop behind `<WhenVisible>`; it is never computed unless the widget scrolls into
  view.
- Poll only what goes stale fast, only its own props, and pause while the tab is hidden.

## Vue

```vue
<script setup lang="ts">
import { Deferred, WhenVisible, router, usePoll } from '@inertiajs/vue3'

defineProps<{
  openTasks: number
  overdueByMember?: OverdueRow[]
  throughput?: ThroughputPoint[]
  activity?: ActivityItem[]
}>()

usePoll(60_000, { only: ['openTasks'] }, { background: 'pause' })
</script>

<template>
  <KpiCard :value="openTasks" />

  <Deferred data="overdueByMember">
    <template #fallback><WidgetSkeleton rows="5" /></template>
    <template #rescue="{ reloading }">
      <WidgetError :busy="reloading" @retry="router.reload({ only: ['overdueByMember'] })" />
    </template>
    <OverdueTable :rows="overdueByMember!" />
  </Deferred>

  <Deferred data="throughput">
    <template #fallback><WidgetSkeleton chart /></template>
    <ThroughputChart :points="throughput!" />
  </Deferred>

  <WhenVisible data="activity" :buffer="200">
    <template #fallback><WidgetSkeleton rows="8" /></template>
    <ActivityFeed :items="activity!" />
  </WhenVisible>
</template>
```

- The `#rescue` slot renders when the server marked the prop `rescue: true` and it failed; without rescue, a
  throwing prop fails its whole group.
- Skeletons keep the widget's final size, so a late widget does not shift the others.
- An empty result is a designed empty state, not the skeleton forever (`design-quality`, states rule).
- `usePoll` throttles hidden tabs by 90 % by default (since 3.9.0); `background: 'pause'` stops it while hidden
  and fires on return if the interval has passed. `keepAlive` is deprecated in favour of `background: 'continue'`.
- A realtime event reloads only the affected widget's prop, debounced (`web-architecture`, inertia dashboard
  reference).

## Proof

- Backend test: the first response is `missing` every deferred and optional prop; `loadDeferredProps('team', ...)`
  returns only that group's props; `reloadOnly('activity', ...)` returns the feed.
- Browser test: route the request whose `X-Inertia-Partial-Data` header names the `team` props to a delay or a
  500. The other widgets render, the blocked one shows its skeleton, then its error with a retry, and one retry
  click sends one request with only that prop.
- Request log on a cold load: one page request plus one per deferred group, nothing for widgets below the fold.
