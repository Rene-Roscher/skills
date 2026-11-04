# Terms: hosting and cloud providers

verified 2026-11-04. Identity and category only. Prices, limits, regions and product lists change; look them up live.

| term | aliases | what it is | not to confuse with | official URL |
|---|---|---|---|---|
| Cloudflare | CF | Network provider: DNS, CDN, proxy, security and a developer platform | Cloudflare R2, Workers and Pages are separate products of the same company | https://www.cloudflare.com/ |
| Cloudflare R2 | R2 | S3-compatible object storage from Cloudflare | AWS S3, Backblaze B2, any other product called R2 | https://developers.cloudflare.com/r2/ |
| Cloudflare Workers | Workers, CF Workers | Serverless code that runs on the Cloudflare network | Cloudflare Pages, browser Web Workers | https://developers.cloudflare.com/workers/ |
| Cloudflare Pages | Pages, CF Pages | Static site and frontend hosting on Cloudflare; Cloudflare documents a migration path to Workers with static assets | Workers, GitHub Pages | https://developers.cloudflare.com/pages/ |
| Cloudflare Tunnel | cloudflared, Argo Tunnel | Outbound-only connector that publishes a local service through Cloudflare without an open inbound port | Tailscale, WireGuard, a VPN | https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/ |
| AWS | Amazon Web Services | Amazon's cloud platform | Amazon retail, Amazon Pay | https://aws.amazon.com/ |
| AWS S3 | S3, Amazon S3 | Object storage from AWS; its API is also the de facto protocol other providers copy | R2, B2, MinIO, Hetzner Object Storage (S3-compatible, not S3) | https://aws.amazon.com/s3/ |
| AWS SES | SES, Amazon SES | Transactional and bulk email sending service from AWS | Amazon SNS, other mail providers | https://aws.amazon.com/ses/ |
| DigitalOcean | DO, droplet | Cloud provider with virtual servers called droplets | Hetzner Cloud, Linode | https://www.digitalocean.com/ |
| Backblaze B2 | B2 | S3-compatible object storage from Backblaze | Backblaze Computer Backup, AWS S3 | https://www.backblaze.com/cloud-storage |
| Hetzner | Hetzner Online | German hosting company with cloud, dedicated servers and storage products | one of its sub-products, see the next rows | https://www.hetzner.com/ |
| Hetzner Cloud | hcloud, HCloud, Cloud Console, Hetzner Console | Virtual servers and related resources; hcloud is also the name of the CLI | Hetzner Robot, Hetzner dedicated | https://docs.hetzner.com/cloud/ |
| Hetzner Robot | Robot | Web interface and API for dedicated servers and Storage Boxes | Cloud Console, the Robot Framework | https://docs.hetzner.com/robot/ |
| Hetzner Storage Box | Storage Box, StorageBox | Network storage reachable by SFTP, SMB, rsync and Borg | Hetzner Object Storage, Cloud Volumes | https://docs.hetzner.com/storage/storage-box/ |
| Hetzner Object Storage | Hetzner S3 | S3-compatible object storage from Hetzner | Storage Box, AWS S3 | https://docs.hetzner.com/storage/object-storage/ |
| Hetzner DNS | DNS Console, Hetzner DNS Console (old name) | Hetzner's managed DNS service; moved into the Hetzner Console and the Cloud API, the separate DNS Console and its API are being retired, so old tokens do not work with the new API | the registrar product, Cloudflare DNS | https://docs.hetzner.com/networking/dns/ |
| netcup | netcup GmbH, Root-Server, vServer | German hosting company for VPS, root servers and webhosting | netcup domain reseller account (CCP) versus server panel (SCP) | https://www.netcup.com/ |
| IONOS | 1&1 IONOS, formerly 1&1 | German hosting and domain company | IONOS Cloud (a product line), 1&1 Telecom | https://www.ionos.de/ |
| IONOS Cloud | IONOS DCD | IaaS product line of IONOS with its own data center designer | IONOS webhosting and domains | https://cloud.ionos.de/ |
| OVHcloud | OVH | French hosting and cloud company | - | https://www.ovhcloud.com/ |
| STACKIT | Schwarz Digits cloud | German cloud provider of the Schwarz Group | Schwarz Group retail brands | https://stackit.com/de |
| T Cloud Public | Open Telekom Cloud, OTC, formerly Open Telekom Cloud | Public cloud of Deutsche Telekom (run by T-Systems), OpenStack based; renamed from Open Telekom Cloud in 2026 | Telekom mobile or hosting products | https://www.t-cloud-public.com/ |
| plusserver | pluscloud open | German cloud provider | - | https://www.plusserver.com/ |
| Contabo | - | German provider of VPS and dedicated servers | Hetzner, netcup | https://contabo.com/ |
| Strato | STRATO AG | German hosting, domain and mail provider | Strato Cloud versus Strato webhosting | https://www.strato.de/ |
| Mittwald | mittwald CM | German managed hosting provider | - | https://www.mittwald.de/ |
| Infomaniak | - | Swiss hosting and cloud provider | other Swiss hosts | https://www.infomaniak.com/ |
| Exoscale | - | European cloud provider | Infomaniak | https://www.exoscale.com/ |
| Bunny.net | bunny, BunnyCDN (old name) | CDN, edge storage and DNS provider from Slovenia | Cloudflare | https://bunny.net/ |
| all-inkl | ALL-INKL.COM | German shared hosting provider | IONOS, Strato | https://all-inkl.com/ |
