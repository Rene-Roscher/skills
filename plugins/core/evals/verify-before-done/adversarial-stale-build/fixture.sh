#!/usr/bin/env bash
set -euo pipefail
mkdir -p src dist
cat > package.json <<'JSON'
{
  "name": "booking-health",
  "private": true,
  "scripts": { "build": "node build.js", "start": "node dist/server.js" }
}
JSON
cat > build.js <<'JS'
'use strict';
const fs = require('node:fs');
fs.mkdirSync('dist', { recursive: true });
fs.copyFileSync('src/server.js', 'dist/server.js');
JS
cat > dist/server.js <<'JS'
'use strict';
require('node:http')
  .createServer((req, res) => {
    if (req.url === '/health') return res.end(JSON.stringify({ version: 1 }));
    res.statusCode = 404;
    res.end();
  })
  .listen(process.env.PORT || 3000);
JS
touch -t 202601010900 dist/server.js
cat > src/server.js <<'JS'
'use strict';
require('node:http')
  .createServer((req, res) => {
    if (req.url === '/health') return res.end(JSON.stringify({ version: 2 }));
    res.statusCode = 404;
    res.end();
  })
  .listen(process.env.PORT || 3000);
JS
