---
type: regex
pattern: '"echarts"\s*:[\s\S]*"vue-echarts"\s*:|"vue-echarts"\s*:[\s\S]*"echarts"\s*:'
target:
  source: file
  path: package.json
weight: 2
---
