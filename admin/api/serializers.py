from rest_framework import serializers
from .models import TelegramUser
from .models import Order
from .models import Product
from .models import Category



class UsersSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    phone = serializers.IntegerField()


    def create(self, validated_data):
        return TelegramUser.objects.create(**validated_data)

class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    picture = serializers.ImageField()

    def create(self, validated_data):
        return Category.objects.create(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'user', 'published_date', 'products')

    def create(self, validated_data):
        products = validated_data.pop('products')
        instance = Order.objects.create(**validated_data)
        for product in products:
            instance.products.add(product)

        return instance
        

class ProductSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=511)
    product_category = serializers.CharField()
    description = serializers.CharField()
    price = serializers.FloatField()

    picture = serializers.ImageField()

    def create(self, validated_data):
        return Product.objects.create(**validated_data)