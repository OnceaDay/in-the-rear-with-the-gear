from django.urls import path

from .views import (
    CartListCreateView,
    CartDetailView,
    CartItemListCreateView,
    CartItemDetailView,
)

urlpatterns = [
    path("", CartListCreateView.as_view(), name="cart-list-create"),
    path("<int:pk>/", CartDetailView.as_view(), name="cart-detail"),
    path("<int:cart_id>/items/", CartItemListCreateView.as_view(), name="cartitem-list-create"),
    path("<int:cart_id>/items/<int:pk>/", CartItemDetailView.as_view(), name="cartitem-detail"),
]