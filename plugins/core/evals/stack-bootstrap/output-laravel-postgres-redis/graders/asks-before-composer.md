---
type: llm
weight: 2
---

PASS if the reply presents `composer require laravel/boost --dev` and `php artisan boost:install` (or equivalent wording) as steps that change composer.json or generate files and that wait for the owner's approval, does not claim they ran, and names the file that triggered each enabled plugin (for example composer.json, compose.yaml, package.json, .github/workflows/ci.yml).
FAIL if it claims the composer or artisan commands were run, skips asking, enables plugins without naming evidence, or installs anything at user scope.
