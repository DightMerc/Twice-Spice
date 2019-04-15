from django.shortcuts import render

from .models import TelegramUser
from .models import Order
from .models import Product

from .serializers import UsersSerializer
from .serializers import OrderSerializer
from .serializers import ProductSerializer

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
                return Response({"success": "User '{}' created successfully".format(user_created.telegram_id)}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    return Response({"error": "User already exists"}, status=status.HTTP_409_CONFLICT)
            
class ListOrdersView(APIView):
    def get(self, request, version):
        orders = Order.objects.all()
        
        serializer = OrderSerializer(orders, many=True)
        return Response({"orders": serializer.data})
    
class OrderCreateView(APIView):
    def post(self, request, version):

        # Create an article from the above data
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user_created = serializer.save()
                return Response({"success": "Order '{}' created successfully".format(user_created.title)}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


            
