---
type: llm
weight: 2
---

PASS if the chart code imports from `echarts/core` with `use([...])` registering only the renderer, chart and components it needs (not a bare `import 'echarts'` or `import * as echarts from 'echarts'`), takes series and grid colours from the CSS tokens or a theme built from them rather than hard-coded hex values, and gives the chart an accessible alternative (the ECharts aria option with `AriaComponent`, or the data or key number as text or a table).
FAIL if it imports the full ECharts bundle, hard-codes colours unrelated to the tokens, or ships the chart with no text alternative.
