"""Build the site once and check the rendered HTML."""

import importlib.util
import json
import re
import shutil
from html import unescape
from pathlib import Path
from urllib.parse import unquote

import pytest
from sphinx.cmd.build import build_main

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("conf", REPO / "conf.py")
conf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(conf)

# Every page Sphinx builds besides the home page, so new pages are checked too.
PAGES = sorted(
    p.stem
    for p in REPO.glob("*.md")
    if p.name not in conf.exclude_patterns and p.stem != "index"
)


# Author lists for two of the home page's selected papers, in the ORCID script's
# format; other listed papers have none, as when a DOI is missing from the file.
PUBLICATION_AUTHORS = {
    "10.7554/elife.108089": [
        {"name": "Kyu Hyun Lee"},
        {"self": True},
        {"name": "Loren M. Frank", "orcid": "https://orcid.org/0000-0000-0000-0001"},
    ],
    "10.7554/elife.64505": [
        {"self": True},
        {"name": "A Consortium", "organization": True},
    ],
}


def copy_site(dest: Path) -> Path:
    # Dot-directories hold git, environments and tool state, never site files.
    shutil.copytree(
        REPO, dest, ignore=shutil.ignore_patterns(".*", "_build", "__pycache__")
    )
    # CI runs pytest before fetching publications from ORCID.
    publications = dest / "_static" / "publications.txt"
    if not publications.exists():
        publications.write_text(
            "### 2026\n:::{container} pub\n**A placeholder paper**\n\n"
            "**Denovellis, E.L.**\n\n*A Journal*.\n:::\n"
        )
    (dest / "_static" / "publication-authors.json").write_text(
        json.dumps(PUBLICATION_AUTHORS)
    )
    return dest


def build_site(src: Path, out: Path) -> int:
    return build_main(["-b", "dirhtml", "-q", str(src), str(out)])


DANGLING_REF = "a-label-that-does-not-exist"


@pytest.fixture(scope="session")
def built_site(tmp_path_factory) -> Path:
    src = copy_site(tmp_path_factory.mktemp("src") / "site")
    # Deploys publish despite warnings (only PR builds are strict), and CI runs
    # these tests before every deploy, so the build must tolerate one.
    with (src / "talks.md").open("a") as f:
        f.write(f"\nSee {{ref}}`{DANGLING_REF}`.\n")
    out = tmp_path_factory.mktemp("out")
    assert build_site(src, out) == 0
    return out


@pytest.fixture(scope="session")
def css(built_site) -> str:
    return (built_site / "_static" / "academic.css").read_text()


def test_page_warnings_do_not_fail_the_build(built_site):
    assert DANGLING_REF in read_page(built_site, "talks")


def read_page(built_site: Path, page: str) -> str:
    if page == "404":
        return (built_site / "404.html").read_text()
    return (built_site / page / "index.html").read_text()


def nav(html: str) -> str:
    return re.search(r'<nav class="site-nav".*?</nav>', html, re.DOTALL).group(0)


def container(html: str, cls: str) -> str:
    """Inner HTML of the first MyST ``{container}`` with this class."""
    match = re.search(
        rf'<div class="{cls} docutils container">(.*?)</div>', html, re.DOTALL
    )
    assert match, f"no {cls} container"
    return match.group(1)


def toctree_entries(markdown: str) -> list[str]:
    block = re.search(r"```\{toctree\}\n(.*?)```", markdown, re.DOTALL).group(1)
    return [
        line.strip()
        for line in block.splitlines()
        if line.strip() and not line.startswith(":")
    ]


def test_top_nav_follows_the_toctree(built_site):
    toctree = toctree_entries((REPO / "index.md").read_text())
    assert toctree
    home = read_page(built_site, "")
    assert re.findall(r'href="([^"]*)"', nav(home)) == [f"{doc}/" for doc in toctree]
    talks = read_page(built_site, "talks")
    assert re.search(r'<a class="site-name" href="\.\./"', talks)


def test_no_search(built_site):
    for page in ["", *PAGES]:
        assert 'type="search"' not in read_page(built_site, page)
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
    footer = re.search(r"<footer.*?</footer>", html, re.DOTALL).group(0)
    for name, url, _ in conf.SOCIAL_LINKS:
        assert f'href="{url}"' in footer
        assert f'aria-label="{name}"' in footer
    assert "Sphinx" not in footer
    copyright_text = re.search(
        r'<div class="copyright">(.*?)</div>', footer, re.DOTALL
    ).group(1)
    assert re.fullmatch(rf"© \d{{4}} {conf.author}", unescape(copyright_text).strip())


def test_404_page(built_site):
    html = read_page(built_site, "404")
    assert '<a class="site-name" href="/"' in html
    assert 'href="/_static/' in html


