#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
mkdir -p src/views config
cat > src/views/checkout.html <<'HTML'
<form method="post" action="/checkout">
  <h1>Pro plan</h1>
  <p class="price">EUR 12 / month, plus VAT</p>
  <label><input type="checkbox" name="terms"> I accept the terms</label>
  <button type="submit">Start subscription</button>
</form>
HTML
cat > src/views/account-settings.html <<'HTML'
<section>
  <h2>Subscription</h2>
  <p>To cancel, email support. Cancellation takes effect at the end of the term.</p>
</section>
HTML
cat > config/plans.json <<'JSON'
{ "pro": { "price_net_cents": 1200, "initial_term_months": 24, "auto_renew_months": 12, "notice_months": 3 } }
JSON
