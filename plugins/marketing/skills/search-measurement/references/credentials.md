# Credentials: least privilege and safe storage

Load this when access is missing (`measure.py` exit 3) or being set up. The owner does the steps in the vendor
consoles; the agent never asks for a key to be pasted into the chat.

## Where keys live

| Source | Environment variable | File (mode 600) |
|---|---|---|
| Search Console | `GSC_ACCESS_TOKEN` (ready token) or `GSC_SERVICE_ACCOUNT_FILE` | `~/.config/search-measurement/gsc-service-account.json` |
| Bing Webmaster | `BING_WEBMASTER_API_KEY` or `BING_WEBMASTER_API_KEY_FILE` | `~/.config/search-measurement/bing-api-key` |
| Plausible | `PLAUSIBLE_API_KEY` or `PLAUSIBLE_API_KEY_FILE`; `PLAUSIBLE_BASE_URL` for self-hosting | `~/.config/search-measurement/plausible-api-key` |

`SEARCH_MEASUREMENT_CONFIG_DIR` moves the default folder. The script refuses a file with any group or other
permission bit and a file inside a git work tree, and says how to fix it (`chmod 600`, move it). On CI, use the
runner's secret store and pass the value as an environment variable.

## Setup per source

Search Console, read-only service account:
1. In a Google Cloud project, enable the Search Console API and create a service account without project roles.
2. Create a JSON key, save it to the file above, `chmod 600` it. Google recommends keys as the exception and
   rotation for every key: https://docs.cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys
   (verified 2026-11-03).
3. A property owner adds the service-account email under Settings, Users and permissions, as Restricted user.
   Restricted has "simple view rights on most data" (https://support.google.com/webmasters/answer/7687615,
   verified 2026-11-03). Whether URL Inspection through the API works for a Restricted user is unverified; if it
   returns 403, raise that one user to Full and note it in the change log.
4. The script requests only `https://www.googleapis.com/auth/webmasters.readonly`.

Without a service account, the owner can set `GSC_ACCESS_TOKEN` to a short-lived token from their own OAuth flow
with the read-only scope. It expires within the hour; that is a feature.

Bing Webmaster:
1. The owner verifies the site in Bing Webmaster Tools, then Settings, API Access, Generate API Key. One key per
   user, valid for all of that user's verified sites (https://learn.microsoft.com/en-us/bingwebmaster/getting-access,
   verified 2026-11-03).
2. When that reach is too wide (an agency account with client sites), create a dedicated Microsoft account, add
   only this site to it, and generate the key there.
3. Save the key to the file above, `chmod 600`.

Plausible:
1. Stats API needs the Business plan on Plausible Cloud (https://plausible.io/docs/stats-api, verified
   2026-11-03). Without it, use CSV exports from the dashboard and say the loop runs on exports.
2. In the team that owns the site, create a key of type "Stats API". Keys are scoped to one team.
3. Save the key to the file above, `chmod 600`.

## When a key is exposed

A key counts as exposed when it was pasted into a chat, a ticket, a commit, a log or a shared screen.
1. Do not use it, repeat it, write it to a file or run a command with it.
2. Ask the owner to revoke it now: delete and regenerate the Bing key, delete the service-account key in IAM,
   revoke the Plausible key. Removing it from a repository alone does not help, because history keeps it.
3. The owner saves the new key to the file location above; the agent continues from there.

## Third-party connectors

A hosted or community connector that holds the Google credential sees every property the account can read. The
bundled script calls the REST API directly with the read-only scope, which keeps the credential on the owner's
machine. If the team prefers a connector, record that choice and its reach in an ADR.
