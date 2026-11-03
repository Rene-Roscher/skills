#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
cat > package.json <<'JSON'
{ "name": "project-tool", "private": true, "scripts": { "start": "node src/server.js" } }
JSON
cat > src/routes.js <<'JS'
'use strict';
// HTTP routes of the project tool.
const tasks = [{ id: 1, title: 'Write spec', assignee: 'sam', dueDate: '2026-12-01' }];
module.exports = {
  'GET /tasks': () => tasks.map(({ id, title, assignee }) => ({ id, title, assignee })),
  'GET /tasks/:id': (id) => tasks.find((t) => t.id === Number(id)),
};
JS
cat > src/server.js <<'JS'
'use strict';
const routes = require('./routes');
console.log(Object.keys(routes).join('\n'));
JS
