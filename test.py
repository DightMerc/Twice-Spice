import client
import datetime

cli = client.Client()

Products = cli.GetAllProducts()

for a in Products:
    print("Title: {} + Description: {}".format(a.title, a.description))

array = []

a = 1
while a < len(Products):
    array.append(a)
    a+=1

time = datetime.datetime.now().replace(microsecond=0).isoformat()
print(cli.CreateOrder(3, time, array))