def test_home_intro_and_plain_links(built_site):
    html = read_page(built_site, "")
    # Everything between the name and the first subsection is the intro.
    intro = re.search(r"<h1>Eric L\. Denovellis.*?<section", html, re.DOTALL).group(0)
    assert re.search(r'<img[^>]*class="portrait', intro)
    assert "profile.jpg" in intro
    assert 'class="tagline' in intro
    links = re.search(r'<p class="links">(.*?)</p>', html, re.DOTALL).group(1)
    assert re.findall(r"<a [^>]*>[^<]+</a>", links)


def test_projects_grouped_by_theme(built_site):
    html = read_page(built_site, "projects")
    groups = re.findall(r"<section id=[^>]*>\s*<h2>.*?</section>", html, re.DOTALL)
    assert groups
    for group in groups:
        assert 'class="project-list' in group
        assert re.search(r'<strong><a class="reference external" href="[^"]+">', group)


def test_contact_address_keeps_its_lines(built_site):
    html = read_page(built_site, "contact")
    assert "<br" in html  # the address keeps its line breaks


def test_titles_not_doubled(built_site):
    assert f"<title>{conf.project}</title>" in read_page(built_site, "")
    for page in PAGES:
        title = re.search(r"<title>(.*?)</title>", read_page(built_site, page)).group(1)
        assert title.count(conf.project) == 1, title


def test_charter_ships_with_the_site(built_site, css):
    # Charter is only preinstalled on Apple devices; everyone else downloads it.
    static = built_site / "_static"
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


def test_orcid_icon_cuts_out_its_letters(built_site):
    # One path draws the disc and the "iD" inside it; nonzero fill paints it solid.
    footer = read_page(built_site, "contact").split('class="site-footer"')[1]
    orcid = re.search(r'aria-label="ORCID".*?</svg>', footer, re.DOTALL).group(0)
    assert 'fill-rule="evenodd"' in orcid


def test_publications_lead_with_the_title(built_site):
    html = read_page(built_site, "publications")
    entries = re.findall(
        r'<div class="pub docutils container">(.*?)</div>', html, re.DOTALL
    )
    assert entries
    for entry in entries:
        paragraphs = re.findall(r"<p>(.*?)</p>", entry, re.DOTALL)
        assert len(paragraphs) >= 2, entry[:200]  # title, authors, usually venue
        title = paragraphs[0]
        assert title.startswith("<strong>") and title.endswith("</strong>")


@pytest.mark.parametrize("page", ["talks", "teaching", ""])  # "" is home Education
def test_dated_entries_have_a_date_and_details(built_site, page):
    block = container(read_page(built_site, page), "dated")
    dates = re.findall(r"<dt>(.*?)</dt>", block)
    assert dates and all(d.strip() for d in dates)
    for dd in re.findall(r"<dd>(.*?)</dd>", block, re.DOTALL):
        assert len(re.findall(r"<p>", dd)) >= 2, dd[:200]  # title, then details


def test_fun_photo_grid(built_site):
    images = re.findall(
        r"<img [^>]*>", container(read_page(built_site, "fun"), "photos")
    )
    assert images
    assert all(re.search(r'alt="[^"]+"', img) for img in images)


def test_music_links_name_each_source(built_site):
    block = container(read_page(built_site, "fun"), "music-links")
    items = re.findall(r"<li>(.*?)</li>", block, re.DOTALL)
    assert items
    for item in items:
        assert re.search(r'<a class="reference external" href="[^"]+">\w', item)
        # A logo, if any, is decorative: the named link carries the meaning.
        for img in re.findall(r"<img [^>]*>", item):
            assert 'alt=""' in img


def test_portrait_loads_eagerly(built_site):
    # The portrait is the first thing on the home page; lazy loading delays it.
    portrait = re.search(r'<img[^>]*class="portrait"[^>]*>', read_page(built_site, ""))
    assert 'loading="lazy"' not in portrait.group(0)


@pytest.mark.parametrize("page", ["", *PAGES])
def test_nav_marks_the_current_page(built_site, page):
    html = read_page(built_site, page)
    current = re.findall(r'<a [^>]*aria-current="page"[^>]*>([^<]+)</a>', nav(html))
    assert current == ([] if page == "" else [re.search(r"<h1>([^<]+)", html).group(1)])


def test_home_lists_selected_papers(built_site):
    html = read_page(built_site, "")
    section = re.search(
        r'<section id="selected-papers">(.*?)</section>', html, re.DOTALL
    )
    entries = re.findall(r'<div class="pub docutils container">', section.group(1))
    assert entries
    assert 'href="publications/"' in section.group(1)


@pytest.mark.parametrize("page", ["", *PAGES])
def test_page_has_a_written_description(built_site, page):
    # Link previews use these; without front matter they fall back to the first text.
    html = read_page(built_site, page)
    description = re.search(r'<meta name="description" content="([^"]*)"', html)
    og = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    assert description and og and description.group(1) == og.group(1)
    assert not description.group(1).startswith("Photo of")  # not the portrait alt


def test_publication_years_sit_under_a_section(built_site):
    html = read_page(built_site, "publications")
    assert re.findall(r"<h2>([^<]+)<a", html) == ["Articles and preprints"]
    years = re.findall(r"<h3>([^<]+)<a", html)
    assert years and all(re.fullmatch(r"\d{4}", y) for y in years)


