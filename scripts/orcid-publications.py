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
HTTP_TIMEOUT = 15  # seconds
OUTPUT_PATH = Path(__file__).parent.parent / "_static/publications.txt"

PREPRINT_JOURNAL_LABELS = {
    "Cold Spring Harbor Laboratory": "bioRxiv preprint",
    "eLife Sciences Publications, Ltd": "eLife reviewed preprint",
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
    url = requests.utils.requote_uri(ORCID_RECORD_API + orcid_id)
    response = session.get(
        url, headers={"Accept": "application/json"}, timeout=HTTP_TIMEOUT
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
        return f"[{display}]({ORCID_RECORD_API}{ORCID_ID})"
    return display


def format_reference(meta: dict, doi: str) -> dict | None:
    try:
        title = meta["title"]
        year = meta["issued"]["date-parts"][0][0]
        authors = ", ".join(format_author(a) for a in meta["author"])
        publisher = meta.get("publisher", "")
        journal = meta.get("container-title", "")
        if meta.get("subtype") == "preprint" and publisher in PREPRINT_JOURNAL_LABELS:
            journal = PREPRINT_JOURNAL_LABELS[publisher]
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("Skipping %s: malformed metadata (%s)", doi, exc)
        return None

    reference = (
        f"{authors} ({year}). **{title}**. {journal}. "
        f"[{doi}](https://doi.org/{doi})"
    )
    return {"year": year, "reference": reference}


def extract_doi(work_summary: dict) -> str | None:
    ext_ids = (work_summary.get("external-ids") or {}).get("external-id", [])
    for ext in ext_ids:
        if ext.get("external-id-type") == "doi":
            return ext.get("external-id-value")
    return None


def extract_title(work_summary: dict) -> str:
    return (
        (work_summary.get("title") or {})
        .get("title", {})
        .get("value", "<unknown>")
    )


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

    entries: list[dict] = []
    for work in track(
        record["activities-summary"]["works"]["group"],
        "Fetching reference data...",
    ):
        summary = work["work-summary"][0]
        doi = extract_doi(summary)
        if doi is None:
            logger.warning("Skipping work without DOI: %s", extract_title(summary))
            continue

        try:
            meta = fetch_doi_metadata(session, doi)
        except requests.RequestException as exc:
            logger.warning("Skipping %s: Crossref fetch failed (%s)", doi, exc)
            continue

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
