from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]
    search_fields = ["name", "slug"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "category", "price", "quantity_available", "in_stock"]
    search_fields = ["name", "slug"]
    list_filter = ["category", "in_stock", "budget_tier", "space_requirement"]