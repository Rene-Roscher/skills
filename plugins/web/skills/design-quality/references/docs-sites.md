# Docs and help sites

Docs pages are product surfaces. They get the same audit as an app screen, and some failures only exist here:
content that silently stops rendering, screenshots that leak data, and navigation that grew one page at a time.

## Navigation

- Group sections the way readers look for them, about four groups of related sections (getting started,
  monitoring the thing, communicating, account and billing), and use the same grouping in the section switcher,
  the sidebar and the home page. One source of truth for the groups.
- Sidebar titles are short because the group gives the context: "Heartbeat", not "Heartbeat checks (push
  monitoring)". No parentheses in titles; the page's H1 may be longer and still has none.
- Use the product's own names and icons for the same things. A check type, a plan or a role shows the icon the
  app shows for it; take it from the app's code, not from a look-alike.
- Icons only where they tell items apart (types, vendors, SDKs). Plain topic pages stay without one, or the
  column turns into a row of pictures.
- Third-party logos (identity providers, SDKs, languages) come from a source with a stated licence, carry an
  attribution comment in the file and a credits entry in the README. Simple Icons is CC0
  (https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md, verified 2026-11); the vendor's brand
  guide decides whether colour versions may be used.
- A guide line beside sidebar and table of contents, with the active item marked on the line, shows place and
  depth at a glance. The marker travels along the line; technique in `interface-motion`.
- The table of contents follows the scroll with an `IntersectionObserver`, not a scroll handler.

## Reading

- Prose blocks get a `max-width` that keeps lines at 45 to 80 characters, measured on rendered lines.
- Headings inherit the text colour; a heading permalink is not a coloured link.
- Long words, URLs and inline code wrap (`overflow-wrap: anywhere` on prose) so a 390 px screen never scrolls
  sideways.
- Callouts and plan badges are tinted surfaces without a border.

## Content that must render

- Block directives (MDC `::name`, MDX components, shortcodes) that are not closed swallow everything after them.
  The page still builds and shows no error. Check it in CI: a script that fails on an opening block without its
  closing line, and on escaped quotes inside directive attributes, which some parsers print as raw text.
- After every content change, compare rendered headings with the source: count `##` lines in the file and `h2`
  in the served page. A crawl over every route does this in seconds and also catches overflow at 390 px and page
  errors.
- When a dev server auto-imports components, a newly added component can produce a hydration or render error
  that a restart of the dev server removes. Confirm with a production build before hunting a bug.

## Screenshots

- Capture at device scale factor 2 from a dedicated test tenant with realistic data.
- Mask private data in the DOM before the capture (replace the text node), never by blurring afterwards. Search
  the image text and the file metadata for addresses and tenant names before committing.
- Open every captured image and look at it. A screenshot that shows a loading state, a cookie banner or the
  wrong theme is worse than none.
- Every screenshot has alt text that says what it shows, and a caption when the reader must act on it.
- A zoom view (lightbox) is centred, fits the viewport on both axes, closes on Escape, a click outside and a
  close button that never covers the image, returns focus to the thumbnail, and locks page scrolling while open.

## Moving pages

- A restructure that changes URLs ships redirects (301) for every old URL in the same change. Search engines
  and links from the app, mails and support answers point at the old addresses.

## Home page

- The search is the main element. Do not show two search fields at once (navbar and hero); hide one until the
  other scrolls out.
- Link to the pages readers want (tasks such as "create a status page"), not to the first page of each section;
  "Overview" repeated in every card says nothing.
- Measure the height on a phone. A grid of equal cards that is five screens tall on 390 px needs grouping.
