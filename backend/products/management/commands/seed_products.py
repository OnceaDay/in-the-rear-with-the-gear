import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from products.models import Category, Product


def load_json_file():
    """
    Load product data from the best available location.

    Priority order:
    1. products/data/products_updated.json
    2. products/data/products_with_real_images.json
    3. products_with_real_images.json
    4. products/data/products.json
    """
    candidate_paths = [
        Path("products/data/products_updated.json"),
        Path("products/data/products_with_real_images.json"),
        Path("products_with_real_images.json"),
        Path("products/data/products.json"),
    ]

    for path in candidate_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)

            if not isinstance(data, list):
                raise CommandError(f"{path} must contain a JSON array of products.")

            return data, path

    searched = "\n".join(str(path) for path in candidate_paths)
    raise CommandError(
        "Could not find a product data file. Checked:\n"
        f"{searched}"
    )


def safe_decimal(value, field_name: str, product_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise CommandError(
            f"Invalid decimal for '{field_name}' on product '{product_name}': {value}"
        ) from exc


def ensure_list(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


class Command(BaseCommand):
    help = "Seed or update products and categories from JSON data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing products before seeding.",
        )

    def handle(self, *args, **options):
        data, data_path = load_json_file()

        self.stdout.write(
            self.style.WARNING(f"Using data file: {data_path}")
        )

        if options["reset"]:
            deleted_count, _ = Product.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {deleted_count} existing product records."
                )
            )

        created_categories = 0
        updated_categories = 0
        created_products = 0
        updated_products = 0

        for item in data:
            product_name = item.get("name")
            product_slug = item.get("slug")

            if not product_name or not product_slug:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping product with missing name or slug: {item}"
                    )
                )
                continue

            category_data = item.get("category") or {}
            category_name = category_data.get("name")
            category_slug = category_data.get("slug")

            if not category_name or not category_slug:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping '{product_name}' because category data is incomplete."
                    )
                )
                continue

            category, category_created = Category.objects.get_or_create(
                slug=category_slug,
                defaults={"name": category_name},
            )

            if category_created:
                created_categories += 1
            else:
                category_updated = False

                if category.name != category_name:
                    category.name = category_name
                    category_updated = True

                if category_updated:
                    category.save(update_fields=["name"])
                    updated_categories += 1

            primary_image = item.get("primary_image", "")
            gallery_images = ensure_list(item.get("gallery_images"))

            defaults = {
                "name": product_name,
                "category": category,
                "short_description": item.get("short_description", ""),
                "long_description": item.get("long_description", ""),
                "price": safe_decimal(item.get("price", "0.00"), "price", product_name),
                "budget_tier": item.get("budget_tier", "budget"),
                "space_requirement": item.get("space_requirement", "small"),
                "in_stock": bool(item.get("in_stock", True)),
                "quantity_available": int(item.get("quantity_available", 0)),
                "tags": ensure_list(item.get("tags")),
                "features": ensure_list(item.get("features")),
                "accessibility_features": ensure_list(
                    item.get("accessibility_features")
                ),
                "primary_image": primary_image,
                "gallery_images": gallery_images,
                "image_alt_text": item.get(
                    "image_alt_text",
                    f"{product_name} in the {category_name} category",
                ),
            }

            try:
                product, created = Product.objects.update_or_create(
                    slug=product_slug,
                    defaults=defaults,
                )
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed updating '{product_name}' ({product_slug}): {exc}"
                    )
                )
                continue

            if created:
                created_products += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created product: {product.name}")
                )
            else:
                updated_products += 1
                self.stdout.write(
                    self.style.NOTICE(f"Updated product: {product.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeding complete. "
                f"Categories created: {created_categories}, "
                f"categories updated: {updated_categories}, "
                f"products created: {created_products}, "
                f"products updated: {updated_products}."
            )
        )