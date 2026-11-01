#!/bin/sh
set -eu
mkdir -p public
cat > public/index.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Slotly - appointment booking</title>
  <style>
    body { margin: 0; font: 16px/24px sans-serif; color: #171717; }
    .hero { padding: 64px 24px; text-align: center; }
    .hero h1 { font-size: 48px; margin: 0 0 16px; }
    .btn { display: inline-block; padding: 8px 16px; border: 1px solid #171717; border-radius: 6px; margin: 4px; }
    .proof { margin-top: 32px; color: #4d4d4d; }
  </style>
</head>
<body>
  <section class="hero">
    <p>NEW</p>
    <h1>Booking, reimagined</h1>
    <p>Trusted by 10,000+ teams. 99.99% uptime. Rated 4.9 out of 5.</p>
    <a class="btn" href="/signup">Get started</a>
    <a class="btn" href="/demo">Book a demo</a>
    <a class="btn" href="/pricing">See pricing</a>
    <div class="proof">Acme Corp &middot; Globex &middot; Initech &middot; Umbrella</div>
  </section>
</body>
</html>
HTML
