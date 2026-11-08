# Simple Academic Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Furo theme with a minimal local Sphinx theme (top bar + single centered column), and rework the home and projects pages to remove cards, badges and buttons.

**Architecture:** Add a local theme `_themes/academic/` that inherits Sphinx's `basic` theme and overrides `layout.html`. The top nav is rendered from the existing hidden toctree in `index.md` via Sphinx's `toctree()` template function, and the footer icons come from `SOCIAL_LINKS` passed through `html_context`. Search is disabled at the builder level. A pytest module builds the site into a temp directory once per session and asserts on the HTML, which guards the head injections, nav, footer, and removed components.

**Tech Stack:** Sphinx 9.2, MyST-Parser 5.1, sphinx-design 0.7 (kept only for the Fun page grid), plain CSS, pytest, uv.

**Spec:** `docs/superpowers/specs/2026-11-08-site-redesign-design.md`

## Global Constraints

- Work on a branch `site-redesign` off `main`. Don't push.
- Use `uv run` for everything (see `CLAUDE.md`; `uv pip` targets the wrong env here because `VIRTUAL_ENV` points at conda base).
- Strict build must pass: `uv run make dirhtml SPHINXOPTS="-nW --keep-going"`.
- Brand teal: `#0f766e` light / `#2dd4bf` dark. Text and links must meet WCAG AA contrast.
- Content column about 650px wide. Name/page title is clearly the largest text; section headings noticeably smaller.
- No search UI and no light/dark toggle. Dark mode comes only from `@media (prefers-color-scheme: dark)`.
- No cards, shaded panels, pill badges, solid buttons, drop shadows, gradients, or animations anywhere.
- Preserve: `_inject_head` (JSON-LD + GA `G-R14SV5XX1X`), OpenGraph, sitemap, favicon, 404 at `/404.html`, `reduced-motion.js`, root-absolute `/_static/...` video paths, 24×24px footer icon targets.
- Don't rewrite bio, talks, teaching, or publications wording. Project descriptions are rewritten (Task 3).
- Python formatted with `uvx ruff format`. Comments only where the *why* is non-obvious.
- End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Phone width (375px):** the nav wraps under the name, there's no horizontal scroll, and the home intro photo stacks above the name. Checked by the 375px screenshots in Task 5.
2. **Dark mode and transparent images:** `_static/spyglass.png` is a transparent PNG with black lettering, so it disappears on a dark background. Featured images need a light backing in dark mode only, with no grey well in light mode. Task 3 owns the CSS; checked by the dark screenshots in Task 5.
3. **Long publication entries and URLs:** they must wrap inside the 650px column (`overflow-wrap: anywhere` on body text), not overflow it. Checked on the Publications screenshot in Task 5.
4. **Reduced motion:** the featured Replay video must still be paused by `reduced-motion.js` after the markup change. Checked manually in Task 5 (Chrome DevTools → Rendering → emulate `prefers-reduced-motion: reduce`).
5. **404 page at a nested missing URL** (e.g. `/foo/bar/`): CSS and the photo must still load, because GitHub Pages serves `/404.html` for every missing path. `test_404_page` asserts root-absolute asset URLs; Task 5 loads a nested URL.

---

### Task 1: Local theme shell, search disabled, Furo removed

**Files:**

- Create: `tests/test_site_build.py`
- Create: `_themes/academic/theme.toml`
- Create: `_themes/academic/layout.html`
- Create: `_themes/academic/static/academic.css`
- Modify: `conf.py` (theme settings, lines ~29–80 and ~104–108, `setup()`, `notfound_context`)
- Modify: `pyproject.toml` (remove `furo`), then `uv lock`
- Delete: `_templates/hello.html`, `_static/custom.css`
- Modify: `CLAUDE.md` (Theme section)

**Interfaces:**

