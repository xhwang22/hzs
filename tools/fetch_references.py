"""Collect citation metadata from primary arXiv records into the paper workspace."""
import concurrent.futures
import json
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAPERS = {
    "envharness": "2608.19880", "spade": "2608.19197", "facet": "2608.18580",
    "ace": "2608.27260", "autodata": "2606.25996", "envscaler": "2601.05808",
    "scaleenv": "2602.06820", "awm": "2602.10090", "envfactory": "2605.18703",
    "agentscaler": "2509.13311", "agentworld": "2604.18292", "datamaster": "2605.10906",
    "rods": "2606.19047", "writ": "2606.02908", "agentomnia": "2607.23124",
    "paired": "2012.02096", "plr": "2010.03934", "grpo": "2402.03300",
    "tau2": "2506.07982", "automationbench": "2604.18934", "rsibenchdata": "2607.25886",
}


def fetch(item):
    key, identity = item
    url = "https://arxiv.org/abs/" + identity
    target = ROOT / "sources/arxiv"
    target.mkdir(exist_ok=True)
    cached = target / (identity + ".html")
    if cached.is_file():
        html = cached.read_text()
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "EnvOpt-paper-bibliography/0.1"})
        with urllib.request.urlopen(request, timeout=40) as response:
            html = response.read().decode()
    soup = BeautifulSoup(html, "html.parser")
    def values(name):
        return [node["content"] for node in soup.find_all("meta", attrs={"name": name})]
    title, authors, date = values("citation_title"), values("citation_author"), values("citation_date")
    if not title or not authors or not date:
        raise ValueError("Incomplete metadata: " + url)
    (target / (identity + ".html")).write_text(html)
    return {"key": key, "arxiv": identity, "title": title[0], "authors": authors,
            "date": date[0], "url": url, "abstract": values("citation_abstract")}


if __name__ == "__main__":
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for record in pool.map(fetch, PAPERS.items()):
            records.append(record)
            print(record["key"], record["title"], flush=True)
    (ROOT / "sources/reference_metadata.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
