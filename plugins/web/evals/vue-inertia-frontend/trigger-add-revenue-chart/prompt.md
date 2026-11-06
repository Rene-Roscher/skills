---
description: "Should trigger vue-inertia-frontend: a chart in an Inertia page with no chart library yet. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Picks Apache ECharts through vue-echarts (added to package.json), imports it tree-shaken from echarts/core with only the chart and components it uses, takes colours from the design tokens, and gives the chart an accessible text or table alternative or the ECharts aria option. No Chart.js, ApexCharts or Unovis.
tags: [vue-inertia-frontend, trigger]
runs: 3
max_turns: 14
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add a monthly revenue line chart to the dashboard page (`resources/js/pages/Dashboard.vue`, prop `revenue` is a list of `{ month, cents }`). Pick a chart library, add it to package.json and set it up. I will run the install myself.
