import json
import re
from pathlib import Path

# -- Project information -----------------------------------------------------

project = "Eric L. Denovellis"
author = project
copyright = f"%Y, {author}"
# Trailing slash required: sphinx-sitemap joins page links onto it.
html_baseurl = "https://www.edenovellis.com/"
PROFILE_IMAGE = "_static/profile.jpg"

extensions = [
    "myst_parser",
    "sphinxext.opengraph",
    "sphinx_sitemap",
    "notfound.extension",
]

# All pages live at the repo root; `*` doesn't cross `/`, so tool
# directories (.venv, .remember, ...) are never scanned.
include_patterns = ["*.md"]
exclude_patterns = ["README.md", "CLAUDE.md"]


# -- HTML output -------------------------------------------------

html_theme = "academic"
html_theme_path = ["_themes"]

# Bootstrap Icons SVGs (https://icons.getbootstrap.com/), inlined in the footer.
ICON_GITHUB = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" fill="currentColor"/></svg>'
ICON_LINKEDIN = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z" fill="currentColor"/></svg>'
ICON_INSTAGRAM = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.917 3.917 0 0 0-1.417.923A3.927 3.927 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.916 3.916 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.926 3.926 0 0 0-.923-1.417A3.911 3.911 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0h.003zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599.28.28.453.546.598.92.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.47 2.47 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.478 2.478 0 0 1-.92-.598 2.48 2.48 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233 0-2.136.008-2.388.046-3.231.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92.28-.28.546-.453.92-.598.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045v.002zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92zm-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217zm0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334z" fill="currentColor"/></svg>'
# Bootstrap Icons has no Google Scholar icon; this one is from Simple Icons (CC0).
ICON_GOOGLE_SCHOLAR = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z" fill="currentColor"/></svg>'
ICON_ORCID = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><path d="M256 128c0 70.7-57.3 128-128 128S0 198.7 0 128 57.3 0 128 0s128 57.3 128 128zM86.3 186.2H70.9V79.2h15.4v107zm22.6-107h41.6c39.6 0 57 28.3 57 53.5 0 27.4-21.4 53.5-56.8 53.5h-41.8v-107zm15.4 93.3h24.5c34.9 0 42.9-26.5 42.9-39.8 0-21.6-13.8-39.8-43.7-39.8h-23.7v79.6zM88.7 56.8c0 5.5-4.5 10.1-10.1 10.1s-10.1-4.6-10.1-10.1c0-5.6 4.5-10.1 10.1-10.1s10.1 4.6 10.1 10.1z" fill="currentColor" fill-rule="evenodd"/></svg>'
ICON_EMAIL = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1zm13 2.383-4.708 2.825L15 11.105zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741M1 11.105l4.708-2.897L1 5.383z" fill="currentColor"/></svg>'
ICON_BLUESKY = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M3.468 1.948C5.303 3.325 7.276 6.118 8 7.616c.725-1.498 2.698-4.29 4.532-5.668C13.855.955 16 .186 16 2.632c0 .489-.28 4.105-.444 4.692-.572 2.04-2.653 2.561-4.504 2.246 3.236.551 4.06 2.375 2.281 4.2-3.376 3.464-4.852-.87-5.23-1.98-.07-.204-.103-.3-.103-.218 0-.081-.033.014-.102.218-.379 1.11-1.855 5.444-5.231 1.98-1.778-1.825-.955-3.65 2.28-4.2-1.85.315-3.932-.205-4.503-2.246C.28 6.737 0 3.12 0 2.632 0 .186 2.145.955 3.468 1.948" fill="currentColor"/></svg>'

SOCIAL_LINKS = [
    ("Email", "mailto:eric.denovellis@ucsf.edu", ICON_EMAIL),
    ("GitHub", "https://github.com/edeno", ICON_GITHUB),
    (
        "Google Scholar",
        "https://scholar.google.com/citations?user=vuENbkoAAAAJ",
        ICON_GOOGLE_SCHOLAR,
    ),
    ("ORCID", "https://orcid.org/0000-0003-4606-087X", ICON_ORCID),
    (
        "LinkedIn",
        "https://www.linkedin.com/in/eric-denovellis-70908238/",
        ICON_LINKEDIN,
    ),
    ("Bluesky", "https://bsky.app/profile/eric-denovellis.bsky.social", ICON_BLUESKY),
    ("Instagram", "https://www.instagram.com/edenovellis/", ICON_INSTAGRAM),
]

html_context = {"social_links": SOCIAL_LINKS}

html_favicon = "_static/favicon.ico"
html_title = project
html_static_path = ["_static"]
html_extra_path = ["robots.txt"]
# Nothing links to the raw Markdown sources, so don't publish them.
html_copy_source = False
# No index entries exist, so the generated index page would be empty.
html_use_index = False

