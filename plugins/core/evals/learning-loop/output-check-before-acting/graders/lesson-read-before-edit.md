---
type: tool_order
before:
  tool: Read
  input_match: 'migrations-need-down'
after:
  tool: Write
  input_match: 'db/migrations/'
weight: 3
---
