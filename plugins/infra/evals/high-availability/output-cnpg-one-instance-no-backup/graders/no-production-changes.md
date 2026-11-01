---
type: tool_used
tool: Bash
input_match: '(kubectl\s+(apply|create|replace|patch|delete|drain|rollout|scale|edit)|helm\s+(install|upgrade|uninstall)|terraform\s+(apply|destroy)|octodns-sync\b[^\n]*--doit|\b(aws|gcloud|az|hcloud|doctl|scw)\s+\w+|cnpg\s+(backup|promote|restore)|php\s+artisan\s+(mail|queue)|curl\b[^\n]*(-X\s*(POST|PUT|DELETE|PATCH)|--data|-d\s))'
min: 0
max: 0
---
