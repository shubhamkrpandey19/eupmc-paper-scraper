import requests
import pathlib
import time
import json
import re

# Europe PMC API endpoint
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"     #need to call api one more time

# Output folder for PDFs
PDF_DIR = pathlib.Path("pdfs_new")
PDF_DIR.mkdir(exist_ok=True)

# Custom User-Agent (always good practice)
HEADERS = {
    "User-Agent": "opsin-lambda-scraper/0.1 (pand2623@vandals.uidaho.edu)" #adding your email is optional
}

def pdf_url_from_eupmc(doi):
    """
    Given a DOI, return the first open-access PDF URL from Europe PMC.
    Returns None if not available.
    """
    query = f"DOI:{doi}"
    params = {
        "query": query,
        "format": "json",
        "resultType": "core",
        "fields": "title,pmcid,fullTextUrlList"
    }

    data = requests.get(API, params=params, headers=HEADERS, timeout=20).json()
    hits = data.get("resultList", {}).get("result", [])
    if not hits:
        return None

    urls = hits[0].get("fullTextUrlList", {}).get("fullTextUrl", [])
    for u in urls:
        if u.get("documentStyle") == "pdf":
            return u["url"]

    return None

def slugify(text):
    """
    Sanitize a DOI string into a safe filename format.
    Replaces non-alphanumeric characters with underscores.
    """
    return re.sub(r'[^\w.-]', '_', text)

# Load the list of DOIs
with open("europepmc_dois.txt") as f:
    dois = [line.strip() for line in f if line.strip()]

missing = []

# Loop through DOIs and download PDFs
for i, doi in enumerate(dois, 1):
    print(f"[{i}/{len(dois)}] {doi}", end="  ")
    pdf_url = pdf_url_from_eupmc(doi)

    if not pdf_url:
        print("No PDF found")
        missing.append(doi)
        continue

    # Construct output filename
    fname = PDF_DIR / f"{slugify(doi)}.pdf"

    # Skip if already downloaded
    if fname.exists():
        print("Already downloaded")
        continue

    # Attempt to download the PDF
    try:
        with requests.get(pdf_url, stream=True, headers=HEADERS, timeout=30) as r:
            r.raise_for_status()
            with open(fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Downloaded")
    except Exception as e:
        print(f"Download failed ({e})")
        missing.append(doi)

    time.sleep(0.1)  # polite delay (~10 requests per second)

# Save list of DOIs that failed to download
if missing:
    with open("missing_pdfs.txt", "w") as m:
        m.write("\n".join(missing))
    print(f"\nDownload completed with {len(missing)} missing PDFs. See 'missing_pdfs.txt'.")
else:
    print("\nDownload completed. All PDFs downloaded successfully.")
