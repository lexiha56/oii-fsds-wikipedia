import argparse
from collections.abc import Callable, Generator
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

DATA_DIR = Path("data")


def download_page_w_revisions(page_title: str, limit: int = 100) -> str:
    base_url = "https://en.wikipedia.org/w/index.php"
    params = {
        "title": "Special:Export",
        "pages": page_title,
        "limit": min(limit, 1000),  # Wikipedia API limits to 1000 revisions
        "dir": "desc",
        "action": "submit",
    }
    response = requests.post(base_url, data=params)
    response.raise_for_status()
    return response.text


def parse_mediawiki_revisions(xml_content: str) -> Generator[str, None, None]:
    soup = BeautifulSoup(xml_content, "lxml-xml")
    for revision in soup.find_all("revision"):
        yield str(revision)


def extract_id(revision: str) -> str:
    return str(_extract_attribute(revision, attribute="id"))


def find_timestamp(revision: str) -> datetime:
    return parse_timestring(_extract_attribute(revision, attribute="timestamp"))


def _extract_attribute(text: str, attribute: str = "timestamp") -> str:
    soup = BeautifulSoup(text, "lxml-xml")
    result = soup.find(attribute)
    if result is None:
        raise ValueError(f"Could not find attribute {attribute} in text")
    return result.text


def parse_timestring(timestring: str) -> datetime:
    return datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%SZ")


def _extract_yearmonth(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m")


def find_yearmonth(revision: str) -> str:
    return _extract_yearmonth(find_timestamp(revision))


def construct_path(page_name: str, save_dir: Path, wiki_revision: str) -> Path:
    revision_id = extract_id(wiki_revision)
    timestamp = find_timestamp(wiki_revision)
    year = str(timestamp.year)
    month = str(timestamp.month).zfill(2)
    revision_path = save_dir / page_name / year / month / f"{revision_id}.xml"
    return revision_path


def count_revisions(revisions_dir: Path) -> int:
    return sum(1 for _ in revisions_dir.rglob("*.xml"))


def _extract_yearmonth(path: Path) -> str:
    return f"{path.parent.parent.name}-{path.parent.name}"


def _find_yearmonth_with_func(revisions_dir: Path, sort_func: Callable) -> str:
    return _extract_yearmonth(sort_func(revisions_dir.rglob("*.xml")))


def find_first_revision_yearmonth(revisions_dir: Path) -> str:
    return _find_yearmonth_with_func(revisions_dir, min)


def find_last_revision_yearmonth(revisions_dir: Path) -> str:
    return _find_yearmonth_with_func(revisions_dir, max)


def download_revisions(page: str, limit: int, data_dir: Path) -> None:
    raw_revisions = download_page_w_revisions(page, limit=limit)
    validate_page(page, page_xml=raw_revisions)
    print("Downloaded revisions. Parsing and saving...")
    for wiki_revision in tqdm(parse_mediawiki_revisions(raw_revisions), total=limit):
        revision_path = construct_path(
            wiki_revision=wiki_revision, page_name=page, save_dir=data_dir
        )
        if not revision_path.exists():
            revision_path.parent.mkdir(parents=True, exist_ok=True)
        revision_path.write_text(wiki_revision)
    print("Done!")


def validate_page(page_name: str, page_xml: str) -> None:
    try:
        _ = _extract_attribute(page_xml, attribute="page")
    except ValueError:
        raise ValueError(f"Page {page_name} does not exist")


def main(page: str, limit: int, data_dir: Path, update: bool = False):
    """
    Downloads the main page (with revisions) for the given page title.
    Organizes the revisions into a folder structure like
    <page_name>/<year>/<month>/<revision_id>.xml
    """
    print(f"Downloading {limit} revisions of {page} to {data_dir}")
    page_directory = data_dir / page
    if not update and (page_directory).exists():
        print(f"Page {page} already exists. Skipping download.")
    else:
        download_revisions(page, limit, data_dir)

    revision_count = count_revisions(page_directory)
    max_yearmonth = find_last_revision_yearmonth(page_directory)
    min_yearmonth = find_first_revision_yearmonth(page_directory)
    print(
        f"Page {page} had {revision_count} revisions between {min_yearmonth} and {max_yearmonth}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download Wikipedia page revisions",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("page", type=str, help="Title of the Wikipedia page")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of revisions to download",
    )
    parser.add_argument(
        "--update", action="store_true", help="Should new data be updated?"
    )
    args = parser.parse_args()
    main(page=args.page, limit=args.limit, data_dir=DATA_DIR, update=args.update)
