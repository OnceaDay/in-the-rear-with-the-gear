from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "category_id",
            "short_description",
            "long_description",
            "price",
            "budget_tier",
            "space_requirement",
            "in_stock",
            "quantity_available",
            "tags",
            "features",
            "accessibility_features",
            "primary_image",
            "gallery_images",
            "image_alt_text",
            "created_at",
            "updated_at",
        ]