#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
mkdir -p src/views
cat > src/views/members.html <<'HTML'
<table class="members">
  <thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead>
  <tbody>
    {{#members}}
    <tr><td>{{name}}</td><td>{{email}}</td><td>{{role}}</td></tr>
    {{/members}}
  </tbody>
</table>
HTML
cat > src/csp.json <<'JSON'
{ "img-src": ["'self'", "data:"] }
JSON