def test_contact_leads_with_email_and_lists_every_profile(built_site):
    html = read_page(built_site, "contact")
    page = re.search(r'<main class="page">(.*?)</main>', html, re.DOTALL).group(1)
    # Sphinx cloaks addresses with entities, %40 and <span>s; read it as a browser would.
    readable = unquote(unescape(re.sub(r"</?span>", "", page)))
    assert re.search(r'href="mailto:([^"]+)">\1</a>', readable)  # address written out
    for _, url, _ in conf.SOCIAL_LINKS:
        assert f'href="{url}"' in readable, url  # same profiles as the footer
    assert 'rel="me"' in page  # keeps Mastodon's profile verification
    assert ">Github<" not in page


def structured_data(html: str) -> list[dict]:
    """The nodes of the page's JSON-LD graph."""
    script = re.search(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    )
    data = json.loads(script.group(1))
    assert data["@context"] == "https://schema.org"
    return data["@graph"]


def nodes_of_type(html: str, schema_type: str) -> list[dict]:
    return [n for n in structured_data(html) if n["@type"] == schema_type]


@pytest.mark.parametrize("page", ["", *PAGES])
def test_every_page_describes_the_person(built_site, page):
    (person,) = nodes_of_type(read_page(built_site, page), "Person")
    assert person["@id"].startswith(conf.html_baseurl)
    orcid_url = dict((n, u) for n, u, _ in conf.SOCIAL_LINKS)["ORCID"]
    assert person["identifier"]["propertyID"] == "ORCID"
    assert orcid_url.endswith("/" + person["identifier"]["value"])
    assert "ucsf" in person["worksFor"]["url"]
    # Same summary as the home page's link preview.
    home = read_page(built_site, "")
    description = re.search(r'<meta name="description" content="([^"]*)"', home)
    assert person["description"] == unescape(description.group(1))


def test_home_is_a_profile_page_about_the_person(built_site):
    html = read_page(built_site, "")
    (profile,) = nodes_of_type(html, "ProfilePage")
    (person,) = nodes_of_type(html, "Person")
    assert profile["mainEntity"] == {"@id": person["@id"]}
    assert profile["url"] == conf.html_baseurl
    for page in PAGES:
        assert not nodes_of_type(read_page(built_site, page), "ProfilePage")


def test_structured_data_lists_profiles_not_email(built_site):
    (person,) = nodes_of_type(read_page(built_site, ""), "Person")
    assert person["sameAs"]
    assert not any(url.startswith("mailto:") for url in person["sameAs"])


@pytest.mark.parametrize("page", ["", *PAGES, "404"])
def test_head_has_one_viewport_and_no_unused_assets(built_site, page):
    html = read_page(built_site, page)
    assert html.count('name="viewport"') == 1
    # No search (so no highlighting scripts) and no code blocks (so no Pygments CSS).
    for unused in conf.UNUSED_ASSETS:
        assert unused not in html, unused


def test_build_ships_no_unused_sphinx_files(built_site):
    static = built_site / "_static"
    shipped = {p.name for p in static.iterdir()}
    assert not shipped & (conf.UNUSED_ASSETS | {"publications.txt"})
    assert not (built_site / "_sources").exists()


@pytest.mark.parametrize("page", ["", "publications"])
def test_listed_papers_are_articles_with_their_authors(built_site, page):
    html = read_page(built_site, page)
    (person,) = nodes_of_type(html, "Person")
    listed = {}
    for entry in re.findall(
        r'<div class="pub docutils container">(.*?)</div>', html, re.DOTALL
    ):
        doi = re.search(r'href="(https://doi\.org/[^"]+)"', entry)
        if doi:
            title = re.search(r"<p><strong>(.*?)</strong></p>", entry).group(1)
            listed[unescape(doi.group(1))] = unescape(title)
    articles = nodes_of_type(html, "ScholarlyArticle")
    assert {a["url"]: a["name"] for a in articles} == listed
    me = {"@id": person["@id"]}
    expected = {
        "10.7554/elife.108089": [
            {"@type": "Person", "name": "Kyu Hyun Lee"},
            me,
            {
                "@type": "Person",
                "name": "Loren M. Frank",
                "sameAs": "https://orcid.org/0000-0000-0000-0001",
            },
        ],
        "10.7554/elife.64505": [me, {"@type": "Organization", "name": "A Consortium"}],
    }
    for article in articles:
        doi = article["url"].removeprefix("https://doi.org/").lower()
        if doi in expected:
            assert article["author"] == expected[doi]
        else:
            # Never name the owner as the only author for want of the list.
            assert "author" not in article
    if page == "":
        with_authors = {
            a["url"].removeprefix("https://doi.org/").lower()
            for a in articles
            if "author" in a
        }
        assert with_authors == set(PUBLICATION_AUTHORS)


def test_author_lists_are_not_published(built_site):
    assert not (built_site / "_static" / "publication-authors.json").exists()
