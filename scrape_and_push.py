import os
import requests
import time
from bs4 import BeautifulSoup
from huggingface_hub import HfApi, HfFolder, Repository, upload_file

BASE_URL = "https://rechtspraak.sr"
SEARCH_URL = f"{BASE_URL}/zoekresultaat"
DATASET_REPO_ID = "vGassen/Surinam-Dutch-Court-Cases"
SOURCE = "Uitsprakendatabank van het Hof van Justitie van Suriname"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_case_links():
    res = requests.get(SEARCH_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("a[href*='sru-']")
    urls = {BASE_URL + link['href'] for link in links}
    return list(urls)

def scrape_case(url):
    try:
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        content_section = soup.select_one("div.elementor-widget-container")
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

    urls = get_case_links()
    print(f"Found {len(urls)} URLs.")

    cases = []
    for url in urls:
        case = scrape_case(url)
        if case:
            cases.append(case)
        time.sleep(0.5)  # be polite to their server

    if not cases:
        print("No valid cases found.")
        return

    dataset = Dataset.from_list(cases)
    dataset.push_to_hub(DATASET_REPO_ID, token=hf_token)
    print(f"Pushed {len(cases)} cases to {DATASET_REPO_ID}.")

if __name__ == "__main__":
    main()
