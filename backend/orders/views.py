from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer, CheckoutSerializer
from common.services.checkout import process_checkout, restore_stock_for_order


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_profile = self.request.user.customer_profile

        queryset = (
            Order.objects.select_related("customer", "cart")
            .prefetch_related("items", "items__product")
            .filter(customer=customer_profile)
        )

        status_value = self.request.query_params.get("status")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if status_value:
            queryset = queryset.filter(status=status_value)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_profile = self.request.user.customer_profile
        return (
            Order.objects.select_related("customer", "cart")
            .prefetch_related("items", "items__product")
            .filter(customer=customer_profile)
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        customer_profile = self.request.user.customer_profile
        return (
            Order.objects.select_related("customer", "cart")
            .prefetch_related("items", "items__product")
            .filter(customer=customer_profile)
        )

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")

        valid_statuses = {"pending", "shipped", "delivered", "cancelled"}
        if new_status not in valid_statuses:
            raise ValidationError({"status": "Invalid status."})

        if new_status == "cancelled":
            order = restore_stock_for_order(order)
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = serializer.validated_data["cart"]

        if cart.customer != request.user.customer_profile:
            raise ValidationError({"cart_id": "You do not have permission to checkout this cart."})

        order = process_checkout(cart)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)