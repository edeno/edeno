# Project notes

Personal academic website at https://www.edenovellis.com — Sphinx + MyST built into a static site, deployed to GitHub Pages by `.github/workflows/deploy.yml`.

## Local dev with uv

One-time setup:

```bash
uv venv
uv pip install -r requirements.txt
```

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

`execute-requirements.txt` only matters if a page actually executes a notebook — install it if you start adding `.ipynb` content.

## Generated files

- `_static/publications.txt` — produced by `scripts/orcid-publications.py` from the ORCID API. Not committed; regenerated on each CI build. To regenerate locally: `uv run python scripts/orcid-publications.py`.
- `_build/` — Sphinx output; gitignored.

## Conventions

- Markdown is MyST-flavored (`conf.py:myst_enable_extensions`).
- Python is formatted with `uvx ruff format` (no project config; defaults).
- Comments in Python and markdown should be sparing — only when the *why* is non-obvious.

## Active branches

- `main` — production
- `prototype/furo-theme` — experimental theme migration (not merged); see commit `990c340` for caveats (GA disabled, social icons dropped, brand colour is a placeholder)
