from django.db import transaction
from rest_framework.exceptions import ValidationError

from orders.models import Order, OrderItem


def process_checkout(cart):
    with transaction.atomic():
        cart_items = list(cart.items.select_related("product").all())

        if not cart_items:
            raise ValidationError({"cart_id": "Cannot checkout an empty cart."})

        if not cart.is_active:
            raise ValidationError({"cart_id": "This cart is no longer active."})

        for item in cart_items:
            product = item.product

            if item.quantity > product.quantity_available:
                raise ValidationError(
                    {
                        "quantity": (
                            f"Not enough stock for '{product.name}'. "
                            f"Only {product.quantity_available} item(s) available."
                        )
                    }
                )

        order = Order.objects.create(
            customer=cart.customer,
            cart=cart,
            status="pending",
        )

        for item in cart_items:
            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_slug=product.slug,
                unit_price=product.price,
                quantity=item.quantity,
            )

            product.quantity_available -= item.quantity
            product.save()

        order.recalculate_total()

        cart.is_active = False
        cart.save(update_fields=["is_active", "updated_at"])

        return order


def restore_stock_for_order(order):
    with transaction.atomic():
        if order.status in ["shipped", "delivered"]:
            raise ValidationError(
                {"status": "Cannot cancel shipped or delivered orders."}
            )

        if order.status == "cancelled":
            raise ValidationError({"status": "This order is already cancelled."})

        for item in order.items.select_related("product").all():
            if item.product:
                item.product.quantity_available += item.quantity
                item.product.save()

        order.status = "cancelled"
        order.save(update_fields=["status", "updated_at"])

        return order