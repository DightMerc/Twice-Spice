from django.urls import path
from .views import ListUsersView, UserCreateView
from .views import ListOrdersView, OrderCreateView


urlpatterns = [
    path('users/', ListUsersView.as_view(), name="users-all"),
    path('users/create/', UserCreateView.as_view(), name="user-create"),
    path('orders/', ListOrdersView.as_view(), name="orders-all"),
    path('orders/create/', OrderCreateView.as_view(), name="order-create"),
]