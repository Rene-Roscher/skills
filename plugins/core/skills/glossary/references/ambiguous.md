# Ambiguous terms

verified 2026-11-04. Each term below has more than one plausible meaning in a German or EU software business. Do not pick one from the sentence alone: check the project (dependencies, config keys, environment variable names, docs), or ask with the candidates listed. Not a `term | aliases` table, so `check_glossary.py` skips it.

| ambiguous term | candidates | where to look |
|---|---|---|
| analytics | Plausible, Matomo, Umami, etracker, GA4, Google Search Console, an in-house events table, ClickHouse-style product analytics | package.json or composer.json, script tags in layouts, `.env` keys, CSP allow-lists |
| R2 | Cloudflare R2 object storage; a second environment or region named R2 | filesystem or storage config, S3 endpoint URLs ending in r2.cloudflarestorage.com |
| S3 | AWS S3 itself; any S3-compatible store (R2, B2, MinIO, Garage, Hetzner Object Storage); the S3 API only | endpoint and region settings in the storage config |
| panel | Pterodactyl or Pelican panel; Plesk, cPanel, KeyHelp; a customer-facing console; an admin panel of the app | deploy docs, server inventory, route and package names |
| ptero | Pterodactyl panel, Wings daemon on a node, a Pterodactyl API key | environment keys, node hostnames in the inventory |
| Lexware | Lexware Office (cloud, formerly lexoffice); installed Lexware products; the Haufe brand | API client or webhook code, accounting export docs |
| DPA | AVV (data processing agreement); a data protection authority; Digital Platform Agreement in other contexts | surrounding legal text, who the counterparty is |
| OSS | One-Stop-Shop for EU VAT; open-source software | tax or billing context versus license context |
| Gutschrift | credit note on an invoice; a voucher; a plain credit to an account | accounting export, invoice templates |
| Sentry | Sentry SaaS; GlitchTip or another Sentry-compatible endpoint | DSN host in config |
| Vault | HashiCorp Vault; OpenBao; Vaultwarden; a generic secret store | secret-management docs, CI variables |
| Pages | Cloudflare Pages; GitHub Pages; a CMS pages table | deploy config, workflow files |
| Workers | Cloudflare Workers; queue workers; Go probe workers; Web Workers | `wrangler` config versus queue or process config |
| Robot | Hetzner Robot (dedicated servers); Robot Framework; an automation bot | hosting inventory, provider names |
| DSA | EU Digital Services Act; the Digital Signature Algorithm | legal versus cryptography context |
| TOM | technische und organisatorische Maßnahmen under the DSGVO; a person | privacy or security documentation |
| SES | AWS Simple Email Service; another provider with a similar service name | mailer config, SMTP host |
| CDN | Cloudflare, Bunny.net, or another edge in front of the app | DNS records, response headers |
