import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# =========================
# CONFIG
# =========================
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
INPUT_JSON = Path("products/data/products.json")
OUTPUT_JSON = Path("products_with_real_images.json")
MEDIA_DIR = Path("media/products")
REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.6

# Prefer medium-large images for web use
PEXELS_SIZE_KEY_ORDER = [
    "large",
    "large2x",
    "medium",
    "landscape",
    "original",
]

CATEGORY_HINTS = {
    "living-room": "living room furniture",
    "bedroom": "bedroom furniture",
    "office": "office furniture workspace",
    "electronics": "consumer electronics desk setup",
    "storage": "storage furniture shelving",
}

GENERIC_FALLBACK_HINTS = {
    "chair": "modern chair interior",
    "sofa": "modern sofa living room",
    "couch": "modern couch living room",
    "loveseat": "loveseat living room",
    "ottoman": "ottoman furniture interior",
    "rug": "area rug interior",
    "lamp": "table lamp interior",
    "desk": "modern desk office",
    "bookcase": "bookcase shelf interior",
    "bookshelf": "bookshelf interior",
    "cabinet": "cabinet furniture interior",
    "dresser": "dresser bedroom furniture",
    "nightstand": "nightstand bedroom",
    "wardrobe": "wardrobe closet furniture",
    "bed": "bedroom bed furniture",
    "headboard": "bed headboard bedroom",
    "monitor": "computer monitor desk",
    "keyboard": "computer keyboard desk",
    "mouse": "computer mouse desk",
    "router": "wifi router desk",
    "webcam": "webcam desk setup",
    "speaker": "speaker desk setup",
    "microphone": "microphone desk setup",
}

# =========================
# HELPERS
# =========================
def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def build_queries(product: Dict[str, Any]) -> List[str]:
    name = product.get("name", "").strip()
    slug = product.get("slug", "").strip()
    category = (product.get("category") or {}).get("slug", "").strip()

    queries: List[str] = []

    if name and category:
        queries.append(f"{name} {CATEGORY_HINTS.get(category, category)}")

    if name:
        queries.append(name)

    for token, hint in GENERIC_FALLBACK_HINTS.items():
        if token in slug:
            queries.append(hint)

    if category:
        queries.append(CATEGORY_HINTS.get(category, category))

    # dedupe while preserving order
    seen = set()
    deduped = []
    for q in queries:
        key = q.lower().strip()
        if key and key not in seen:
            seen.add(key)
            deduped.append(q)
    return deduped


def pexels_headers() -> Dict[str, str]:
    if not PEXELS_API_KEY:
        raise RuntimeError(
            "PEXELS_API_KEY is missing. Set it in your environment first."
        )
    return {"Authorization": PEXELS_API_KEY}


def search_pexels_photo(query: str) -> Optional[Dict[str, Any]]:
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "per_page": 5,
        "orientation": "landscape",
        "size": "medium",
    }
    response = requests.get(
        url,
        headers=pexels_headers(),
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    photos = data.get("photos", [])
    return photos[0] if photos else None


def pick_photo_src(photo: Dict[str, Any]) -> Optional[str]:
    src = photo.get("src", {})
    for key in PEXELS_SIZE_KEY_ORDER:
        if src.get(key):
            return src[key]
    return None


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
        response.raise_for_status()
        with open(destination, "wb") as file_obj:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_obj.write(chunk)


def file_extension_from_url(url: str) -> str:
    lower = url.lower()
    if ".png" in lower:
        return ".png"
    if ".webp" in lower:
        return ".webp"
    return ".jpg"


def enrich_product(product: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(product)
    slug = updated.get("slug") or slugify(updated.get("name", "product"))
    name = updated.get("name", "Product")
    category_name = (updated.get("category") or {}).get("name", "Product")

    chosen_photo = None
    chosen_query = None

    for query in build_queries(updated):
        try:
            photo = search_pexels_photo(query)
            if photo:
                chosen_photo = photo
                chosen_query = query
                break
        except requests.HTTPError as exc:
            print(f"[WARN] Search failed for '{name}' with query '{query}': {exc}")
            continue

    if not chosen_photo:
        print(f"[MISS] No image found for {name}")
        return updated

    image_url = pick_photo_src(chosen_photo)
    if not image_url:
        print(f"[MISS] No usable src found for {name}")
        return updated

    ext = file_extension_from_url(image_url)
    filename = f"{slug}{ext}"
    local_path = MEDIA_DIR / filename

    try:
        download_file(image_url, local_path)
    except requests.HTTPError as exc:
        print(f"[WARN] Download failed for '{name}': {exc}")
        return updated

    updated["primary_image"] = f"/media/products/{filename}"
    updated["gallery_images"] = []
    updated["image_alt_text"] = f"{name} in the {category_name} category"
    updated["_image_source"] = {
        "provider": "Pexels",
        "query": chosen_query,
        "photographer": chosen_photo.get("photographer"),
        "pexels_url": chosen_photo.get("url"),
    }

    print(f"[OK] {name} -> {updated['primary_image']} ({chosen_query})")
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    return updated


def main() -> None:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_JSON}")

    with open(INPUT_JSON, "r", encoding="utf-8") as file_obj:
        products: List[Dict[str, Any]] = json.load(file_obj)

    enriched = [enrich_product(product) for product in products]

    with open(OUTPUT_JSON, "w", encoding="utf-8") as file_obj:
        json.dump(enriched, file_obj, indent=2, ensure_ascii=False)

    print(f"\nDone. Wrote: {OUTPUT_JSON}")
    print(f"Downloaded images to: {MEDIA_DIR.resolve()}")


if __name__ == "__main__":
    main()