- Produces: the `built_site` pytest fixture (session-scoped, returns `pathlib.Path` to the dirhtml output) and the helper `read_page(built_site: Path, page: str) -> str` (`page=""` → `index.html`, `"projects"` → `projects/index.html`, `"404"` → `404.html`). Tasks 2–4 add tests to this file using both.
- Produces: CSS classes that later tasks use in Markdown: `.intro` (home photo + name block), `.links` (inline row of plain text links), `.featured` (featured project block), `.project` (list entry), `.project-links` (small links line under a project).

- [ ] **Step 1: Create branch**

Run: `git switch -c site-redesign`

- [ ] **Step 2: Write the build fixture and failing tests in `tests/test_site_build.py`**

The fixture copies the repo into `tmp_path_factory` with `shutil.copytree(..., ignore=shutil.ignore_patterns(".git", ".venv", "_build", ".superpowers", ".remember", "__pycache__", "tests", "docs"))`. If `_static/publications.txt` is missing in the copy (it is in CI, where pytest runs before the ORCID fetch), it writes a one-line stub. Then it runs `sphinx.cmd.build.build_main(["-b", "dirhtml", "-nW", "--keep-going", "-q", src, out])`, asserts the return code is 0, and returns `out`.

```python
NAV = ["Projects", "Publications", "Talks", "Teaching", "Fun", "Contact"]

def test_top_nav_lists_pages_in_order(built_site):
    html = read_page(built_site, "talks")
    nav = re.search(r'<nav class="site-nav".*?</nav>', html, re.S).group(0)
    assert re.findall(r"<a [^>]*>([^<]+)</a>", nav) == NAV
    assert 'class="site-name"' in html and 'href="../"' in html  # name links home

def test_no_furo_no_search(built_site):
    for page in ["", "projects", "publications"]:
        html = read_page(built_site, page)
        assert "furo" not in html.lower()
        assert 'type="search"' not in html
    assert not (built_site / "search").exists()
    assert not (built_site / "searchindex.js").exists()

def test_head_injection_survives(built_site):
    html = read_page(built_site, "")
    assert '<script type="application/ld+json">' in html
    assert "G-R14SV5XX1X" in html
    assert '<meta property="og:title"' in html
    assert 'rel="icon"' in html

def test_footer_social_links(built_site):
    html = read_page(built_site, "")
    footer = re.search(r"<footer.*?</footer>", html, re.S).group(0)
    for name, url, _ in conf.SOCIAL_LINKS:
        assert f'href="{url}"' in footer and f'aria-label="{name}"' in footer
    assert "Furo" not in footer and "Sphinx" not in footer

def test_404_page(built_site):
    html = read_page(built_site, "404")
    assert "search" not in html.lower()
    assert 'href="/_static/' in html  # root-absolute so nested missing URLs still get CSS
```

Import `conf` by putting the repo root on `sys.path` inside the test module.

- [ ] **Step 3: Run to verify they fail**

Run: `uv run pytest tests/test_site_build.py -v`
Expected: the fixture builds, and tests fail (no `site-nav`, `furo` present, `search/` exists).

- [ ] **Step 4: Create the theme**

- `theme.toml`: `[theme] inherit = "basic"`, `stylesheets = ["academic.css"]`, `sidebars = []`.
- `layout.html`: `{% extends "basic/layout.html" %}`. Empty the `relbar1`, `relbar2`, `sidebar1`, `sidebar2` blocks. Override `header` with `<header class="site-header"><a class="site-name" href="{{ pathto(root_doc) }}">{{ project }}</a><nav class="site-nav" aria-label="Main">…</nav></header>`. The nav renders `toctree(maxdepth=1, titles_only=True, includehidden=True, collapse=True)`. Restyle the resulting `<ul>` inline in CSS rather than re-templating it, so the test's `<a>` scan still works. Override `footer` with the copyright plus one `<a href aria-label>` per `social_links` entry, wrapping its inline SVG. Override `body_tag` to `<body>` and put the content inside `<main class="page">`.
- `academic.css`: CSS custom properties on `:root` (foreground, muted, hairline, background, brand `#0f766e`), redefined under `@media (prefers-color-scheme: dark)` (brand `#2dd4bf`). System sans stack. Content `max-width: 650px; margin: 0 auto`. Header bar uses `display:flex; flex-wrap:wrap; justify-content:space-between` with one hairline bottom border. Type scale: h1 about 1.75rem, h2 about 1.2rem, h3 about 1.05rem. Body line-height 1.6. `overflow-wrap: anywhere` on paragraphs and list items. Footer icons are 24×24px `inline-flex` targets. Hide `a.headerlink` until hover/focus. Define the classes listed in Interfaces. Also suppress basic.css's leftover chrome (`div.sphinxsidebar`, `div.related`, `div.bodywrapper` margins).

