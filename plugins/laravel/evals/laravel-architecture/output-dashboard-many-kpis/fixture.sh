#!/bin/sh
set -eu
mkdir -p app/Http/Controllers resources/js/pages docs
cat > app/Http/Controllers/DashboardController.php <<'PHP'
<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Models\Invoice;
use App\Models\Project;
use App\Models\Task;
use App\Models\TimeEntry;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

final class DashboardController
{
    public function __invoke(Request $request): Response
    {
        $tenantId = $request->user()->current_tenant_id;

        return Inertia::render('Dashboard', [
            'openTasks' => Task::where('tenant_id', $tenantId)->whereNull('done_at')->count(),
            'overdueByMember' => Task::where('tenant_id', $tenantId)->whereNull('done_at')
                ->where('due_at', '<', now())->selectRaw('assignee_id, count(*) as overdue')
                ->groupBy('assignee_id')->get(),
            'hoursThisQuarter' => TimeEntry::where('tenant_id', $tenantId)
                ->where('started_at', '>=', now()->startOfQuarter())->sum('minutes') / 60,
            'revenueByMonth' => Invoice::where('tenant_id', $tenantId)->where('issued_at', '>=', now()->subYear())
                ->selectRaw("to_char(issued_at, 'YYYY-MM') as month, sum(total_cents) as total")
                ->groupBy('month')->orderBy('month')->get(),
            'throughput' => Task::where('tenant_id', $tenantId)->whereNotNull('done_at')
                ->where('done_at', '>=', now()->subDays(90))
                ->selectRaw('date(done_at) as day, count(*) as done')->groupBy('day')->get(),
            'activity' => Project::where('tenant_id', $tenantId)->with('events.user')->latest()->limit(20)->get(),
        ]);
    }
}
PHP
cat > resources/js/pages/Dashboard.vue <<'VUE'
<script setup lang="ts">
defineProps<{
  openTasks: number
  overdueByMember: { assignee_id: number; overdue: number }[]
  hoursThisQuarter: number
  revenueByMonth: { month: string; total: number }[]
  throughput: { day: string; done: number }[]
  activity: unknown[]
}>()
</script>

<template>
  <div class="grid grid-cols-3 gap-4">
    <KpiCard label="Open tasks" :value="openTasks" />
    <OverdueTable :rows="overdueByMember" />
    <KpiCard label="Hours this quarter" :value="hoursThisQuarter" />
    <RevenueChart :points="revenueByMonth" />
    <ThroughputChart :points="throughput" />
    <ActivityFeed :items="activity" />
  </div>
</template>
VUE
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Laravel 13, Inertia 3 with Vue 3, PostgreSQL 17, Redis for cache and queues.
- Multi-tenant B2B: every table has `tenant_id`. Largest tenant: 2.1 million tasks, 9 million time entries.
- The activity feed sits below the fold. Revenue and throughput are fine if a few minutes old; open tasks should
  be current within a minute.
MD
