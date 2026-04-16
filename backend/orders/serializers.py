from rest_framework import serializers

from .models import Order, OrderItem
from carts.models import Cart
from products.models import Product


class OrderProductSummarySerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "primary_image",
        ]

    def get_price(self, obj):
        return f"{obj.price:.2f}"


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderProductSummarySerializer(read_only=True)
    unit_price = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_slug",
            "unit_price",
            "quantity",
            "subtotal",
        ]
        read_only_fields = fields

    def get_unit_price(self, obj):
        return f"{obj.unit_price:.2f}"

    def get_subtotal(self, obj):
        return f"{obj.subtotal:.2f}"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "cart",
            "status",
            "total",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = fields

    def get_total(self, obj):
        return f"{obj.total:.2f}"


class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(),
        source="cart",
    )

    def validate_cart(self, cart):
        if not cart.is_active:
            raise serializers.ValidationError("This cart is no longer active.")

        if not cart.items.exists():
            raise serializers.ValidationError("Cannot checkout an empty cart.")

        return cart