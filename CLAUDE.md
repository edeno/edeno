# Project notes

Personal academic website at https://www.edenovellis.com — Sphinx + MyST built into a static site, deployed to GitHub Pages by `.github/workflows/deploy.yml`.

## Local dev with uv

Dependencies live in `pyproject.toml` and are pinned in `uv.lock`; the Python version is in `.python-version`. Setup (rerun after pulling changes to the lock):

```bash
uv sync
```

Use `uv sync` / `uv run` / `uv add`, not `uv pip`: the project commands always target `.venv`, while `uv pip` targets whatever `VIRTUAL_ENV` points at (which may be conda base). To bump dependencies: `uv lock --upgrade`.

Build the site:

```bash
uv run sphinx-build -nW --keep-going -b dirhtml . _build/dirhtml
open _build/dirhtml/index.html
```

Live-reload while editing:

```bash
uv run sphinx-autobuild -b dirhtml . _build/dirhtml \
  --ignore "_build/*" --ignore "**/.ipynb_checkpoints"
```

The `execute` dependency group (`uv sync --group execute`) only matters if a page actually executes a notebook — CI installs it, but there are no `.ipynb` pages yet.

## Generated files

- `_static/publications.txt` — produced by `scripts/orcid-publications.py` from the ORCID API. Not committed; regenerated on each CI build. To regenerate locally: `uv run python scripts/orcid-publications.py`.
- `_build/` — Sphinx output; gitignored.

## Conventions

- Markdown is MyST-flavored (`conf.py:myst_enable_extensions`).
- Python is formatted with `uvx ruff format` (no project config; defaults).
- Comments in Python and markdown should be sparing — only when the *why* is non-obvious.

## Theme

The site uses [Furo](https://pradyunsg.me/furo/). Two things to know:

- Brand colour is currently a placeholder (`#2563eb` light / `#60a5fa` dark, `conf.py: html_theme_options.light_css_variables`); pick something distinctive at leisure.
- Furo doesn't accept Pydata-style theme options. Google Analytics, JSON-LD Person schema, and any other `<head>` content is injected via the `_inject_head` html-page-context hook in `conf.py` (theme-agnostic). Social icons live in Furo's `footer_icons` slot as inline Bootstrap Icons SVGs.
