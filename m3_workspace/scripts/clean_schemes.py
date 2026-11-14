import json
import os

def clean_schemes(raw_path, output_path):
    if not os.path.exists(raw_path):
        print(f"Raw data not found at {raw_path}")
        return
        
    with open(raw_path, encoding="utf-8") as f:
        schemes = json.load(f)
    
    cleaned = []
    for s in schemes:
        if not s.get("title") or not s.get("description"):
            continue
        
        # Normalize fields
        s["scheme_id"] = s.get("scheme_id", "").lower().replace(" ", "-")
        s["funding_amount"] = parse_amount(s.get("funding_amount"))
        s["category"] = s.get("category", [])
        s["state"] = s.get("state", "all").lower()
        s["min_age"] = safe_int(s.get("min_age"))
        s["max_age"] = safe_int(s.get("max_age"))
        
        # Build full_text for embedding
        s["full_text"] = f"{s['title']}. {s['description']}. " \
                         f"Eligibility: {s.get('eligibility_text', '')}. " \
                         f"Benefits: {s.get('benefits_text', '')}."
        
        cleaned.append(s)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned: {len(cleaned)} schemes from {len(schemes)} raw")
    print(f"Saved to: {output_path}")

def parse_amount(val):
    if isinstance(val, int): return val
    if not val: return None
    text = str(val).replace("₹", "").replace(",", "").strip()
    if "lakh" in text.lower():
        return int(float(text.lower().replace("lakh", "").strip()) * 100000)
    if "crore" in text.lower():
        return int(float(text.lower().replace("crore", "").strip()) * 10000000)
    try: return int(text)
    except: return None

def safe_int(val):
    try: return int(val)
    except: return None

if __name__ == "__main__":
    clean_schemes("../data/raw/scraped_schemes.json", "../data/processed/seed_schemes.json")
