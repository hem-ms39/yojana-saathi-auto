"""
Embed schemes using Gemini text-embedding-004 and upload to Qdrant.
Replaces the OpenAI-based embedder (quota exceeded).
"""
import json
import os
import hashlib
import time
from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from tqdm import tqdm

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Qdrant client
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

COLLECTION = "schemes"
EMBED_MODEL = "models/gemini-embedding-001"
VECTOR_SIZE = 3072  # gemini-embedding-001 outputs 3072-dim


def recreate_collection():
    """Delete old collection and create fresh one with correct vector size."""
    try:
        existing = [c.name for c in qdrant.get_collections().collections]
        if COLLECTION in existing:
            qdrant.delete_collection(collection_name=COLLECTION)
            print(f"Deleted old collection: {COLLECTION}")
            import time; time.sleep(2)
    except Exception as e:
        print(f"Warning during delete: {e}")

    try:
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION} (dim={VECTOR_SIZE})")
    except Exception as e:
        if "already exists" in str(e):
            print(f"Collection exists, proceeding with upload")
        else:
            raise


def embed_text(text: str) -> list[float]:
    """Get embedding using Gemini text-embedding-004."""
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']


def embed_query(text: str) -> list[float]:
    """Get query embedding (uses retrieval_query task type for better search)."""
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="retrieval_query"
    )
    return result['embedding']


def scheme_id_to_int(scheme_id: str) -> int:
    """Convert string scheme_id to int for Qdrant point ID."""
    return int(hashlib.md5(scheme_id.encode()).hexdigest()[:12], 16)


def upload_schemes(json_path: str):
    """Embed and upload all schemes to Qdrant."""
    with open(json_path, encoding="utf-8") as f:
        schemes = json.load(f)
    
    print(f"\n📤 Uploading {len(schemes)} schemes to Qdrant...")
    
    points = []
    for s in tqdm(schemes, desc="Embedding"):
        # Use full_text for embedding
        embed_source = s.get("full_text", f"{s['title']}. {s['description']}")
        vector = embed_text(embed_source)
        
        # Build payload (everything searchable + displayable)
        payload = {
            "scheme_id": s["scheme_id"],
            "title": s.get("title", ""),
            "title_hi": s.get("title_hi", ""),
            "title_kn": s.get("title_kn", ""),
            "description": s.get("description", ""),
            "eligibility_text": s.get("eligibility_text", ""),
            "benefits_text": s.get("benefits_text", ""),
            "funding_amount": s.get("funding_amount"),
            "category": s.get("category", []),
            "target_group": s.get("target_group", []),
            "ministry": s.get("ministry", ""),
            "state": s.get("state", "all"),
            "min_age": s.get("min_age"),
            "max_age": s.get("max_age"),
            "max_income": s.get("max_income"),
            "documents_required": s.get("documents_required", []),
            "application_url": s.get("application_url", ""),
            "deadline": s.get("deadline"),
            "application_steps": s.get("application_steps", []),
            "full_text": embed_source,
        }
        
        points.append(PointStruct(
            id=scheme_id_to_int(s["scheme_id"]),
            vector=vector,
            payload=payload
        ))
        
        time.sleep(0.1)  # Gemini rate limit
    
    # Upload in batches
    BATCH = 50
    for i in range(0, len(points), BATCH):
        qdrant.upsert(collection_name=COLLECTION, points=points[i:i+BATCH])
    
    print(f"✅ Uploaded {len(points)} schemes to Qdrant")


def verify_search():
    """Run verification queries to ensure search quality."""
    test_queries = [
        ("young woman starting a tailoring business in Bangalore", 
         "Should find MUDRA, PMEGP, Stand-Up India"),
        ("farmer in Uttar Pradesh needs crop insurance",
         "Should find PM Fasal Bima, PM-KISAN, KCC"),
        ("scholarship for SC student after 10th class",
         "Should find NSP Post-Matric SC, NMMSS"),
        ("loan for small restaurant startup",
         "Should find MUDRA, PMEGP, CGTMSE"),
        ("healthcare coverage for poor family",
         "Should find Ayushman Bharat, PMSBY"),
    ]
    
    print(f"\n{'='*60}")
    print("🔍 VERIFICATION SEARCH RESULTS")
    print(f"{'='*60}")
    
    for query, expected in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        print(f"   Expected: {expected}")
        
        vector = embed_query(query)
        results = qdrant.query_points(
            collection_name=COLLECTION,
            query=vector,
            limit=5
        )
        
        for i, r in enumerate(results.points):
            score = r.score
            title = r.payload.get("title", "?")
            amount = r.payload.get("funding_amount", "N/A")
            amount_str = f"₹{amount:,}" if isinstance(amount, int) else "N/A"
            print(f"   {i+1}. [{score:.3f}] {title} ({amount_str})")
        
        time.sleep(0.5)
    
    # Print collection stats
    info = qdrant.get_collection(collection_name=COLLECTION)
    print(f"\nCollection stats:")
    print(f"   Points: {info.points_count}")
    print(f"   Status: {info.status}")


if __name__ == "__main__":
    recreate_collection()
    upload_schemes("../data/processed/seed_schemes.json")
    verify_search()
