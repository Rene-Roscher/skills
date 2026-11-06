---
type: llm
weight: 2
---

PASS if the relative time is built with `Intl.RelativeTimeFormat` or date-fns (`formatDistance`, `formatDistanceToNow`) and the toast goes through vue-sonner (the existing `notifySuccess` wrapper or `toast` from vue-sonner), and the reply says in a sentence or two why moment and a second toast library were not added (moment is in maintenance mode, one library per need, both needs are already covered).
FAIL if moment, vue-toastification or another toast library is added or imported, or the reply silently ignores the request without explaining.
