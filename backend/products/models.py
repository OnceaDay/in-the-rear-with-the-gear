from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    BUDGET_TIERS = [
        ("budget", "Budget"),
        ("midrange", "Midrange"),
        ("premium", "Premium"),
    ]

    SPACE_REQUIREMENTS = [
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=275, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    short_description = models.CharField(max_length=255, blank=True)
    long_description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    budget_tier = models.CharField(
        max_length=20,
        choices=BUDGET_TIERS,
        blank=True,
    )
    space_requirement = models.CharField(
        max_length=20,
        choices=SPACE_REQUIREMENTS,
        blank=True,
    )

    in_stock = models.BooleanField(default=True)
    quantity_available = models.PositiveIntegerField(default=0)

    tags = models.JSONField(default=list, blank=True)
    features = models.JSONField(default=list, blank=True)
    accessibility_features = models.JSONField(default=list, blank=True)

    primary_image = models.URLField(blank=True)
    gallery_images = models.JSONField(default=list, blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["price"]),
            models.Index(fields=["in_stock"]),
            models.Index(fields=["category"]),
            models.Index(fields=["budget_tier"]),
            models.Index(fields=["space_requirement"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.quantity_available == 0 and self.in_stock:
            self.in_stock = False

        if self.quantity_available > 0 and not self.in_stock:
            self.in_stock = True

        if self.price < 0:
            raise ValidationError({"price": "Price cannot be negative."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        self.in_stock = self.quantity_available > 0
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.in_stock and self.quantity_available > 0

    @property
    def main_image(self):
        return self.primary_image or ""

    def reduce_stock(self, quantity):
        if quantity <= 0:
            raise ValidationError("Quantity to reduce must be greater than zero.")

        if quantity > self.quantity_available:
            raise ValidationError("Not enough stock available.")

        self.quantity_available -= quantity
        self.in_stock = self.quantity_available > 0
        self.save()

    def increase_stock(self, quantity):
        if quantity <= 0:
            raise ValidationError("Quantity to increase must be greater than zero.")

        self.quantity_available += quantity
        self.in_stock = self.quantity_available > 0
        self.save()