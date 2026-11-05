#!/bin/sh
set -eu
mkdir -p public
cat > public/index.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bookings</title>
  <style>
    body { margin: 0; font: 16px/24px sans-serif; color: #171717; background: #ffffff; }
    header { display: flex; justify-content: space-between; align-items: center; padding: 12px 24px; border-bottom: 1px solid rgba(0, 0, 0, 0.08); }
    nav a { margin-left: 16px; color: #171717; text-decoration: none; font-size: 14px; }
  </style>
</head>
<body>
  <header>
    <strong>Bookings</strong>
    <nav><a href="/calendar">Calendar</a><a href="/rooms">Rooms</a></nav>
  </header>
  <main><h1>Today</h1><p>Three rooms are free this afternoon.</p></main>
</body>
</html>
HTML