- [ ] **Step 5: Update `conf.py`**

- Set `html_theme = "academic"` and `html_theme_path = ["_themes"]`.
- Delete `html_theme_options`, `html_sidebars`, `html_css_files`, and the Furo comments. Add `html_context = {"social_links": SOCIAL_LINKS}`, and change the icon comment to say the SVGs are rendered by the footer.
- Add `def _disable_search(app) -> None: app.builder.search = False` and connect it to `"builder-inited"` in `setup()`. Drop `"search/"` from `sitemap_excludes`.
- Change `notfound_context["body"]` to end with `Try the <a href="/">home page</a>.</p>`.
- Reword the `_inject_head` comment so it no longer names Furo.

Then delete `_templates/hello.html` and `_static/custom.css`. Remove `templates_path` if `_templates/` is now empty. Remove `furo` from `pyproject.toml` and run `uv lock`.

- [ ] **Step 6: Run tests and strict build**

Run: `uv run pytest -v && uv run make dirhtml SPHINXOPTS="-nW --keep-going"`
Expected: all tests pass (including the existing ORCID tests) and the build reports no warnings.

- [ ] **Step 7: Update the `CLAUDE.md` Theme section**

Describe the local theme at `_themes/academic/` (inherits `basic`, top nav from the `index.md` toctree, footer icons from `SOCIAL_LINKS` via `html_context`, search disabled in `setup()`, dark mode via `prefers-color-scheme` only). Keep the teal contrast note, restated against the new backgrounds.

- [ ] **Step 8: Commit**

```bash
uvx ruff format conf.py tests/test_site_build.py
git add -A _themes conf.py pyproject.toml uv.lock tests/test_site_build.py CLAUDE.md _templates _static/custom.css
git commit -m "Replace Furo with a minimal top-bar theme"
```

---

### Task 2: Home page

**Files:**

- Modify: `index.md:1-12`
- Test: `tests/test_site_build.py`

**Interfaces:**

- Consumes: `.intro` and `.links` CSS classes and the `built_site` / `read_page` fixtures from Task 1.

- [ ] **Step 1: Write failing test**

```python
def test_home_intro_and_plain_links(built_site):
    html = read_page(built_site, "")
    intro = re.search(r'<div class="intro.*?</div>\s*</div>', html, re.S).group(0)
    assert "profile.jpg" in intro and "<h1" in intro
    links = re.search(r'<p class="links">(.*?)</p>', html, re.S).group(1)
    assert re.findall(r">([^<]+)</a>", links) == ["CV (PDF)", "Google Scholar", "GitHub", "Email"]
    assert "sd-badge" not in html
```

