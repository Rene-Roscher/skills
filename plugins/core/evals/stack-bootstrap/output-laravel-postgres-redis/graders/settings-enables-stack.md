---
type: regex
pattern: '(?=[\s\S]*"laravel@rene-roscher-skills"\s*:\s*true)(?=[\s\S]*"data@rene-roscher-skills"\s*:\s*true)(?=[\s\S]*"web@rene-roscher-skills"\s*:\s*true)(?=[\s\S]*"delivery@rene-roscher-skills"\s*:\s*true)(?=[\s\S]*"laravel-boost@claude-plugins-official"\s*:\s*true)'
target:
  source: file
  path: .claude/settings.json
weight: 2
---
