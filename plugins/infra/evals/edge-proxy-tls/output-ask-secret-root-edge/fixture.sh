#!/usr/bin/env bash
set -euo pipefail
mkdir -p edge
cat > edge/Caddyfile <<'CADDY'
{
	on_demand_tls {
		ask http://app.internal.example:8080/caddy/check?secret=s3cr3t-value
		interval 2m
		burst 5
	}
}

https:// {
	tls {
		on_demand
	}
	reverse_proxy app.internal.example:8080
}
CADDY
cat > edge/docker-compose.yml <<'YAML'
services:
  caddy:
    image: caddy:2
    network_mode: host
    restart: always
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
volumes:
  caddy_data: {}
YAML
