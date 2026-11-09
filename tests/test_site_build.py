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


def copy_site(dest: Path) -> Path:
    shutil.copytree(
        REPO,
        dest,
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
    publications = dest / "_static" / "publications.txt"
    if not publications.exists():
        publications.write_text("Publications placeholder.\n")
    return dest


def build_site(src: Path, out: Path) -> int:
    return build_main(["-b", "dirhtml", "-q", str(src), str(out)])


@pytest.fixture(scope="session")
def built_site(tmp_path_factory) -> Path:
    src = copy_site(tmp_path_factory.mktemp("src") / "site")
    out = tmp_path_factory.mktemp("out")
    assert build_site(src, out) == 0
    return out


def test_page_warnings_do_not_fail_the_build(tmp_path):
    # Deploys publish despite warnings (only PR builds are strict), and CI
    # runs these tests before every deploy, so they must not be strict either.
    src = copy_site(tmp_path / "site")
    with (src / "talks.md").open("a") as f:
        f.write("\nSee {ref}`a-label-that-does-not-exist`.\n")
    assert build_site(src, tmp_path / "out") == 0


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
    "spyglass.png",
    "replay-trajectory-classification.mp4",
]


PROJECT_GROUPS = {
    "Data infrastructure": ["Spyglass"],
    "Decoding hippocampal activity": [
        "Replay Trajectory Classification",
        "Non-Local Detector",
        "Track Linearization",
    ],
    "Signal processing": ["Spectral Connectivity", "Ripple Detection"],
    "Interactive visualization": ["RasterVis", "SpectraVis"],
}


def test_projects_grouped_by_theme(built_site):
    html = read_page(built_site, "projects")
    headings = re.findall(r"<h2>(.*?)<a class=\"headerlink", html)
    assert headings == list(PROJECT_GROUPS)
    for group, names in PROJECT_GROUPS.items():
        section = re.search(rf"<h2>{group}.*?</section>", html, re.S).group(0)
        found = re.findall(
            r'<strong><a class="reference external" href="https://github\.com/[^"]+">([^<]+)</a></strong>',
            section,
        )
        assert found == names
    for banned in ["sd-card", "sd-badge", "shields.io", "<video", "<img"]:
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


def test_home_description_starts_with_tagline(built_site):
    html = read_page(built_site, "")
    for pattern in [
        r'<meta content="([^"]*)" name="description"',
        r'<meta property="og:description" content="([^"]*)"',
    ]:
        assert (
            re.search(pattern, html)
            .group(1)
            .startswith("Computational research scientist")
        )


def test_titles_not_doubled(built_site):
    assert "<title>Eric L. Denovellis</title>" in read_page(built_site, "")
    assert re.search(
        r"<title>Talks &#8212; Eric L\. Denovellis</title>",
        read_page(built_site, "talks"),
    )


def test_charter_ships_with_the_site(built_site):
    # Charter is only preinstalled on Apple devices; everyone else downloads it.
    static = built_site / "_static"
    css = (static / "academic.css").read_text()
    faces = re.findall(r"@font-face\s*{([^}]*)}", css)
    styles = set()
    for face in faces:
        assert re.search(r'font-family:\s*"Charter"', face)
        src = re.search(r"src:([^;]*);", face).group(1)
        assert src.strip().startswith('local("Charter')
        for url in re.findall(r'url\("([^"]+)"\)', src):
            assert (static / url).is_file(), url
        weight = re.search(r"font-weight:\s*(\d+)", face).group(1)
        style = re.search(r"font-style:\s*(\w+)", face).group(1)
        styles.add((weight, style))
    assert styles == {
        ("400", "normal"),
        ("400", "italic"),
        ("700", "normal"),
        ("700", "italic"),
    }
    assert "Bitstream" in (static / "fonts" / "LICENSE.txt").read_text()


def test_coauthor_link_style_stays_on_publications(built_site):
    # Co-author names read as plain text there; an ORCID link elsewhere is a normal link.
    css = (built_site / "_static" / "academic.css").read_text()
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    selectors = re.findall(r"([^{}]*orcid\.org[^{}]*){", css)
    assert selectors
    for group in selectors:
        for selector in group.split(","):
            assert selector.strip().startswith("#publications "), selector
    assert '<section id="publications">' in read_page(built_site, "publications")
    contact = read_page(built_site, "contact")
    assert 'href="https://orcid.org/' in contact
    assert '<section id="publications">' not in contact


def test_orcid_icon_cuts_out_its_letters(built_site):
    # One path draws the disc and the "iD" inside it; nonzero fill paints it solid.
    footer = read_page(built_site, "contact").split('class="site-footer"')[1]
    orcid = re.search(r'aria-label="ORCID".*?</svg>', footer, re.S).group(0)
    assert 'fill-rule="evenodd"' in orcid


def test_publications_lead_with_the_title(built_site):
    html = read_page(built_site, "publications")
    entries = re.findall(r'<div class="pub docutils">(.*?)</div>', html, re.S)
    assert len(entries) >= 26  # the hand-written conference abstracts alone
    for entry in entries:
        paragraphs = re.findall(r"<p>(.*?)</p>", entry, re.S)
        assert len(paragraphs) == 3, entry[:200]
        title, authors, _ = paragraphs
        assert title.startswith("<strong>") and title.endswith("</strong>")
        assert "Denovellis, E.L." in authors
    css = (built_site / "_static" / "academic.css").read_text()
    assert ".pub p + p" in css
