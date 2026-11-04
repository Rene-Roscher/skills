---
type: regex
pattern: '```(php|ya?ml|json|sh|bash)[^`]*(kafka|rdkafka|EventStore|event_store)'
flags: i
match: not_contains
weight: 2
---
