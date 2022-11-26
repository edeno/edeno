# -- Project information -----------------------------------------------------

project = "Eric L. Denovellis"
copyright = "2022, Eric L. Denovellis"
author = "Eric L. Denovellis"

extensions = [
    "myst_nb",
    "ablog",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_examples",
    "sphinxext.opengraph",
    "sphinxext.rediraffe",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**/pandoc_ipynb/inputs/*",
    ".nox/*",
    "README.md",
    "**/.ipynb_checkpoints/*"
]


# -- HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "search_bar_text": "Search this site...",
    "analytics": {"google_analytics_id": "UA-88310237-1"},
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/edeno/",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Twitter",
            "url": "https://twitter.com/eric_denovellis",
            "icon": "fa-brands fa-twitter",
        },
        {
            "name": "Instagram",
            "url": "https://www.instagram.com/edenovellis/",
            "icon": "fa-brands fa-instagram",
        },
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/in/eric-denovellis-70908238/",
            "icon": "fa-brands fa-linkedin",
        },

    ],
}

html_favicon = "_static/favicon.ico"
html_title = "Eric L. Denovellis"
html_static_path = ["_static"]
html_sidebars = {
    "index": ["hello.html"],
    "publications": ["hello.html"],
    "projects": ["hello.html"],
    "talks": ["hello.html"],
    "teaching": ["hello.html"],
}

# OpenGraph config
ogp_site_url = "https://www.edenovellis.com"
ogp_image = "https://www.edenovellis.com/_static/profile.jpg"


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
