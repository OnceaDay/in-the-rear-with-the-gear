from rest_framework import serializers

from .models import Cart, CartItem
from accounts.models import CustomerProfile
from products.models import Product
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True,
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "subtotal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "subtotal", "created_at", "updated_at"]

    def get_subtotal(self, obj):
        return f"{obj.subtotal:.2f}"


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "customer",
            "is_active",
            "created_at",
            "updated_at",
            "items",
            "total",
            "total_items",
        ]
        read_only_fields = fields

    def get_total(self, obj):
        return f"{obj.total:.2f}"

    def get_total_items(self, obj):
        return obj.total_items