# Content crawl

A crawl over every route of a docs, help or marketing site after a content or layout change. It finds pages that
build and serve but no longer show what their source says.

## What each page is checked for

| Check | How | Fails when |
|---|---|---|
| Status | response of `page.goto` | not 200 |
| Rendered headings | count `^## ` lines in the source file (code fences removed) and `h2` elements in the page's content area | the counts differ: a block swallowed the rest of the page |
| Raw directive text | search visible text for directive syntax that should have rendered, for example a line starting with `::` or `{src=` | any hit |
| Horizontal overflow | at 390 px, `document.documentElement.scrollWidth` against `clientWidth`, and elements whose right edge passes the viewport | any overflow |
| Page errors | `pageerror` events and console errors | any |
| Broken images | `img` with `naturalWidth` 0 after load | any |

## Recipe

1. Build the route list from the content directory or the sitemap, mapping each route to its source file.
2. Open one headless browser, one page at 390 × 844, and visit routes one after another; retry `goto` up to three
   times on network errors, which are not page failures.
3. Wait for the load event and a short settle, then read all checks in one `page.evaluate`.
4. Print one line per failing page and a summary line with the page count, so a run over a hundred pages reads at
   a glance. Exit non-zero on any failure.
5. Run it against the dev server after each content batch, and once against the production URL after deploy.
