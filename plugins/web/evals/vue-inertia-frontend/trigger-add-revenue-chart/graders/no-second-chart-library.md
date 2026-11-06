---
type: regex
pattern: '"(chart\.js|vue-chartjs|apexcharts|vue3-apexcharts|@unovis/vue|@unovis/ts|highcharts)"'
match: not_contains
target:
  source: file
  path: package.json
weight: 2
---
