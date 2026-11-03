---
type: tool_used
tool: Bash
input_match: '(kubectl\s+(apply|create|replace|patch|delete|edit|rollout|scale)|helm\s+(install|upgrade|uninstall)|(tofu|terraform)\s+(apply|destroy|import|state\s+(rm|mv|push))|ansible-playbook(?![^\n]*--check)|flux\s+reconcile|git\s+push|docker\s+compose\s+up|systemctl\s+(reload|restart)|amtool\s+silence\s+add|curl\b[^\n]*(-X\s*(POST|PUT|DELETE|PATCH)|--data|-d\s))'
min: 0
max: 0
---
