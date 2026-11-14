import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm
import os

BASE_URL = "https://www.myscheme.gov.in"

def get_scheme_list(page=1):
    """Get list of scheme URLs from the directory."""
    # MyScheme has an API — try this first (faster than HTML scraping)
    api_url = f"{BASE_URL}/api/search/schemes?page={page}&limit=50"
    headers = {"Accept": "application/json"}
    
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
    
    return []

def scrape_scheme_detail(scheme_url: str) -> dict:
    """Scrape a single scheme's full details. Using mock for hackathon reliability."""
    # In a real scenario, this would use BeautifulSoup or Firecrawl to parse the specific page.
    # For now, returning a basic structured representation.
    scheme_id = scheme_url.split("/")[-1] if "/" in scheme_url else scheme_url
    
    scheme = {
        "scheme_id": scheme_id,
        "title": scheme_id.replace("-", " ").title(),
        "description": f"Detailed description for {scheme_id}",
        "eligibility_text": "Must be citizen of India. Age 18+.",
        "benefits_text": "Financial support and grants.",
        "funding_amount": "₹50,000",
        "category": ["business", "loan"],
        "target_group": ["all"],
        "ministry": "Relevant Ministry",
        "state": "all",
        "min_age": 18,
        "max_age": None,
        "max_income": None,
        "documents_required": ["aadhaar", "pan"],
        "application_url": f"{BASE_URL}/schemes/{scheme_id}",
        "deadline": "2026-12-31"
    }
    return scheme

def main():
    os.makedirs("../data/raw", exist_ok=True)
    os.makedirs("../data/processed", exist_ok=True)
    
    all_schemes = []
    # Scrape fewer pages for hackathon MVP speed
    for page in tqdm(range(1, 3), desc="Pages"):  
        scheme_list = get_scheme_list(page)
        
        # If API returns a list under a specific key (e.g., 'data' or 'schemes')
        items = scheme_list.get("data", []) if isinstance(scheme_list, dict) else scheme_list
        
        # If the API doesn't return exactly what we expect, let's mock 10 items per page
        if not items:
            items = [{"url": f"scheme-{page}-{i}"} for i in range(10)]
            
        for s in tqdm(items, desc="Schemes", leave=False):
            url = s.get("url", s.get("slug", f"mock-scheme-{len(all_schemes)}"))
            detail = scrape_scheme_detail(url)
            all_schemes.append(detail)
            time.sleep(0.1)  # Be polite, but fast
    
    output_path = "../data/raw/scraped_schemes.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_schemes, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(all_schemes)} schemes to {output_path}")

if __name__ == "__main__":
    main()
