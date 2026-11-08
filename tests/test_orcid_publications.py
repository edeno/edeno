import importlib.util
from pathlib import Path

import pytest
import requests

SCRIPT = Path(__file__).parents[1] / "scripts" / "orcid-publications.py"
_spec = importlib.util.spec_from_file_location("orcid_publications", SCRIPT)
op = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(op)

SMITH_ORCID = "https://orcid.org/0000-0000-0000-0001"
SELF_LINK = f"[**Denovellis, E.L.**]({op.ORCID_PROFILE})"


def make_meta(**overrides) -> dict:
    meta = {
        "type": "journal-article",
        "title": "A title",
        "issued": {"date-parts": [[2021, 9, 27]]},
        "author": [
            {"family": "Smith", "given": "Jane", "ORCID": SMITH_ORCID},
            {"family": "Denovellis", "given": "Eric L."},
        ],
        "container-title": "eLife",
        "volume": "10",
    }
    meta.update(overrides)
    return meta


@pytest.mark.parametrize(
    ("given", "expected"),
    [("Loren M.", "L.M"), ("Jean-Pierre", "J.P"), ("Uri T", "U.T")],
)
def test_initials(given, expected):
    assert op.initials(given) == expected


@pytest.mark.parametrize(
    ("author", "expected"),
    [
        ({"family": "Smith", "given": "Jane"}, "Smith, J."),
        (
            {"family": "Smith", "given": "Jane", "ORCID": SMITH_ORCID},
            f"[Smith, J.]({SMITH_ORCID})",
        ),
        ({"family": "Denovellis", "given": "Eric"}, SELF_LINK),
        ({"family": "Plato"}, "Plato"),
    ],
)
def test_format_author(author, expected):
    assert op.format_author(author) == expected


def test_format_reference_journal_article():
    entry = op.format_reference(make_meta(issue="3", page="1-9"), "10.1/x")
    assert entry == {
        "issued": [2021, 9, 27],
        "reference": (
            f"[Smith, J.]({SMITH_ORCID}), {SELF_LINK}. **A title**. "
            "*eLife*, *10*(3), 1-9. [10.1/x](https://doi.org/10.1/x)"
        ),
    }


def test_format_reference_marks_co_first_authors(monkeypatch):
    monkeypatch.setitem(op.CO_FIRST_AUTHORS, "10.1/x", 2)
    reference = op.format_reference(make_meta(), "10.1/X")["reference"]
    assert reference.startswith(f"[Smith, J.]({SMITH_ORCID})\\*, {SELF_LINK}\\*.")


@pytest.mark.parametrize(
    ("institution", "expected_journal"),
    [
        ([{"name": "bioRxiv"}], "*bioRxiv preprint*."),
        ([{"name": "eLife"}], "*eLife reviewed preprint*."),
    ],
)
def test_format_reference_labels_preprint_server(institution, expected_journal):
    meta = make_meta(type="posted-content", institution=institution, volume=None)
    assert expected_journal in op.format_reference(meta, "10.1/x")["reference"]


def test_format_reference_skips_malformed_metadata():
    meta = make_meta()
    del meta["title"]
    assert op.format_reference(meta, "10.1/x") is None


def related(doi: str, relation: str = "has-version") -> dict:
    return {relation: [{"id-type": "doi", "id": doi}]}


def test_drop_other_versions_keeps_published_over_linked_preprint():
    preprint = ("10.1101/pre", make_meta(type="posted-content"))
    published = ("10.7554/Pub", make_meta(relation=related("10.1101/PRE")))
    unrelated = ("10.1/other", make_meta())
    works = [preprint, published, unrelated]
    assert op.drop_other_versions(works) == [published, unrelated]


def test_drop_other_versions_follows_links_from_either_side():
    preprint = (
        "10.1101/pre",
        make_meta(type="posted-content", relation=related("10.7554/pub")),
    )
    published = ("10.7554/pub", make_meta())
    assert op.drop_other_versions([preprint, published]) == [published]


def summary(*dois: str) -> dict:
    return {
        "external-ids": {
            "external-id": [
                {"external-id-type": "doi", "external-id-value": d} for d in dois
            ]
        }
    }


@pytest.fixture
def fake_fetch(monkeypatch):
    """Serve DOI metadata from a dict; a None value simulates a failed fetch."""
    responses: dict[str, dict | None] = {}
    calls: list[str] = []

    def fetch(session, doi):
        calls.append(doi)
        if responses[doi] is None:
            raise requests.ConnectionError(doi)
        return responses[doi]

    monkeypatch.setattr(op, "fetch_doi_metadata", fetch)
    return responses, calls


def test_select_version_prefers_published(fake_fetch):
    responses, _ = fake_fetch
    responses.update(pre=make_meta(type="posted-content"), pub=make_meta())
    group = {"work-summary": [summary("pre"), summary("pub")]}
    assert op.select_version(None, group) == ("pub", responses["pub"])


def test_select_version_falls_back_to_first_preprint(fake_fetch):
    responses, _ = fake_fetch
    responses.update(
        a=make_meta(type="posted-content"), b=make_meta(type="posted-content")
    )
    group = {"work-summary": [summary("a"), summary("b")]}
    assert op.select_version(None, group) == ("a", responses["a"])


def test_select_version_skips_failed_and_repeated_dois(fake_fetch):
    responses, calls = fake_fetch
    responses.update(bad=None, pub=make_meta())
    group = {"work-summary": [summary("bad", "pub"), summary("PUB")]}
    assert op.select_version(None, group) == ("pub", responses["pub"])
    assert calls == ["bad", "pub"]


def test_render_markdown_groups_by_year_newest_first():
    entries = [
        {"issued": [2019, 11], "reference": "old"},
        {"issued": [2021, 9, 27], "reference": "september"},
        {"issued": [2021, 10], "reference": "october"},
    ]
    assert op.render_markdown(entries) == (
        "## 2021\noctober\n\nseptember\n\n## 2019\nold\n"
    )


def test_format_reference_single_period_after_initials():
    meta = make_meta(author=[{"family": "Frank", "given": "Loren M."}])
    assert op.format_reference(meta, "10.1/x")["reference"].startswith(
        "Frank, L.M. **A title**."
    )


def test_format_reference_collapses_whitespace_in_title():
    meta = make_meta(title="Spectral Connectivity: a python\n  package")
    assert "**Spectral Connectivity: a python package**." in (
        op.format_reference(meta, "10.1/x")["reference"]
    )
