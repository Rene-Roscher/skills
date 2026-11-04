# Terms: operations and developer tooling

verified 2026-11-04. Identity and category only. Versions, licenses and maintenance status change; look them up live.

| term | aliases | what it is | not to confuse with | official URL |
|---|---|---|---|---|
| Kubernetes | K8s | Container orchestration system | Docker, Docker Swarm | https://kubernetes.io/ |
| k3s | - | Lightweight Kubernetes distribution | RKE2, k3d | https://k3s.io/ |
| RKE2 | RKE Government | Kubernetes distribution from SUSE Rancher with a security focus | RKE1, Rancher (the management UI) | https://docs.rke2.io/ |
| Helm | Helm chart | Package manager for Kubernetes | Helmfile | https://helm.sh/ |
| Argo CD | ArgoCD | GitOps controller that syncs Kubernetes from Git | Argo Workflows | https://argo-cd.readthedocs.io/ |
| Flux | FluxCD | GitOps toolkit for Kubernetes | Argo CD | https://fluxcd.io/ |
| Terraform | tf | Infrastructure as code tool from HashiCorp | OpenTofu (fork), Ansible | https://developer.hashicorp.com/terraform |
| OpenTofu | tofu | Community-governed fork of Terraform, stewarded by the Linux Foundation | Terraform | https://opentofu.org/ |
| Ansible | - | Agentless configuration management and automation | Terraform | https://docs.ansible.com/ |
| Docker | Docker Engine | Container runtime and tooling | Docker Desktop, Kubernetes | https://docs.docker.com/ |
| Docker Compose | compose | Tool to define and run multi-container apps from a YAML file | Docker Swarm | https://docs.docker.com/compose/ |
| Caddy | Caddyfile | Web server and reverse proxy with automatic HTTPS | Traefik, nginx | https://caddyserver.com/ |
| Traefik | - | Reverse proxy and ingress controller with dynamic configuration | Caddy | https://traefik.io/traefik |
| nginx | - | Web server and reverse proxy | NGINX Ingress Controller | https://nginx.org/ |
| PostgreSQL | Postgres, PG, Psql | Relational database | psql (the client) | https://www.postgresql.org/ |
| PgBouncer | - | Connection pooler for PostgreSQL | Pgpool-II | https://www.pgbouncer.org/ |
| ClickHouse | CH | Column-oriented database for analytics | Clickhouse Cloud (the managed service) | https://clickhouse.com/docs |
| Redis | - | In-memory data store used as cache, queue and session store | Valkey (fork) | https://redis.io/docs/ |
| Valkey | - | BSD-licensed key-value store derived from Redis code, backed by the Linux Foundation | Redis | https://valkey.io/ |
| Kafka | Apache Kafka | Distributed event streaming platform | Redpanda (compatible) | https://kafka.apache.org/ |
| Redpanda | - | Kafka-API-compatible streaming platform | Kafka itself | https://www.redpanda.com/ |
| NATS | NATS JetStream | Lightweight messaging system; JetStream adds persistence | Kafka | https://nats.io/ |
| MinIO | - | S3-compatible self-hosted object storage; the community edition went to maintenance mode in late 2025, check its status live before choosing it | AWS S3, MinIO AIStor (commercial) | https://min.io/ |
| Garage | - | Lightweight S3-compatible distributed object storage from Deuxfleurs | MinIO | https://garagehq.deuxfleurs.fr/ |
| Ceph | Rook-Ceph | Distributed storage for block, file and object | Rook (the Kubernetes operator) | https://ceph.io/ |
| restic | - | Encrypted deduplicating backup tool | BorgBackup | https://restic.net/ |
| BorgBackup | Borg | Deduplicating backup tool | restic | https://www.borgbackup.org/ |
| Prometheus | - | Metrics monitoring and alerting system | Grafana | https://prometheus.io/ |
| Grafana | - | Dashboards and visualisation for metrics, logs and traces | Prometheus | https://grafana.com/ |
| Loki | Grafana Loki | Log aggregation system from Grafana Labs | Elasticsearch, Logstash | https://grafana.com/oss/loki/ |
| OpenTelemetry | OTel, OTLP | Vendor-neutral standard and SDKs for traces, metrics and logs | OpenTracing | https://opentelemetry.io/ |
| Sentry | - | Application error and performance monitoring | GlitchTip (compatible alternative) | https://sentry.io/ |
| GlitchTip | - | Open-source error tracking compatible with Sentry SDKs | Sentry | https://glitchtip.com/ |
| Uptime Kuma | - | Self-hosted status and uptime monitor | Uptime monitoring SaaS | https://github.com/louislam/uptime-kuma |
| Tailscale | - | Mesh VPN built on WireGuard with a managed control plane | Headscale, NetBird | https://tailscale.com/ |
| Headscale | - | Self-hosted open-source replacement for the Tailscale control server | Tailscale | https://headscale.net/ |
| WireGuard | WG | VPN protocol and kernel module | Tailscale, OpenVPN | https://www.wireguard.com/ |
| NetBird | - | Open-source mesh VPN and zero trust network platform from Germany | Tailscale | https://netbird.io/ |
| OpenBao | - | Open-source secrets manager forked from Vault, under the Linux Foundation (OpenSSF) | HashiCorp Vault | https://openbao.org/ |
| Vault | HashiCorp Vault | Secrets management service from HashiCorp | Vaultwarden, OpenBao | https://developer.hashicorp.com/vault |
| Vaultwarden | - | Lightweight self-hosted server compatible with Bitwarden clients | HashiCorp Vault | https://github.com/dani-garcia/vaultwarden |
| Keycloak | - | Open-source identity and access management with OIDC and SAML | an LDAP directory | https://www.keycloak.org/ |
| GitHub Actions | GHA, Actions | CI and automation on GitHub | GitHub Apps | https://docs.github.com/actions |
| Forgejo | - | Self-hosted software forge run by the non-profit Codeberg e.V. | Gitea, Codeberg (the hosted instance) | https://forgejo.org/ |
