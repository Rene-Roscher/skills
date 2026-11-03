#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
mkdir -p site legal
cat > site/index.html <<'HTML'
<header><a href="/">ShiftBoard</a></header>
<main>
  <h1>Shift planning for clinics and care homes</h1>
  <p>Trusted by 500+ teams. The fastest rota tool in Germany.</p>
  <a href="/signup">Start free</a>
</main>
<footer><a href="/privacy">Privacy</a></footer>
HTML
cat > legal/terms.md <<'MD'
# Terms of service
Version 1. These terms apply to businesses and individuals.
We may change these terms at any time; continued use means you accept the change.
MD
