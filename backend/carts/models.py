from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from accounts.models import CustomerProfile
from products.models import Product


class Cart(models.Model):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="carts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["customer"],
                condition=Q(is_active=True),
                name="unique_active_cart_per_customer",
            )
        ]

    def __str__(self):
        return f"Cart #{self.id} - {self.customer}"

    @property
    def total(self):
        return sum(
            (item.product.price * item.quantity for item in self.items.select_related("product").all()),
            Decimal("0.00"),
        )

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="unique_product_per_cart")
        ]
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Cart #{self.cart.id}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be at least 1."})

        if self.quantity > self.product.quantity_available:
            raise ValidationError(
                {"quantity": f"Only {self.product.quantity_available} item(s) available in stock."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.product.price * self.quantity