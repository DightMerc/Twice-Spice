import requests

from config import url

import json



class Client(object):

    def CreateUser(self, telegram_id, full_name, username, phone):

        usr = User(telegram_id=telegram_id, full_name=full_name, username=username, phone=phone)
        headers = {'Content-Type': 'application/json'}

        r = requests.post(url + "api/v2/users/create/", data=json.dumps(usr.__dict__), headers=headers)
        print(r.status_code)
        return str(r.json())

    def CreateOrder(self, user, published_date, products):
        bk = Order(user=user, published_date=published_date, products=products)
        headers = {'Content-Type': 'application/json'}

        r = requests.post(url + "api/v2/orders/create/", data=json.dumps(bk.__dict__), headers=headers)

        return str(r.status_code)

    def GetAllProducts(self):
        r = requests.get(url + 'api/v2/products/')

        Products = r.json()

        array_to_return = []

        Products = Products['products']
        for a in Products:
            new = Payload(json.dumps(a))
            array_to_return.append(new)

        return(array_to_return)

    def GetAllUsers(self):
        r = requests.get(url + 'api/v2/users/')
        print(r.status_code)

        return(r.json())

    def GetAllCats(self):
        r = requests.get(url + 'api/v2/cats/')
        print(r.status_code)

        cats = r.json()

        array_to_return = []

        cats = cats['categories']
        for a in cats:
            new = Payload(json.dumps(a))
            array_to_return.append(new)

        return(array_to_return)

class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


class User(object):

    def __init__(self, telegram_id, full_name, username, phone):
        self.telegram_id = telegram_id
        self.full_name = full_name
        if username!="":
            self.username = username
        else:
            self.username = ""
        self.phone = phone


class Category(object):

    def __init__(self, title, description, picture):
        self.title = title
        self.description = description
        self.picture = picture
        

class Order(object):

    def __init__(self, user, published_date, products):
        self.user = user
        self.published_date = published_date
        self.products = products

class Product(object):

    def __init__(self, title, catproduct_category, description, price, picture):
        self.title = title
        self.product_category = product_category

        if description!="description":
            self.description = description
        else:
            self.description = "Описание отсутствует"

        self.price = price
        self.picture = picture