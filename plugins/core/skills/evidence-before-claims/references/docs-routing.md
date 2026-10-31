# Docs routing

Load when you need a library, CLI or API fact and have to pick a tool, a library ID or a fallback.

## Find the tools by capability

- Tool names depend on the machine. An MCP server added by the user shows up under its own key (for example
  `mcp__context7__query-docs`); one shipped in a plugin shows up as `mcp__plugin_[plugin]_[server]__[tool]`.
- Some tools are deferred behind a tool search. Search for the capability ("docs", "context7", "fetch",
  "crawl", "firecrawl") before you conclude that a tool is missing.
- Write down which tools you found and which you used. Never claim a tool you did not call.

## Fallback chain

1. A docs index. With Context7: call `resolve-library-id` with the library name and the question, pick the
   result by exact name, source reputation and snippet count, then call `query-docs` with that ID and one
   concept per query. At most three calls per question.
2. The official documentation page through the built-in web fetch tool.
3. A crawler or search tool, if one is configured. It costs credits, so prefer the built-in fetch for a single
   static page.
4. The installed source of the dependency.
5. Nothing produced evidence: answer "unverified" with the check that would settle it.

Some frameworks ship their own docs tool that knows which packages are installed. Treat it as a docs index.

## Versions in a docs index

- `resolve-library-id` lists the versions it has per library. `query-docs` accepts an ID with a version
  suffix in the form `/org/project/version`, using a version string from that list (tool schema, read
  2026-10-31).
- The Context7 README documents a second way: name the version in the prompt and let the tool match it.
- If the version-pinned ID returns nothing, try the unversioned ID or another ID for the same project before
  you fall back. An empty result is not an answer.
- Say which docs version you used when it differs from the installed one.

## Web fetch caveats

- The page goes through an extraction prompt, so the result only contains what the prompt asked for. "The
  page does not mention X" may mean the prompt did not ask. Fetch again with a narrower prompt, or read the raw
  page with a shell download if shell access is allowed.
- One call reads up to 100,000 characters. A longer page needs a follow-up call from the reported offset.
- Fetches outside the preapproved documentation domains ask for permission per domain in the default
  permission modes.

Source: https://code.claude.com/docs/en/tools-reference (verified 2026-10).

## Crawler tools by capability

Firecrawl as the example. It needs `FIRECRAWL_API_KEY`, or `FIRECRAWL_API_URL` for a self-hosted instance.

| Need | Tool |
|---|---|
| Content of one known URL | `firecrawl_scrape` |
| Which URLs a site has | `firecrawl_map` |
| Ranked results for a question | `firecrawl_search` |
| Content of many pages under one site | `firecrawl_crawl` |
| A click or typed input before the page can be read | `firecrawl_interact` |
| Credits left | `firecrawl_credit_usage` |

Source: https://github.com/firecrawl/firecrawl-mcp-server (README, verified 2026-10).

## Installed source per ecosystem

| Ecosystem | Where the installed code is |
|---|---|
| PHP (Composer) | `vendor/[vendor]/[package]` |
| Node (npm, Yarn) | `node_modules/[package]`; with pnpm the real files sit under `node_modules/.pnpm/` |
| Go | the module cache printed by `go env GOMODCACHE`, then `[module]@[version]` |
| Python | `pip show -f [package]` or `uv pip show [package]` prints the location |
| Rust | `cargo metadata --format-version 1` lists each package's `manifest_path` |

Cite what you read as `path:line`.

## CLI flags

The installed binary is the primary source: `[tool] --help`, `[tool] [command] -h`, or the man page. Run it
before you explain a flag, and quote the line that lists it. An unknown option error is evidence that the
installed version does not accept it.
