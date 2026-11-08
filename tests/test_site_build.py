"""Build the site once and check the rendered HTML."""

import re
import shutil
import sys
from pathlib import Path

import pytest
from sphinx.cmd.build import build_main

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
import conf  # noqa: E402

NAV = ["Projects", "Publications", "Talks", "Teaching", "Fun", "Contact"]


@pytest.fixture(scope="session")
def built_site(tmp_path_factory) -> Path:
    src = tmp_path_factory.mktemp("src") / "site"
    out = tmp_path_factory.mktemp("out")
    shutil.copytree(
        REPO,
        src,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            "_build",
            ".superpowers",
            ".remember",
            "__pycache__",
            "tests",
            "docs",
        ),
    )
    # CI runs pytest before fetching publications from ORCID.
    publications = src / "_static" / "publications.txt"
    if not publications.exists():
        publications.write_text("Publications placeholder.\n")
    assert (
        build_main(["-b", "dirhtml", "-nW", "--keep-going", "-q", str(src), str(out)])
        == 0
    )
    return out


def read_page(built_site: Path, page: str) -> str:
    if page == "404":
        return (built_site / "404.html").read_text()
    return (built_site / page / "index.html").read_text()


def test_top_nav_lists_pages_in_order(built_site):
    html = read_page(built_site, "talks")
    nav = re.search(r'<nav class="site-nav".*?</nav>', html, re.S).group(0)
    assert re.findall(r"<a [^>]*>([^<]+)</a>", nav) == NAV
    assert re.search(r'<a class="site-name" href="\.\./"', html)


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
    assert conf.GA_MEASUREMENT_ID in html
    assert '<meta property="og:title"' in html
    assert 'rel="icon"' in html


def test_footer_social_links(built_site):
    html = read_page(built_site, "")
    footer = re.search(r"<footer.*?</footer>", html, re.S).group(0)
    for name, url, _ in conf.SOCIAL_LINKS:
        assert f'href="{url}"' in footer
        assert f'aria-label="{name}"' in footer
    assert "Furo" not in footer
    assert "Sphinx" not in footer


def test_404_page(built_site):
    html = read_page(built_site, "404")
    assert "search box" not in html
    assert '<a class="site-name" href="/"' in html
    assert 'href="/_static/' in html


def test_home_intro_and_plain_links(built_site):
    html = read_page(built_site, "")
    # Everything between the name and the first subsection is the intro.
    intro = re.search(r"<h1>Eric L\. Denovellis.*?<section", html, re.S).group(0)
    assert re.search(r'<img[^>]*class="portrait', intro)
    assert "profile.jpg" in intro
    assert 'class="tagline' in intro
    links = re.search(r'<p class="links">(.*?)</p>', html, re.S).group(1)
    assert re.findall(r">([^<]+)</a>", links) == [
        "CV (PDF)",
        "Google Scholar",
        "GitHub",
        "Email",
    ]
    assert "sd-badge" not in html


REMOVED_MEDIA = [
    "RasterVis.mp4",
    "SpectraVis-Demo.mp4",
    "spectral_connectivity.png",
    "track_linearization.png",
    "ripple_detection.png",
]


def test_projects_featured_then_list(built_site):
    html = read_page(built_site, "projects")
    assert len(re.findall(r'class="featured[ "]', html)) == 2
    assert len(re.findall(r'class="project[ "]', html)) == 6
    for banned in ["sd-card", "sd-badge", "shields.io"]:
        assert banned not in html


def test_unused_project_media_removed(built_site):
    for name in REMOVED_MEDIA:
        assert not (built_site / "_static" / name).exists()


@pytest.mark.parametrize(
    "page", ["", "projects", "publications", "talks", "teaching", "fun", "contact"]
)
def test_no_boxed_components(built_site, page):
    html = read_page(built_site, page)
    for banned in ["sd-card", "sd-badge", "sd-shadow", "sd-btn"]:
        assert banned not in html


def test_contact_address_keeps_its_lines(built_site):
    html = read_page(built_site, "contact")
    address = re.search(
        r"<strong>Sandler Neurosciences Center</strong>.*?</p>", html, re.S
    ).group(0)
    assert address.count("<br") == 3
