# CI gate, allow and deny files, editor hook

## Gate

Run the scan after the production build and before the deploy step. A failing scan stops the deploy.

```bash
python3 scripts/audience_scan.py --self-test
python3 scripts/audience_scan.py [build output dir] --min-html [pages you expect] \
  --locale-keys [locale files] --deny .audience-deny --allow .audience-allow
```

- Copy the script into the project (for example `scripts/audience_scan.py`) and pin it by commit, so CI does not
  depend on a skill installation.
- Run `--self-test` in the same job. It fails when the script loses a rule, so the gate cannot go quiet.
- Set `--min-html` a little below the number of pages the build prerenders. A build that silently prerendered
  nothing then fails instead of passing with zero findings.
- Scan the output the deploy ships (the static export, or pages fetched from the built server), not the
  development server.
- After the deploy, scan the live site with `--site` and compare: a page that differs from the build points at a
  cache or a second build path.

## Allow file

One regular expression per line, matched against the finding's snippet, with a required reason:

```text
Terraform (ab Version )?1\.5  # third-party version the reader runs
*/brand* :: Acme Cloud is a platform  # bilingual boilerplate offered for download
```

`GLOB :: REGEX` limits an entry to locations that match the glob. An entry without `# reason` stops the scan.
Review the allow file in every pull request that touches it.

## Deny file

One term per line: code names, internal hostnames, module names, names of internal teams or tools. Every hit is
an error. Keep the file out of a public repository if the terms themselves are private.

## Editor hook

An agent that writes a locale or content file can be warned at write time. A hook on edits to locale and
content files that runs the source scan on the changed file and returns the findings as context gives the
warning before review. Keep it a warning: code comments and tests legitimately contain the same words.
The `guardrails` plugin of this repository ships such a hook.