# OpenGraph; X/Twitter cards fall back to the og:* tags.
ogp_site_url = html_baseurl
ogp_image = PROFILE_IMAGE
ogp_image_alt = f"Photo of {author}"
ogp_type = "profile"
ogp_custom_meta_tags = [
    '<meta property="profile:first_name" content="Eric">',
    '<meta property="profile:last_name" content="Denovellis">',
    '<meta name="twitter:card" content="summary">',
]


# -- MyST ---------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]


# -- Per-page <head> injection (theme-agnostic) -------------------------
#
# Head content (JSON-LD, analytics) is appended to the `metatags` context
# variable, which every standard Sphinx layout renders inside <head>.

JSON_LD_PERSON = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": author,
    "givenName": "Eric",
    "familyName": "Denovellis",
    "jobTitle": "Computational Research Scientist",
    "url": html_baseurl,
    "image": html_baseurl + PROFILE_IMAGE,
    "affiliation": {
        "@type": "Organization",
        "name": "University of California, San Francisco",
        "url": "https://www.ucsf.edu/",
    },
    "alumniOf": [
        {
            "@type": "CollegeOrUniversity",
            "name": "Boston University",
            "url": "https://www.bu.edu/",
        },
        {
            "@type": "CollegeOrUniversity",
            "name": "University of California, Santa Barbara",
            "url": "https://www.ucsb.edu/",
        },
    ],
    "sameAs": [url for _, url, _ in SOCIAL_LINKS if not url.startswith("mailto:")]
    + ["https://neuromatch.social/@edeno"],
}

GA_MEASUREMENT_ID = "G-R14SV5XX1X"

_GTAG_SNIPPET = (
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>'
    "<script>"
    "window.dataLayer = window.dataLayer || [];"
    "function gtag(){dataLayer.push(arguments);}"
    'gtag("js", new Date());'
    f'gtag("config", "{GA_MEASUREMENT_ID}");'
    "</script>"
)


# Files Sphinx and the basic theme add for search, code blocks, and their own
# stylesheet; this site uses none of them.
_UNUSED_ASSETS = {
    "basic.css",
    "doctools.js",
    "documentation_options.js",
    "file.png",
    "language_data.js",
    "minus.png",
    "plus.png",
    "pygments.css",
    "searchtools.js",
    "sphinx_highlight.js",
}


def _inject_head(app, pagename, templatename, context, doctree):
    # basic/layout.html already writes a viewport tag; drop docutils' duplicate.
    head = re.sub(r'\s*<meta name="viewport"[^>]*>', "", context.get("metatags") or "")
    for key in ("script_files", "css_files"):
        context[key] = [
            f
            for f in context.get(key, [])
            if Path(str(getattr(f, "filename", f))).name not in _UNUSED_ASSETS
        ]
    head += (
        '\n<script type="application/ld+json">'
        + json.dumps(JSON_LD_PERSON)
        + "</script>"
    )
    head += "\n" + _GTAG_SNIPPET
    context["metatags"] = head


def _move_404_to_root(app, exception):
    # dirhtml writes 404/index.html, but GitHub Pages only serves /404.html.
    if exception is None and app.builder.name == "dirhtml":
        outdir = Path(app.outdir)
        (outdir / "404" / "index.html").replace(outdir / "404.html")
        (outdir / "404").rmdir()


def _remove_unused_output(app, exception):
    # publications.txt is only an include source; html_copy_source=False still
    # leaves an empty _sources/ behind.
    if exception is None:
        static = Path(app.outdir) / "_static"
        for name in _UNUSED_ASSETS | {"publications.txt"}:
            (static / name).unlink(missing_ok=True)
        sources = Path(app.outdir) / "_sources"
        if sources.is_dir() and not any(sources.iterdir()):
            sources.rmdir()


def _disable_search(app):
    # A seven-page site doesn't need search; skips search/ and searchindex.js.
    app.builder.search = False


def setup(app):
    app.connect("builder-inited", _disable_search)
    app.connect("html-page-context", _inject_head)
    app.connect("build-finished", _move_404_to_root)
    app.connect("build-finished", _remove_unused_output)


# Sitemap
sitemap_locales = [None]
sitemap_url_scheme = "{link}"
sitemap_excludes = ["404/"]

# 404 page: served by GitHub Pages for any missing URL, so asset links must be absolute.
notfound_urls_prefix = "/"
notfound_context = {
    "title": "Page not found",
    "body": "<h1>Page not found</h1>\n\n<p>Sorry, that page doesn't exist. "
    'Try the <a href="/">home page</a>.</p>',
}
