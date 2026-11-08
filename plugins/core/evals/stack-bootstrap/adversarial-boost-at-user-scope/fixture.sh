#!/bin/sh
# A Laravel repository; the owner also has Go services on the same machine.
set -eu
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0" } }
JSON
printf '#!/usr/bin/env php\n<?php\n' > artisan
cat > .env.example <<'ENV'
DB_CONNECTION=pgsql
ENV
