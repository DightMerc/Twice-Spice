from django.db import models
from .fields import IntegerRangeField

class TelegramUser(models.Model):
    telegram_id = models.PositiveIntegerField("Telegram ID", default=0, unique=True, null=False)
    full_name = models.CharField("Name", max_length=255, default="", null=False)
    username = models.CharField("Username", max_length=255, default="", null=True)
    phone = models.PositiveIntegerField("Phone Number", default=0, null=False)

    def __str__(self):
        return str(self.phone)


class Product(models.Model):
    title = models.CharField("Название", max_length=511, default="", unique=False, null=False)
    description = models.TextField("Описание")

    def __str__(self):
        return str(self.title)

class Order(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    published_date = models.DateTimeField(blank=True, null=True)
    delivery = models.BooleanField(default=False)
    latitude = models.IntegerField()
    longitude = models.IntegerField()

    products = models.ManyToManyField(Product)
    
    def __str__(self):
        return str(self.user)