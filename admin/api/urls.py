from django.urls import path
from .views import ListUsersView, UserCreateView
from .views import ListOrdersView, OrderCreateView
from .views import UserUpdateView, ListProductView
from .views import ListCategoryView

urlpatterns = [
    path('users/', ListUsersView.as_view(), name="users-all"),
    path('users/create/', UserCreateView.as_view(), name="user-create"),
    path('orders/', ListOrdersView.as_view(), name="orders-all"),
    path('products/', ListProductView.as_view(), name="products-all"),
    path('orders/create/', OrderCreateView.as_view(), name="order-create"),
    path(r'^users/(?P<id>\d+)$/update/', UserUpdateView.as_view(),name="order-update"),
    path('cats/', ListCategoryView.as_view(), name="cats-all"),
    
]