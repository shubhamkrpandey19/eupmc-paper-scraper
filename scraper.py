import requests
import time

# Define the search query for <your research>-related papers
query = " put your desired keywords here. use AND and OR logic to improve the search "

# Europe PMC API endpoint
BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# Paging settings
page = 1 # start your search from first page to achieve more related results
page_size = 1000     # maximum number of results per API call
max_pages = 2        # how many pages to fetch

# Set to store unique DOIs
all_dois = set()

# Loop through pages and collect DOIs
while page <= max_pages:
    print(f"Fetching page {page}...", end="\r")

    params = {
        "query": query,
        "format": "json",
        "pageSize": page_size,
        "page": page,
        "resultType": "core",   # only fetch basic metadata
        "fields": "doi"         # only retrieve DOI field
    }

    # Send the request
    response = requests.get(BASE_URL, params=params, timeout=30)
    data = response.json()

    # Extract results
    results = data.get("resultList", {}).get("result", [])
    if not results:
        break  # stop if no more results

    # Store DOIs in a set to avoid duplicates
    for item in results:
        doi = item.get("doi")
        if doi:
            all_dois.add(doi.lower().strip())

    page += 1
    time.sleep(0.1)  # brief pause to avoid hitting API too hard

# Save the DOIs to a text file
with open("europepmc_dois.txt", "w") as f:
    for doi in sorted(all_dois):
        f.write(doi + "\n")

print(f"Collected {len(all_dois)} unique DOIs from Europe PMC.")
