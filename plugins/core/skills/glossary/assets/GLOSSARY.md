# Glossary

Project vocabulary for people and agents. One row per term. This file wins over the generic references of the
`glossary` skill. Keep a row to what holds for anyone on the project: identity and meaning, not prices,
limits or dates that change. Check the table with `python3 scripts/check_glossary.py docs/GLOSSARY.md` from
the skill folder.

| term | aliases | meaning in this project | not to confuse with | source |
|---|---|---|---|---|
| R2 | uploads bucket | Cloudflare R2 bucket that holds customer uploads; configured as the `uploads` disk | R2 as a release name, AWS S3 | config/filesystems.php |
| analytics | stats | Plausible, self-hosted; script tag in the main layout | Google Search Console, the events table | resources/views/layout.blade.php |