Adjust the regexes to whatever markup Step 3 actually produces. The assertions (photo and h1 together; exactly those four link labels in order; no badges) are the fixed part.

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_site_build.py::test_home_intro_and_plain_links -v`. Expected: FAIL.

- [ ] **Step 3: Rewrite the top of `index.md`**

- A MyST `{div} intro` containing the photo (`/_static/profile.jpg`, alt "Photo of Eric L. Denovellis", about 110px, circular via CSS), `# Eric L. Denovellis`, and the existing tagline sentence unchanged.
- A paragraph with class `links` (`{div} links` or an `{attrs}`-free raw `<p class="links">`) holding: CV (PDF) → `_static/eric_denovellis_CV.pdf`, Google Scholar → `https://scholar.google.com/citations?user=vuENbkoAAAAJ`, GitHub → `https://github.com/edeno`, Email → `mailto:eric.denovellis@ucsf.edu`.
- Remove the four `{bdg-…}` lines. The About/Education/Collaborators text stays unchanged.
- Remove the now-unused `.hero-*` rules if any came across.
- On viewports under 480px, the intro stacks with the photo above the name.

- [ ] **Step 4: Run tests and strict build**

Run: `uv run pytest -v && uv run make dirhtml SPHINXOPTS="-nW --keep-going"`. Expected: pass, no warnings.

- [ ] **Step 5: Commit**: `git commit -am "Home page: photo beside name, plain link row"` (stage any CSS changes too).

---

### Task 3: Projects page — featured + text list, rewritten descriptions

**Files:**

- Modify: `projects.md` (whole file)
- Modify: `_themes/academic/static/academic.css` (featured image rules)
- Delete: `_static/RasterVis.mp4`, `_static/SpectraVis-Demo.mp4`, `_static/spectral_connectivity.png`, `_static/track_linearization.png`, `_static/ripple_detection.png`
- Test: `tests/test_site_build.py`

**Interfaces:**

- Consumes: `.featured`, `.project`, `.project-links` from Task 1.

- [ ] **Step 1: Write failing tests**

```python
REMOVED_MEDIA = ["RasterVis.mp4", "SpectraVis-Demo.mp4", "spectral_connectivity.png",
                 "track_linearization.png", "ripple_detection.png"]

def test_projects_featured_then_list(built_site):
    html = read_page(built_site, "projects")
    assert html.count('class="featured') == 2
    assert html.count('class="project') - html.count('class="project-links') == 6
    for banned in ["sd-card", "sd-badge", "shields.io"]:
        assert banned not in html

def test_unused_project_media_removed(built_site):
    for name in REMOVED_MEDIA:
        assert not (built_site / "_static" / name).exists()
```

- [ ] **Step 2: Run to verify they fail.** Expected: FAIL.

- [ ] **Step 3: Research each project before writing copy**

For each of the 8 projects, read its README and the top level of its repo with `gh api repos/<owner>/<repo>/readme -H "Accept: application/vnd.github.raw"` and `gh repo view <owner>/<repo>`, and skim the linked paper's abstract where there is one. Note what it does *today*: backend (NumPy/JAX/GPU), main capabilities, whether it's maintained. Repos: `LorenFrankLab/spyglass`, `Eden-Kramer-Lab/replay_trajectory_classification`, `LorenFrankLab/non_local_detector`, `Eden-Kramer-Lab/spectral_connectivity`, `NeurophysVis/RasterVis`, `NeurophysVis/SpectraVis`, and the Track Linearization and Ripple Detection repos linked from the current `projects.md`. Write a scratch note (not committed) of any place where the current description is wrong or stale. Report it to the owner with the new copy.

- [ ] **Step 4: Rewrite `projects.md`**

- Keep the intro line as one plain sentence pointing to GitHub.
- `## Featured`: two `{div} featured` blocks (Spyglass, then Replay Trajectory Classification). Each has an image (`_static/spyglass.png`) or the existing `<video controls autoplay loop muted playsinline preload="metadata" aria-label=…>` with the `/_static/replay-trajectory-classification.mp4` source. Then `### [Name](repo)`, a description of no more than 3 sentences, and a `project-links` line: `Code · Paper`.
- `## More projects`: six `{div} project` blocks in the current order, each with `### [Name](repo)` (or a bold linked name, whichever the type scale makes look right), 1–2 sentences, and a `project-links` line: Code, plus Paper (its own publication only; spectral_connectivity → JOSS, Spyglass → eLife, replay → eLife) or Demo (RasterVis and SpectraVis live demos, taken from the current file).
- Inline citation links such as Liu et al. 2022 may stay inline.
- CSS: featured media `max-height: 200px; width: 100%; object-fit: contain` with no background in light mode. Under `prefers-color-scheme: dark`, give featured images and the video a white background with a little padding and a small radius, so the transparent black-text Spyglass logo stays legible.
- Delete the five media files.

