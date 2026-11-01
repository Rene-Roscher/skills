#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p copy
cat > copy/facts.md <<'EOF'
# Facts for the status page product (confirmed by the product owner)

- Check interval: from 30 seconds, set per check. Default is 60 seconds.
- Locations: checks run from four locations (Frankfurt, Dublin, Virginia, Singapore).
- Alert trigger: an alert fires when two locations report the site as down.
- Alert channels: email, SMS, phone call, Slack, Microsoft Teams.
- Status page: public, custom domain on the Team plan.
- Free plan: 5 checks. Team plan: 50 checks.
- Customer count: not published, no consent records exist.
- No benchmark against other tools has been run.
EOF
cat > copy/landing.md <<'EOF'
# Our Powerful Status Page Platform

In today's fast-paced digital world, uptime is not just a metric. It's peace of mind. We are the fastest and best status page on the market, trusted by over 10,000 teams worldwide. Our seamless, robust and cutting-edge platform empowers your team to stay ahead of every outage, ensuring a flawless experience for your customers.

Get Started
EOF
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add landing draft'
