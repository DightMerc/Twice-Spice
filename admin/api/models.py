from django.db import models
from .fields import IntegerRangeField

class TelegramUser(models.Model):
    telegram_id = models.PositiveIntegerField("Telegram ID", default=0, unique=True, null=False)
    full_name = models.CharField("Name", max_length=255, default="", null=False)
    username = models.CharField("Username", max_length=255, default="", null=True)
    phone = models.PositiveIntegerField("Phone Number", null=True)

    def __str__(self):
        return str(self.telegram_id)


class Category(models.Model):
    title = models.CharField("Название", max_length=511, default="", unique=False, null=False)
    description = models.TextField("Описание")

    picture = models.ImageField(blank=True, null=True, upload_to="pictures/")

    class Meta:
         verbose_name = "product type"

    def __str__(self):
        return str(self.title)


class Product(models.Model):
    title = models.CharField("Название", max_length=511, default="", unique=False, null=False)
    product_category = models.ForeignKey(Category, default="", on_delete=models.CASCADE)
    description = models.TextField("Описание")

    price = models.FloatField("Цена", default=0)

    picture = models.ImageField(blank=True, null=True, upload_to="pictures/")

    def __str__(self):
        return str(self.title)

class Order(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    published_date = models.DateTimeField(blank=True, null=True)

    products = models.ManyToManyField(Product)
    
    def __str__(self):
        return str(self.user)

