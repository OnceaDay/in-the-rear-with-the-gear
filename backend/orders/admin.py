from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "unit_price", "quantity", "subtotal"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["customer__user__username", "customer__user__email"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product_name", "quantity", "unit_price", "subtotal"]
    search_fields = ["product_name"]