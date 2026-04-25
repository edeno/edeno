import os

# -- Project information -----------------------------------------------------

project = "Eric L. Denovellis"
copyright = "2026, Eric L. Denovellis"
author = "Eric L. Denovellis"

extensions = [
    "myst_nb",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_examples",
    "sphinxext.opengraph",
    "sphinxext.rediraffe",
    "sphinx_sitemap",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**/pandoc_ipynb/inputs/*",
    ".nox/*",
    ".venv/*",
    "README.md",
    "CLAUDE.md",
    "**/.ipynb_checkpoints/*",
]


# -- HTML output -------------------------------------------------

html_theme = "furo"

# Furo theme options. Note: Pydata's `analytics` and `icon_links` keys
# don't exist in Furo. Google Analytics needs to be re-injected via the
# layout.html extrahead block if this prototype is adopted; social links
# can be added via Furo's `footer_icons` (requires inline SVG markup).
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#2563eb",
        "color-brand-content": "#2563eb",
    },
    "dark_css_variables": {
        "color-brand-primary": "#60a5fa",
        "color-brand-content": "#60a5fa",
    },
}

html_favicon = "_static/favicon.ico"
html_title = "Eric L. Denovellis"
html_static_path = ["_static"]
html_logo = "_static/profile.jpg"
html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "hello.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

# OpenGraph + Twitter Card config
ogp_site_url = "https://www.edenovellis.com"
ogp_image = "https://www.edenovellis.com/_static/profile.jpg"
ogp_type = "profile"
ogp_site_name = "Eric L. Denovellis"
ogp_description_length = 200
ogp_custom_meta_tags = [
    '<meta property="profile:first_name" content="Eric">',
    '<meta property="profile:last_name" content="Denovellis">',
    '<meta name="twitter:card" content="summary">',
    '<meta name="twitter:title" content="Eric L. Denovellis">',
    '<meta name="twitter:image" content="https://www.edenovellis.com/_static/profile.jpg">',
    '<meta name="twitter:image:alt" content="Photo of Eric L. Denovellis">',
]


# -- MyST and MyST-NB ---------------------------------------------------

# MyST
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]

# MyST-NB
nb_execution_mode = "cache"


def setup(app):
    app.add_css_file("custom.css")


# Sitemap
html_baseurl = "https://www.edenovellis.com"
sitemap_locales = [None]
sitemap_url_scheme = "{link}"
