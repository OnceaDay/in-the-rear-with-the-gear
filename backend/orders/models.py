from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import CustomerProfile
from carts.models import Cart
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    cart = models.OneToOneField(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"

    def recalculate_total(self):
        self.total = sum((item.subtotal for item in self.items.all()), Decimal("0.00"))
        self.save(update_fields=["total"])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=255)
    product_slug = models.SlugField(max_length=275)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product_name"]),
        ]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be at least 1."})

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        self.full_clean()
        super().save(*args, **kwargs)