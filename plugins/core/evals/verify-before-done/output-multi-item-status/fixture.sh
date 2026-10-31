#!/usr/bin/env bash
set -euo pipefail
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "project-tool", "private": true, "scripts": { "test": "node --test" } }
JSON
cat > README.md <<'MD'
# Projcet tool

Boards, tasks and milestones for small teams.
MD
cat > src/slug.js <<'JS'
'use strict';
// Turns a board name into a URL slug: lower case, words joined by hyphens.
function slugify(name) {
  return name.trim().toLowerCase();
}
module.exports = { slugify };
JS
cat > test/slug.test.js <<'JS'
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { slugify } = require('../src/slug');

test('joins words with hyphens', () => {
  assert.strictEqual(slugify('  Q4 Roadmap Review '), 'q4-roadmap-review');
});
JS
