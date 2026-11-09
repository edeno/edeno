# Project notes

Personal academic website at https://www.edenovellis.com — Sphinx + MyST built into a static site, deployed to GitHub Pages by `.github/workflows/deploy.yml`.

## Local dev with uv

Dependencies live in `pyproject.toml` and are pinned in `uv.lock`; the Python version is in `.python-version`. Setup (rerun after pulling changes to the lock):

```bash
uv sync
```

Use `uv sync` / `uv run` / `uv add`, not `uv pip`: the project commands always target `.venv`, while `uv pip` targets whatever `VIRTUAL_ENV` points at (which may be conda base). To bump dependencies: `uv lock --upgrade`.

Build the site (the `Makefile` is the single entry point; CI runs the same target, strict on PRs):

```bash
uv run make dirhtml SPHINXOPTS="-nW --keep-going"
open _build/dirhtml/index.html
```

Live-reload while editing (`sphinx-autobuild` is in the `dev` group, which `uv sync` installs by default; CI sets `UV_NO_DEV=1`):

```bash
uv run make live
```

## Generated files

- `_static/publications.txt` — produced by `scripts/orcid-publications.py` from the ORCID API. Not committed; regenerated on each CI build. To regenerate locally: `uv run python scripts/orcid-publications.py`. Its offline tests run with `uv run pytest` (also in CI).
- `_build/` — Sphinx output; gitignored.

## Conventions

- Markdown is MyST-flavored (`conf.py:myst_enable_extensions`).
- Python is formatted with `uvx ruff format` (no project config; defaults).
- Comments in Python and markdown should be sparing — only when the *why* is non-obvious.

## Theme

The site uses a small local theme, `_themes/academic/`, that inherits Sphinx's `basic` theme: a top bar, a single ~650px column, and no sidebar or search. The design intent (simple, academic, no cards/badges/buttons) is in `docs/superpowers/specs/2026-11-08-site-redesign-design.md`.

- `layout.html` renders the top nav from the hidden toctree in `index.md`, so add or reorder pages there. Footer icons come from `SOCIAL_LINKS` in `conf.py`, passed through `html_context` (inline Bootstrap Icons SVGs).
- All styling lives in `static/academic.css`. Colours are CSS variables on `:root`. Dark mode follows the visitor's system setting via `prefers-color-scheme`; there is no toggle.
- Reading text is Charter. Apple devices use their installed copy; everyone else downloads the Latin-subset WOFF2 files in `static/fonts/` (Bitstream licence in `static/fonts/LICENSE.txt`, which must ship with them).
- Brand colour is teal (`#0f766e` light / `#2dd4bf` dark). Both meet WCAG AA text contrast on the page backgrounds (5.5:1 on `#ffffff`, 9.8:1 on `#121519`), so keep that bar if changing it.
- Search is turned off in `conf.py` (`_disable_search`), so no `search/` page or index is built.
- Google Analytics, JSON-LD Person schema, and any other `<head>` content is injected via the `_inject_head` html-page-context hook in `conf.py`.
- `tests/test_site_build.py` builds the site and checks the nav, head tags, footer and 404 page. It runs with `uv run pytest`.
