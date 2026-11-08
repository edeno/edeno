"""Generate _static/publications.txt from ORCID for publications.md to include."""

import logging
import sys
from collections import defaultdict
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from rich.progress import track
from urllib3.util.retry import Retry

ORCID_ID = "0000-0003-4606-087X"
ORCID_RECORD_API = "https://pub.orcid.org/v3.0/"
ORCID_PROFILE = f"https://orcid.org/{ORCID_ID}"
HTTP_TIMEOUT = 15  # seconds
OUTPUT_PATH = Path(__file__).parent.parent / "_static/publications.txt"

# Preprint servers are named in Crossref's `institution` field; most are
# labelled "<server> preprint".
PREPRINT_SERVER_LABELS = {"eLife": "eLife reviewed preprint"}
# Crossref relations linking different versions (preprint, reviewed preprint,
# version of record) of the same work.
SAME_WORK_RELATIONS = (
    "is-same-as",
    "is-version-of",
    "has-version",
    "has-preprint",
    "is-preprint-of",
)

# Crossref has no equal-contribution field, so co-first authorship (as
# marked in the CV) is listed here: DOI -> number of leading co-first authors.
CO_FIRST_AUTHORS = {
    "10.7554/elife.108089.3": 2,
    "10.1016/j.neuron.2012.09.029": 3,
}

logger = logging.getLogger("orcid-publications")


