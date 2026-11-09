# Site redesign: simple academic layout

> **Historical.** This records the redesign as first planned. The site changed afterwards (grouped one-line Projects, serif text, bundled Charter, dated Talks and Teaching, no videos, no sphinx-design); `CLAUDE.md` and the git log describe the current state.

## Intent

The site should look like a simple, clean, modern academic homepage. It should not look like a software product page or a documentation site. Today it reads as "technical": every project sits in a bordered card, coloured pills (Python, GPU, star counts) appear everywhere, the home page has app-style solid buttons, and Furo's documentation chrome surrounds it all (grey sidebar panel, search box, right-hand "On this page" column). Element sizing is also off. Headings are nearly as large as the name. The Spyglass logo fills a 360px image well. The three-column project grid squeezes descriptions to about four words per line.

The owner's words: they don't like "boxes separating areas" (not literally only borders: any visual compartmentalising), the sizing of elements is bad, and they prefer "simple clean websites that are modern but not too technical and flashy."

## Goals

- Replace Furo with a minimal custom layout: a top bar and a single centered column.
- Remove compartmentalising visuals site-wide: cards, shaded panels, badges/pills, solid buttons, the sidebar.
- Establish a clear type hierarchy, so the name/page title is clearly the largest thing and section headings are noticeably smaller.
- Rework the Projects page into "a few featured, then a list."

## Non-goals

- No content rewrites. Wording of bio, talks, teaching, and publications stays as-is, except where markup must change (badges/cards → plain text). Project descriptions are the one exception (see Projects page below).
- No change to the ORCID publications pipeline, its tests, CI, or deployment.
- No move away from Sphinx + MyST Markdown.

## Anti-goals (failure even if it works)

- Anything that looks flashy: animations, gradients, hero banners, big decorative imagery, drop shadows.
- Anything that looks like docs or an app: search boxes, toggles, sidebars, pill badges, button rows.
- Swapping one kind of box for another (e.g. replacing cards with heavy hairline-bordered rows on every item).

## Decided by the owner

**Frame on every page** (chosen from mockups, option "B"):

- A thin top bar: the name on the left (links to home), the six page links on the right (Projects, Publications, Talks, Teaching, Fun, Contact). One hairline separates the bar from the content. No sidebar, no right-hand table of contents.
- A single centered content column, about 650px wide.
- Section headings noticeably smaller than the name/page title.
- Teal stays the link/brand colour (`#0f766e` light / `#2dd4bf` dark; both meet WCAG AA, see `CLAUDE.md`).
- **No search.** Remove it entirely, including the search page from the build if feasible.
- **No light/dark toggle.** Dark mode follows the visitor's system setting (`prefers-color-scheme`).

**Home page** (`index.md`):

- Profile photo (circular, about 110px) beside the name (h1) and the one-line tagline ("Computational research scientist at UCSF — …").
- One row of plain text links under that: CV (PDF) · Google Scholar · GitHub · Email. These replace the four solid badge buttons.
- Then About me, Education, Collaborators as plain text.

**Projects page** (`projects.md`), chosen from mockups, option "C":

- Featured: Spyglass and Replay Trajectory Classification. Each has an image (or the existing video) capped at about 200px tall, scaled to fit without cropping, followed by name, description, and plain links.
- All other projects (Non-Local Detector, Spectral Connectivity, RasterVis, SpectraVis, Track Linearization, Ripple Detection) become a plain text list: name (linked), one or two sentences, then small plain links (Code, Paper where one exists). The list has no images or videos. The mockup the owner chose showed text only for these entries.
- **Descriptions are trimmed** to one or two sentences each (featured ones may run a little longer). The owner asked that the trimmed text be grounded in the projects themselves, not just a condensation of the current paragraphs. For each project, read its repository (README, docs, and what the code actually supports today) and its paper where there is one, and describe what it does now. Current descriptions may be out of date, for example on GPU/JAX support or features added since. The owner reviews the new copy before it ships.
- No cards, grey image wells, shaded footers, or badges. Where the mockups put a light grey behind images, follow this spec instead: no grey.

## Builder's calls (stated to the owner, not explicitly approved)

- On narrow screens the page links wrap onto a second line under the name. No hamburger menu.
- The footer keeps the social icons (`SOCIAL_LINKS` in `conf.py`) and the copyright line. It drops "Made with Sphinx and Furo."
- The long focus-areas line from the current sidebar ("Neuroscience · Probabilistic Machine Learning · …") is dropped, since the tagline covers it.
- GitHub star-count shields and language/topic tags on projects are dropped (tags could become plain grey text if they feel missed).
- RasterVis and SpectraVis keep their live **Demo** link alongside Code (these are the only projects with demos).
- Media no longer used anywhere (`RasterVis.mp4`, `SpectraVis-Demo.mp4`, `spectral_connectivity.png`, `track_linearization.png`, `ripple_detection.png` in `_static/`) are deleted, so they stop deploying.
- The featured Replay Trajectory Classification video keeps autoplay/loop/controls, still guarded by `reduced-motion.js`.
- Inline citation links inside a description (e.g. Liu et al. 2022 on Ripple Detection) stay inline as citations. "Paper" means the project's own publication.
- Body font: keep a system sans-serif stack (close to the current look; "modern").
- Stay on Sphinx. Implement the layout as a small local theme or template override (e.g. inherit from Sphinx's `basic` theme). Do not adopt another third-party theme.

## Constraints to preserve

- Everything currently injected into `<head>` must survive: Google Analytics, JSON-LD Person schema (`_inject_head` in `conf.py`, appended to `metatags`), OpenGraph tags (`sphinxext.opengraph`), sitemap (`sphinx_sitemap`), favicon.
- The 404 page (`notfound.extension` + `_move_404_to_root`). Its body text currently mentions "the search box" and must be updated.
- `reduced-motion.js` behaviour (pauses autoplaying videos when the visitor prefers reduced motion).
- Accessibility: Lighthouse a11y was 100 on all pages before this change. Keep it: contrast, 24×24px tap targets for footer icons, alt text, video controls.
- Strict build: `uv run make dirhtml SPHINXOPTS="-nW --keep-going"` must pass.
- `dirhtml` builder and root-absolute static paths (`/_static/...`) used by videos.
- Update `CLAUDE.md`'s Theme section to describe the new layout (it currently documents Furo specifics).
- Remove `furo` from dependencies and anything that existed only for Furo (`html_sidebars`, `hello.html`, `html_theme_options`, Furo-specific CSS such as `.bottom-of-page .icons`).

## Left to the builder

- Exact spacing, font sizes, line heights, and hairline colours, within the intent above.
- How the other pages (Publications, Talks, Teaching, Contact, Fun) adapt. They are already mostly plain text and should simply inherit the new type scale. The Fun page's photo grid and Spotify embed should keep working, and the grid should not look boxed.
- Whether `sphinx_design` is still needed after the projects/home rework (Fun uses `grid`). Remove it only if nothing uses it.
- Phone-width behaviour of the home intro (photo can stack above the name).
