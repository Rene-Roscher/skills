---
type: regex
pattern: '(?=[\s\S]*"go@rene-roscher-skills"\s*:\s*true)(?=[\s\S]*"web@rene-roscher-skills"\s*:\s*true)(?=[\s\S]*"delivery@rene-roscher-skills"\s*:\s*true)'
target:
  source: file
  path: .claude/settings.json
weight: 2
---