def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_orcid_record(session: requests.Session, orcid_id: str) -> dict:
    response = session.get(
        ORCID_RECORD_API + orcid_id,
        headers={"Accept": "application/json"},
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def fetch_doi_metadata(session: requests.Session, doi: str) -> dict:
    response = session.get(
        f"https://doi.org/{doi}",
        headers={"accept": "application/citeproc+json"},
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def initials(given_name: str) -> str:
    """Build dotted initials, treating hyphenated parts (Jean-Pierre) separately."""
    parts = []
    for word in given_name.split():
        for sub in word.split("-"):
            if sub:
                parts.append(sub[0].upper())
    return ".".join(parts)


def format_author(author: dict) -> str:
    family = author.get("family", "")
    given = author.get("given", "")
    is_self = "denovellis" in family.lower()

    if is_self:
        display = "**Denovellis, E.L.**"
    elif given:
        display = f"{family}, {initials(given)}."
    else:
        display = family or "<unknown>"

    if "ORCID" in author:
        return f"[{display}]({author['ORCID']})"
    if is_self:
        return f"[{display}]({ORCID_PROFILE})"
    return display


def format_journal_details(meta: dict, journal: str) -> str:
    """Render `*Journal*, *vol*(issue), pages.` for an APA-style citation tail."""
    if not journal:
        return ""
    parts = [f"*{journal}*"]
    volume = meta.get("volume")
    issue = meta.get("issue")
    page = meta.get("page")
    if volume:
        parts.append(f"*{volume}*({issue})" if issue else f"*{volume}*")
    if page:
        parts.append(page)
    return ", ".join(parts) + "."


def format_reference(meta: dict, doi: str) -> dict | None:
    try:
        title = meta["title"]
        year = meta["issued"]["date-parts"][0][0]
        n_co_first = CO_FIRST_AUTHORS.get(doi.lower(), 0)
        authors = ", ".join(
            format_author(a) + ("\\*" if i < n_co_first else "")
            for i, a in enumerate(meta["author"])
        )
        journal = meta.get("container-title", "")
        if is_preprint(meta):
            servers = [i["name"] for i in meta.get("institution", []) if "name" in i]
            if servers:
                journal = PREPRINT_SERVER_LABELS.get(
                    servers[0], f"{servers[0]} preprint"
                )
        details = format_journal_details(meta, journal)
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("Skipping %s: malformed metadata (%s)", doi, exc)
        return None

    parts = [f"{authors}.", f"**{title}**."]
    if details:
        parts.append(details)
    parts.append(f"[{doi}](https://doi.org/{doi})")
    return {"year": year, "reference": " ".join(parts)}


def extract_dois(work_summary: dict) -> list[str]:
    ext_ids = (work_summary.get("external-ids") or {}).get("external-id", [])
    return [
        ext["external-id-value"]
        for ext in ext_ids
        if ext.get("external-id-type") == "doi" and ext.get("external-id-value")
    ]


def is_preprint(meta: dict) -> bool:
    return meta.get("subtype") == "preprint" or meta.get("type") == "posted-content"


def related_dois(meta: dict) -> set[str]:
    relations = meta.get("relation") or {}
    return {
        rel["id"].lower()
        for kind in SAME_WORK_RELATIONS
        for rel in relations.get(kind, [])
        if rel.get("id-type") == "doi"
    }


def select_version(session: requests.Session, group: dict) -> tuple[str, dict] | None:
    """Return the first published (non-preprint) DOI in an ORCID work group.

    Falls back to the first preprint if the group has no published version.
    """
    fallback = None
    seen: set[str] = set()
    for summary in group["work-summary"]:
        for doi in extract_dois(summary):
            if doi.lower() in seen:
                continue
            seen.add(doi.lower())
            try:
                meta = fetch_doi_metadata(session, doi)
            except requests.RequestException as exc:
                logger.warning("Skipping %s: Crossref fetch failed (%s)", doi, exc)
                continue
            if not is_preprint(meta):
                return doi, meta
            fallback = fallback or (doi, meta)
    return fallback


def drop_other_versions(works: list[tuple[str, dict]]) -> list[tuple[str, dict]]:
    """Drop works that Crossref links to another listed version of the same work.

    ORCID can split versions of one paper into separate groups (e.g., each
    eLife reviewed-preprint version gets its own DOI). Published versions
    are considered first so they win over their preprints.
    """
    kept: list[tuple[str, set[str]]] = []
    for doi, meta in sorted(works, key=lambda work: is_preprint(work[1])):
        links = related_dois(meta)
        same_as_kept = next(
            (k for k, k_links in kept if doi.lower() in k_links or k in links), None
        )
        if same_as_kept is not None:
            logger.info(
                "Skipping %s: another version (%s) is listed", doi, same_as_kept
            )
            continue
        kept.append((doi.lower(), links))
    kept_dois = {k for k, _ in kept}
    return [work for work in works if work[0].lower() in kept_dois]


def extract_title(work_summary: dict) -> str:
    return (work_summary.get("title") or {}).get("title", {}).get("value", "<unknown>")


def render_markdown(entries: list[dict]) -> str:
    by_year: dict[int, list[str]] = defaultdict(list)
    for entry in entries:
        by_year[entry["year"]].append(entry["reference"])

    lines = []
    for year in sorted(by_year, reverse=True):
        lines.append(f"## {year}")
        for ref in by_year[year]:
            lines.append(ref)
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    session = make_session()

    logger.info("Retrieving ORCID entries from API...")
    try:
        record = fetch_orcid_record(session, ORCID_ID)
    except requests.RequestException as exc:
        sys.exit(
            f"ORCID API request failed; aborting to preserve existing "
            f"{OUTPUT_PATH.name}: {exc}"
        )

    works: list[tuple[str, dict]] = []
    for group in track(
        record["activities-summary"]["works"]["group"],
        "Fetching reference data...",
    ):
        selected = select_version(session, group)
        if selected is None:
            logger.warning(
                "Skipping work without a resolvable DOI: %s",
                extract_title(group["work-summary"][0]),
            )
            continue
        works.append(selected)

    works = drop_other_versions(works)
    unmatched = CO_FIRST_AUTHORS.keys() - {doi.lower() for doi, _ in works}
    if unmatched:
        logger.warning("Co-first DOIs not in the publication list: %s", unmatched)

    entries: list[dict] = []
    for doi, meta in works:
        entry = format_reference(meta, doi)
        if entry is not None:
            entries.append(entry)

    if not entries:
        sys.exit(
            f"All DOIs failed; refusing to overwrite {OUTPUT_PATH.name} with "
            f"an empty file"
        )

    OUTPUT_PATH.write_text(render_markdown(entries))
    logger.info("Wrote %d entries to %s", len(entries), OUTPUT_PATH)


if __name__ == "__main__":
    main()
