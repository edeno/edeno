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


def toctree_pages() -> list[str]:
    """Docs in the hidden toctree in index.md, which drives the top nav."""
    index = (REPO / "index.md").read_text()
    block = re.search(r"```\{toctree\}\n(.*?)```", index, re.S).group(1)
    return [
        line.strip()
        for line in block.splitlines()
        if line.strip() and not line.startswith(":")
    ]


PAGES = toctree_pages()


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


def test_top_nav_follows_the_toctree(built_site):
    home = read_page(built_site, "")
    nav = re.search(r'<nav class="site-nav".*?</nav>', home, re.S).group(0)
    assert re.findall(r'href="([^"]*)"', nav) == [f"{page}/" for page in PAGES]
    talks = read_page(built_site, "talks")
    assert re.search(r'<a class="site-name" href="\.\./"', talks)


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
    assert re.findall(r"<a [^>]*>[^<]+</a>", links)


def test_projects_grouped_by_theme(built_site):
    html = read_page(built_site, "projects")
    groups = re.findall(r"<section id=[^>]*>\s*<h2>.*?</section>", html, re.S)
    assert groups
    for group in groups:
        assert 'class="project-list' in group
        assert re.search(r'<strong><a class="reference external" href="[^"]+">', group)


@pytest.mark.parametrize("page", ["", *PAGES])
def test_no_boxed_components(built_site, page):
    html = read_page(built_site, page)
    for banned in ["sd-card", "sd-badge", "sd-shadow", "sd-btn"]:
        assert banned not in html


def test_contact_address_keeps_its_lines(built_site):
    html = read_page(built_site, "contact")
    assert "<br" in html  # the address keeps its line breaks


def test_home_description_is_set_not_alt_text(built_site):
    html = read_page(built_site, "")
    description = re.search(r'<meta content="([^"]*)" name="description"', html)
    og = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    assert description.group(1) and description.group(1) == og.group(1)
    assert not description.group(1).startswith("Photo of")


def test_titles_not_doubled(built_site):
    assert f"<title>{conf.project}</title>" in read_page(built_site, "")
    for page in PAGES:
        title = re.search(r"<title>(.*?)</title>", read_page(built_site, page)).group(1)
        assert title.count(conf.project) == 1, title


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
    entries = re.findall(r'<div class="pub docutils container">(.*?)</div>', html, re.S)
    assert entries
    for entry in entries:
        paragraphs = re.findall(r"<p>(.*?)</p>", entry, re.S)
        assert len(paragraphs) >= 2, entry[:200]  # title, authors, usually venue
        title = paragraphs[0]
        assert title.startswith("<strong>") and title.endswith("</strong>")
    css = (built_site / "_static" / "academic.css").read_text()
    assert ".pub p + p" in css


def test_talks_have_a_date_column(built_site):
    html = read_page(built_site, "talks")
    block = re.search(
        r'<div class="dated docutils container">(.*?)</dl>', html, re.S
    ).group(1)
    dates = re.findall(r"<dt>(.*?)</dt>", block)
    assert dates and all(d.strip() for d in dates)
    for dd in re.findall(r"<dd>(.*?)</dd>", block, re.S):
        assert len(re.findall(r"<p>", dd)) >= 2, dd[:200]  # title, then venue
    css = (built_site / "_static" / "academic.css").read_text()
    assert re.search(r"\.dated dl\s*{[^}]*grid-template-columns", css)


def test_teaching_matches_the_talks_layout(built_site):
    html = read_page(built_site, "teaching")
    block = re.search(
        r'<div class="dated docutils container">(.*?)</dl>', html, re.S
    ).group(1)
    dates = re.findall(r"<dt>(.*?)</dt>", block)
    assert dates and all(d.strip() for d in dates)
    for dd in re.findall(r"<dd>(.*?)</dd>", block, re.S):
        assert len(re.findall(r"<p>", dd)) >= 2, dd[:200]  # role, then details


@pytest.mark.parametrize("page", ["", *PAGES])
def test_no_sphinx_design_assets(built_site, page):
    html = read_page(built_site, page)
    assert "sphinx-design" not in html
    assert "design-tabs.js" not in html


def test_fun_photo_grid(built_site):
    html = read_page(built_site, "fun")
    grid = re.search(
        r'<div class="photos docutils container">(.*?)</div>', html, re.S
    ).group(1)
    images = re.findall(r"<img [^>]*>", grid)
    assert images
    assert all(re.search(r'alt="[^"]+"', img) for img in images)
    css = (built_site / "_static" / "academic.css").read_text()
    assert re.search(r"\.photos\s*{[^}]*grid-template-columns:\s*repeat\(3", css)


def test_music_links_name_each_source(built_site):
    html = read_page(built_site, "fun")
    block = re.search(
        r'<div class="music-links docutils container">(.*?)</div>', html, re.S
    ).group(1)
    items = re.findall(r"<li>(.*?)</li>", block, re.S)
    assert items
    for item in items:
        assert re.search(r'<a class="reference external" href="[^"]+">\w', item)
        # A logo, if any, is decorative: the named link carries the meaning.
        for img in re.findall(r"<img [^>]*>", item):
            assert 'alt=""' in img
