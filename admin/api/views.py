from django.shortcuts import render

from .models import TelegramUser
from .models import Order
from .models import Product
from .models import Category

from .serializers import UsersSerializer
from .serializers import OrderSerializer
from .serializers import ProductSerializer
from .serializers import CategorySerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from django.db import IntegrityError

# Create your views here.

class ListUsersView(APIView):
    def get(self, request, version):
        users = TelegramUser.objects.all()
        
        serializer = UsersSerializer(users, many=True)
        return Response({"users": serializer.data})
    
class UserCreateView(APIView):
    def post(self, request, version):

        # Create an article from the above data
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user_created = serializer.save()
                return Response({"success": "{} User '{}' created successfully".format(user_created.id, user_created.telegram_id)}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    return Response({"error": "User already exists"}, status=status.HTTP_409_CONFLICT)
            
class ListOrdersView(APIView):
    def get(self, request, version):
        orders = Order.objects.all()
        
        serializer = OrderSerializer(orders, many=True)
        return Response({"orders": serializer.data})


class ListCategoryView(APIView):
    def get(self, request, version):
        cats = Category.objects.all()
        
        serializer = CategorySerializer(cats, many=True)
        return Response({"categories": serializer.data})

    
class ListProductView(APIView):
    def get(self, request, version):
        products = Product.objects.all()
        
        serializer = ProductSerializer(products, many=True)
        return Response({"products": serializer.data})
    
class OrderCreateView(APIView):
    def post(self, request, version):

        # Create an article from the above data
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                order_created = serializer.save()
                return Response({"success": "Order created successfully"}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class UserUpdateView(APIView):
    def get_object(self, pk):
        try:
            return TelegramUser.objects.get(pk=pk)
        except TelegramUser.DoesNotExist:
            raise Http404

    def patch(self, request, version, pk, format=None):
        user = self.get_object(pk)
        serializer = UsersSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
