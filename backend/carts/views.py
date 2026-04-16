
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_profile = self.request.user.customer_profile
        return (
            Cart.objects.select_related("customer")
            .prefetch_related("items__product")
            .filter(customer=customer_profile)
        )

    def perform_create(self, serializer):
        customer_profile = self.request.user.customer_profile

        existing_cart = Cart.objects.filter(customer=customer_profile, is_active=True).first()
        if existing_cart:
            raise ValidationError(
                {
                    "detail": "This user already has an active cart.",
                    "cart_id": existing_cart.id,
                }
            )

        serializer.save(customer=customer_profile)


class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_profile = self.request.user.customer_profile
        return (
            Cart.objects.select_related("customer")
            .prefetch_related("items__product")
            .filter(customer=customer_profile)
        )


class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_cart(self):
        customer_profile = self.request.user.customer_profile
        return get_object_or_404(Cart, pk=self.kwargs["cart_id"], customer=customer_profile)

    def get_queryset(self):
        return CartItem.objects.filter(cart=self.get_cart()).select_related("product", "cart")

    def perform_create(self, serializer):
        cart = self.get_cart()

        if not cart.is_active:
            raise ValidationError({"cart": "Cannot modify an inactive cart."})

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)

        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        if existing_item:
            raise ValidationError(
                {"detail": "This product is already in the cart. Update the quantity instead."}
            )

        if quantity > product.quantity_available:
            raise ValidationError(
                {"quantity": f"Only {product.quantity_available} item(s) available in stock."}
            )

        serializer.save(cart=cart)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_cart(self):
        customer_profile = self.request.user.customer_profile
        return get_object_or_404(Cart, pk=self.kwargs["cart_id"], customer=customer_profile)

    def get_queryset(self):
        return CartItem.objects.filter(cart=self.get_cart()).select_related("product", "cart")

    def perform_update(self, serializer):
        cart = self.get_cart()

        if not cart.is_active:
            raise ValidationError({"cart": "Cannot modify an inactive cart."})

        product = serializer.validated_data.get("product", serializer.instance.product)
        quantity = serializer.validated_data.get("quantity", serializer.instance.quantity)

        if quantity > product.quantity_available:
            raise ValidationError(
                {"quantity": f"Only {product.quantity_available} item(s) available in stock."}
            )

        serializer.save()