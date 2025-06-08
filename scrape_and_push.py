import os
import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "https://rechtspraak.sr"
AJAX_URL = f"{BASE_URL}/wp-content/themes/understrap/templates/loadmore_search_results.php"
DATASET_REPO_ID = "vGassen/Surinam-Dutch-Court-Cases"
SOURCE = "Uitsprakendatabank van het Hof van Justitie van Suriname"

# maximum number of case URLs to fetch
MAX_CASES = 500

# file used to keep track of already processed URLs
PROCESSED_FILE = "processed_urls.txt"


def load_processed_urls():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_processed_urls(urls):
    if not urls:
        return
    with open(PROCESSED_FILE, "a") as f:
        for url in urls:
            f.write(url + "\n")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_case_links(max_cases: int = MAX_CASES):
    """Retrieve up to `max_cases` case URLs by mimicking the site's AJAX search."""
    session = requests.Session()

    page = 1
    urls = set()

    while len(urls) < max_cases:
        payload = {
            "paged": page,
            "sText": "",
            "sField": "",
            "sSortOrder": "pronunciation_asc",
            "sAuthority[]": "all",
            "sCaseNumber": "",
            "sJurisdiction[]": "all",
            "declaration_date": "",
            "publication_date": "",
            "sDateType": "",
            "sDatePeriod": "",
            "sStartDate": "",
            "sEndDate": "",
            "search_type": "advance_search",
            "search_type2": "advance_search",
            "max_records_display": str(max_cases),
            "sSruNumber": "",
        }

        res = session.post(AJAX_URL, headers=HEADERS, data=payload)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("a[href*='sru-']")
        if not links:
            break
        for link in links:
            href = link.get("href")
            if not href:
                continue
            if not href.startswith("http"):
                href = BASE_URL + href
            urls.add(href)
            if len(urls) >= max_cases:
                break
        page += 1

    return list(urls)[:max_cases]

def scrape_case(url):
    try:
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        content_section = soup.select_one("div.sru-list.sru-content")
        if not content_section:
            return None
        content = content_section.get_text(separator="\n", strip=True)
        return {
            "url": url,
            "content": content,
            "source": SOURCE
        }
    except Exception:
        return None

def main():
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not set")

    from datasets import Dataset, DatasetDict

    processed = load_processed_urls()

    urls = get_case_links(MAX_CASES)
    new_urls = [u for u in urls if u not in processed]
    print(f"Found {len(new_urls)} new URLs out of {len(urls)} total.")

    cases = []
    for url in new_urls:
        case = scrape_case(url)
        if case:
            cases.append(case)
        time.sleep(0.5)  # be polite to their server

    if not cases:
        print("No new cases found.")
        return

    dataset = Dataset.from_list(cases)
    dataset.push_to_hub(DATASET_REPO_ID, token=hf_token)
    save_processed_urls(new_urls)
    print(f"Pushed {len(cases)} cases to {DATASET_REPO_ID}.")

if __name__ == "__main__":
    main()
