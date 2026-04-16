import json
from pathlib import Path

INPUT_FILE = Path("products/data/products_updated.json")
BASE_URL = "http://127.0.0.1:8000"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    primary_image = item.get("primary_image", "")
    if primary_image.startswith("/media/"):
        item["primary_image"] = f"{BASE_URL}{primary_image}"

    gallery_images = item.get("gallery_images", [])
    item["gallery_images"] = [
        f"{BASE_URL}{img}" if isinstance(img, str) and img.startswith("/media/") else img
        for img in gallery_images
    ]

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("products_updated.json has been updated with full image URLs.")