- [ ] **Step 5: Run tests and strict build.** Expected: pass, no warnings.

- [ ] **Step 6: Commit**

```bash
git add projects.md _themes/academic/static/academic.css tests/test_site_build.py
git rm _static/RasterVis.mp4 _static/SpectraVis-Demo.mp4 _static/spectral_connectivity.png _static/track_linearization.png _static/ripple_detection.png
git commit -m "Projects page: two featured projects, the rest as a plain list"
```

---

### Task 4: Remaining pages

**Files:**

- Modify (only if needed after viewing): `fun.md`, `contact.md`, `publications.md`, `talks.md`, `teaching.md`, `_themes/academic/static/academic.css`
- Test: `tests/test_site_build.py`

- [ ] **Step 1: Write failing test**

```python
@pytest.mark.parametrize("page", ["", "projects", "publications", "talks", "teaching", "fun", "contact"])
def test_no_boxed_components(built_site, page):
    html = read_page(built_site, page)
    for banned in ["sd-card", "sd-badge", "sd-shadow", "sd-btn"]:
        assert banned not in html
```

This may already pass after Tasks 2–3. If so, keep it as a regression guard and note that in the commit.

- [ ] **Step 2: Build and view each page at 1400px and 375px** (screenshot commands are in Task 5). Fix only what looks boxed or mis-sized under the new type scale:
  - Fun page: the photo grid uses `sd-container`/`sd-row`. Give photos a uniform aspect ratio with `object-fit: cover` and a small gap, with no borders or shadows. The KEXP/Gorilla vs. Bear logos sit inline at a modest height (about 48px). The Spotify iframe stays.
  - Don't change any wording.
- [ ] **Step 3: Run tests and strict build.** Expected: pass, no warnings.
- [ ] **Step 4: Commit**: `git commit -am "Fit remaining pages to the new layout"`.

---

### Task 5: Visual, accessibility and motion verification

No code unless a check fails. If one does, fix it in the owning task's files and commit separately.

- [ ] **Step 1: Screenshots.** Serve `_build/dirhtml` with `python3 -m http.server 8765`. Use headless Chrome (`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --window-size=W,H --screenshot=…`) to capture every page at 1400×1800 and 375×1600, and every page again with `--force-dark-mode` (confirm it switched by checking the background colour in the screenshot). Save the images in the session scratchpad.
  - Expected: no boxes or shaded panels; the name is the largest text; at 375px there's no horizontal scroll and the nav wraps; the Spyglass logo is legible in dark mode; long publication entries wrap inside the column.
- [ ] **Step 2: Nested 404.** `http.server` can't serve a custom 404, so run `grep -oE '(href|src)="[^"]*"' _build/dirhtml/404.html`. Expected: every `_static` and page link starts with `/`.
- [ ] **Step 3: Lighthouse accessibility.** Run `PATH=/Users/edeno/.nvm/versions/node/v20.19.5/bin:$PATH npx lighthouse http://localhost:8765/<page>/ --only-categories=accessibility --quiet --chrome-flags="--headless=new" --output=json` for each page, light and dark (`--force-dark-mode` in chrome-flags).
  - Expected: score 100 on every page, as before the redesign.
- [ ] **Step 4: Reduced motion.** In Chrome DevTools (Rendering → emulate `prefers-reduced-motion: reduce`), load `/projects/`. Expected: the Replay video is paused and has controls.
- [ ] **Step 5: Hand-off.** Show the owner the 1400px light/dark screenshots of Home and Projects, and the new project copy with the stale-description notes from Task 3, before any push.
