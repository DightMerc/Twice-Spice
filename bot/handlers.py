from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler, ShippingQueryHandler)

import telegram

import logging
import config
from functools import wraps
import requests

import datetime
import os
from client import Client
import threading
from telegram import ParseMode

from telegram import LabeledPrice


from emoji import emojize

users_path = os.getcwd() + "\\Users\\"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def CreateTelegramUser(user, full_name, username, phone):
    print("Creating new user...", end = " ")

    if str(username)=="None":
        username = "none"
    phone = str(phone).replace("+","")
    phone = str(phone).replace("-","")
    phone = str(phone).replace(" ","")

    cli = Client()
    cli.CreateUser(user, full_name, username, phone)

    return

def CreateOrder(user, published_date, products):

    cli = Client()
    print(cli.CreateOrder(user, published_date, products))

    return 

def GetAllProducts():

    cli = Client()

    products_payload = cli.GetAllProducts()

    product_list = []

    prod_title = []
    prod_description = []
    prod_price = []
    prod_image = []

    for a in products_payload:
        prod_title.append(a.title)
        prod_description.append(a.description)
        prod_price.append(a.price)
        prod_image.append(a.picture)

    
    product_list.append(prod_title)
    product_list.append(prod_description)
    product_list.append(prod_price)
    product_list.append(prod_image)


    return product_list


def send_typing_action(func):

    @wraps(func)
    def command_func(*args, **kwargs):
        bot, update = args
        bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(bot, update, **kwargs)

    return command_func


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def deleteTemp(bot, user):
    try:
        with open(users_path+str(user)+"\\temp_id", "r", encoding="utf8") as file:
            value = file.readlines()
            a = 0
            while a<len(value):
                temp_id = int(value[a].replace("\n",""))
                try:
                    bot.deleteMessage(user, temp_id)
                    a+=1
                except Exception as e:
                    a+=1

    except Exception as e:
        pass

def deleteTemp1(bot, user, num):
    try:
        with open(users_path+str(user)+"\\temp_id", "r", encoding="utf8") as file:
            value = file.readlines()

            temp_id = int(value[int(num)].replace("\n",""))
            try:
                bot.deleteMessage(user, temp_id)
            except Exception as e:
                pass

    except Exception as e:
        pass

@send_typing_action
def TextHandler(bot, update):

    user = update.message.from_user.id
    recieved_text = update.message.text

    #bot.deleteMessage(user, update.message.message_id)

    if  "Оформить заказ" in recieved_text:
        deleteTemp(bot, user)
        bot.deleteMessage(user, update.message.message_id)


        if not os.path.exists(users_path + str(user)+"\\phone"):
            text = "Для оформления заказа нам нужен твой номер телефона"

            #location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
            contact_keyboard = telegram.KeyboardButton(text="Отправить контакт", request_contact=True)
            custom_keyboard = [[ contact_keyboard ]]
            markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)

            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

            return
        else:
            pass


        

        

        


        text = "Cпособ получения товара"

        keyboard = [[InlineKeyboardButton("Доставка", callback_data="delivery") , InlineKeyboardButton("Самовывоз", callback_data="self")],
                    [InlineKeyboardButton("Отмена", callback_data="cancel")]
                    ]
        markup = InlineKeyboardMarkup(keyboard)

        message = bot.sendMessage(user, text, reply_markup=markup)

        with open(users_path+str(user)+"\\temp_id", "a", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        

        return


    if "Назад" in recieved_text:
        deleteTemp(bot, user)
        bot.deleteMessage(user, update.message.message_id)


        text = "Выбери действие"

        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")
        orders.append("")

        count = len(orders) - 1
        if count!=0:
            double_text = " [{}]".format(count)
        else:
            double_text = ""

        keyboard = [["Меню"],["Корзина"+double_text]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        message = bot.sendMessage(user, text, reply_markup = markup)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        return


    if "Меню" in recieved_text:
        deleteTemp(bot, user)

        products = GetAllProducts()
        titles = products[0]

        button_list = []
        
        a = 0
        while a<len(titles):
            button_list.append(InlineKeyboardButton(titles[a], callback_data="prod " + str(a+1)))
            a += 1


        keyboard = build_menu(button_list, 2)
        markup = InlineKeyboardMarkup(keyboard)

        text = "Меню"
        
        message = bot.send_photo(chat_id=user, photo=open('menu.jpg', 'rb'), reply_markup=markup)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")
        bot.deleteMessage(user, update.message.message_id)

        return

    if "Корзина" in recieved_text:
        deleteTemp(bot, user)
        bot.deleteMessage(user, update.message.message_id)
        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")
        orders.append("")

        if len(orders)<2:

            keyboard = [["Меню"],["Корзина"]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Твоя корзина пуста"
            
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

            return
        else:

            all_products = GetAllProducts()
            titles = all_products[0]
            price = all_products[2]

            orders = []
            orders = os.listdir(users_path+str(user)+"\\Orders")

            button_list = []
            total = 0

            for a in orders:
                with open(users_path+str(user)+"\\Orders\\"+str(a),"r",encoding="utf8") as file:
                    value = file.readlines()
                    num = int(value[0].replace("\n",""))
                    quan = int(value[1].replace("\n",""))
                    total += quan*price[num-1]
                            
                    button_list.append(InlineKeyboardButton("{} - {}".format(titles[num-1],quan), callback_data="empty"))
                    button_list.append(InlineKeyboardButton(emojize("❎"), callback_data="delete {}".format(str(a))))

            keyboard = build_menu(button_list, 2)
            markup = InlineKeyboardMarkup(keyboard)
                    

            text = "Твоя корзина"
        
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")
        
            keyboard = [[ "Оформить заказ"] , ["Назад"]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Общая стоимость: {} сум".format(total)
        
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "a", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

            return
            


@send_typing_action
def Start(bot, update):

    user = update.message.from_user.id

    if not os.path.exists(users_path+str(user)):
        os.mkdir(users_path+str(user), 0o777)
        my_thread = threading.Thread(target=CreateTelegramUser, args=(user, update.message.from_user.full_name, update.message.from_user.username, "0",))
        my_thread.start()
    if not os.path.exists(users_path+str(user)+"\\Orders"):
        os.mkdir(users_path+str(user)+"\\Orders")

    text = "Привет! Это бот от Twice Spice! \n{}\n\n{}".format(config.description,"Давай подумаем, что можно сделать")
    markup = ""

    bot.sendMessage(user, text, reply_markup = markup)
    
    text = "Выбери действие"

    orders = []
    orders = os.listdir(users_path+str(user)+"\\Orders")
    orders.append("")

    count = len(orders) - 1
    if count!=0:
        double_text = " [{}]".format(count)
    else:
        double_text = ""

    keyboard = [["Меню"],["Корзина"+double_text]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    message = bot.sendMessage(user, text, reply_markup = markup)
    with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
        file.write(str(message.message_id)+"\n")
    
    
    return

@send_typing_action
def ContactHandler(bot, update):
    user = update.message.from_user.id
    contact = update.message.contact

    if user!= contact.user_id:
        text = "К большому сожалению, нужно отправить именно свой номер :)"
        markup = ""
        message = bot.sendMessage(user, text, reply_markup = markup)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        return
    else:

        file = open(users_path + str(user)+"\\phone","w")
        file.write(str(contact.phone_number).replace("+",""))
        file.close()


        text = "Отлично! Теперь мы сможем с тобой связаться"
        markup = ""
        message = bot.sendMessage(user, text, reply_markup = markup)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        text = "Cпособ получения товара"

        keyboard = [[InlineKeyboardButton("Доставка", callback_data="delivery") , InlineKeyboardButton("Самовывоз", callback_data="self")],
                    [InlineKeyboardButton("Отмена", callback_data="cancel")]
                    ]
        markup = InlineKeyboardMarkup(keyboard)

        message = bot.sendMessage(user, text, reply_markup=markup)

        with open(users_path+str(user)+"\\temp_id", "a", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")
        
    return


def check(user):
    a = 1
    while a<20: 
        if os.path.exists(users_path+str(user)+"\\Orders\\order"+str(a)):
            a += 1
        else:
            break
    return a


#@send_typing_action
def InlineKeyboardHandler(bot, update):
    user = update.callback_query.from_user.id
    recieved_text = update.callback_query.data

    if "empty" in recieved_text:
        bot.answerCallbackQuery(update.callback_query.id)
        return

    if "delete " in recieved_text:
        value = recieved_text.replace("delete ","")
        os.remove(users_path+str(user)+"\\Orders\\"+str(value))

        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")
        orders.append("")

        if len(orders)<2:
            deleteTemp(bot, user)

            orders = []
            orders = os.listdir(users_path+str(user)+"\\Orders")
            orders.append("")

            count = len(orders) - 1
            if count!=0:
                double_text = " [{}]".format(count)
            else:
                double_text = ""

            keyboard = [["Меню"],["Корзина"+double_text]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Твоя корзина пуста"
            
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

        else:

            all_products = GetAllProducts()
            titles = all_products[0]
            description = all_products[1]
            price = all_products[2]

            orders = []
            orders = os.listdir(users_path+str(user)+"\\Orders")

            button_list = []
            total = 0

            for a in orders:
                with open(users_path+str(user)+"\\Orders\\"+str(a),"r",encoding="utf8") as file:
                    value = file.readlines()
                    num = int(value[0].replace("\n",""))
                    quan = int(value[1].replace("\n",""))
                    total += quan*price[num-1]
                    
        
                    button_list.append(InlineKeyboardButton("{} - {}".format(titles[num-1],quan), callback_data="empty"))
                    button_list.append(InlineKeyboardButton(emojize("❎"), callback_data="delete {}".format(str(a))))

            keyboard = build_menu(button_list, 2)
            markup = InlineKeyboardMarkup(keyboard)
                    
            text = "Твоя корзина"
            deleteTemp1(bot, user, 1)

            message = bot.editMessageReplyMarkup(user, update.callback_query.message.message_id, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")
            
            keyboard = [[ "Оформить заказ" ] , [ "Назад" ]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Общая стоимость: {} сум".format(total)
        
            message = bot.sendMessage(user, text, reply_markup = markup, disable_notification=True)
            with open(users_path+str(user)+"\\temp_id", "a", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

            return

    if "cash" in recieved_text:
        deleteTemp(bot, user)

        with open(users_path+str(user)+"\\money", "w", encoding="utf8") as file:
            file.write("0")

        with open(users_path+str(user)+"\\delivery", "r", encoding="utf8") as file:
            value = file.read()

        if value == "0":
            phrase = ""
        else:
            phrase = "и доставлен"

        text = "Вот и все. Заказ скоро будет готов {}".format(phrase)

        bot.sendMessage(user, text)

        text = "<b>Заказ</b>\n\n"

        all_products = GetAllProducts()
        titles = all_products[0]
        description = all_products[1]
        price = all_products[2]


        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")

        for a in orders:
            with open(users_path+str(user)+"\\Orders\\"+str(a),"r",encoding="utf8") as file:
                value = file.readlines()
                num = int(value[0].replace("\n",""))
                quan = int(value[1].replace("\n",""))
                cost = int(price[num-1])

                position = "{} - {}: {} сум\n".format(quan, titles[num-1], cost)

                text = text + position

        markup = ""
        message = bot.sendMessage(user, text, reply_markup=markup, parse_mode=ParseMode.HTML)

        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")


        text = "Выбери действие"


        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")
        orders.append("")

        count = len(orders) - 1
        if count!=0:
            double_text = " [{}]".format(count)
        else:
            double_text = ""

        keyboard = [["Меню"],["Корзина"+double_text]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        message = bot.sendMessage(user, text, reply_markup = markup)

        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id) +"\n")
        return

    
    if "card" in recieved_text:
        deleteTemp(bot, user)

        with open(users_path+str(user)+"\\money", "w", encoding="utf8") as file:
            file.write("1")

        text = "Выбери платежную систему"

        keyboard = [[InlineKeyboardButton("PayMe", callback_data="payme") , InlineKeyboardButton("Click", callback_data="click")],
                    [InlineKeyboardButton("Отмена", callback_data="cancel")]
                    ]
        markup = InlineKeyboardMarkup(keyboard)

        message = bot.sendMessage(user, text, reply_markup = markup)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        return


    if "payme" in recieved_text or "click" in recieved_text:
        deleteTemp(bot, user)
        payload = recieved_text

        if payload=="payme":
            provider_token = "371317599:TEST:667663564"
        else:
            provider_token = "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"

        send_invoice(bot, update, provider_token)

        return


    if "self" in recieved_text:
        deleteTemp(bot, user)

        with open(users_path+str(user)+"\\delivery", "w", encoding="utf8") as file:
            file.write("0")

        text = "Выбери способ оплаты"

        keyboard = [[InlineKeyboardButton("Нал", callback_data="cash") , InlineKeyboardButton("Безнал", callback_data="card")],
                    [InlineKeyboardButton("Отмена", callback_data="cancel")]
                    ]
        markup = InlineKeyboardMarkup(keyboard)

        message = bot.sendMessage(user, text, reply_markup = markup)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        return

    if "delivery" in recieved_text:
        deleteTemp(bot, user)

        with open(users_path+str(user)+"\\delivery", "w", encoding="utf8") as file:
            file.write("1")

        location_keyboard = telegram.KeyboardButton(text="Отправить геолокацию", request_location=True)
        #contact_keyboard = telegram.KeyboardButton(text="Отправить контакт", request_contact=True)
        custom_keyboard = [[ location_keyboard ]]
        markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        text = "Отправь своё местоположение, чтобы мы знали куда везти"

        message = bot.sendMessage(user, text, reply_markup=markup)

        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        return

    if "cancel" in recieved_text:
        deleteTemp(bot, user)
        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")
        orders.append("")

        if len(orders)<2:

            keyboard = [["Меню"],["Корзина"]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Твоя корзина пуста"
            
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

            return
        else:

            all_products = GetAllProducts()
            titles = all_products[0]
            description = all_products[1]
            price = all_products[2]

            orders = []
            orders = os.listdir(users_path+str(user)+"\\Orders")

            button_list = []

            total = 0

            for a in orders:
                with open(users_path+str(user)+"\\Orders\\"+str(a),"r",encoding="utf8") as file:
                    value = file.readlines()
                    num = int(value[0].replace("\n",""))
                    quan = int(value[1].replace("\n",""))
                    total = quan*price[num-1]
        
                    button_list.append(InlineKeyboardButton("{} - {}".format(titles[num-1],quan), callback_data="empty"))
                    button_list.append(InlineKeyboardButton(emojize("❎"), callback_data="delete {}".format(str(a))))

            keyboard = build_menu(button_list, 2)
            markup = InlineKeyboardMarkup(keyboard)
                    

            text = "Твоя корзина"
        
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")
        
            keyboard = [[ "Оформить заказ"] , ["Назад"]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Общая стоимость: {} сум".format(total)
        
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"\\temp_id", "a", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

            return
    

    if "prod " in recieved_text:

        deleteTemp(bot, user)
        product_number = int(recieved_text.replace("prod ",""))

        all_products = GetAllProducts()
        titles = all_products[0]
        description = all_products[1]
        price = all_products[2]
        picture = all_products[3]


        with open(users_path+str(user)+"\\temp_pic", 'wb') as handle:
            response = requests.get(config.url1+str(picture[product_number-1])[1:], stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        text = "<b>" + titles[product_number-1] + "</b>\n\n{}".format(description[product_number-1])+"\n\n<b>Цена: {} сум</b>".format(price[product_number-1])
        
        keyboard = [[InlineKeyboardButton("Добавить в корзину", callback_data="add_to_cart " + str(product_number))],
                    [InlineKeyboardButton("Назад", callback_data="back_to_menu")]
                    ]
        markup = InlineKeyboardMarkup(keyboard)

        message = bot.send_photo(chat_id=user, photo=open(users_path+str(user)+"\\temp_pic", 'rb'), caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")

        return
    
    if "add_to_cart " in recieved_text:

        product_number = int(recieved_text.replace("add_to_cart ",""))
        all_products = GetAllProducts()
        titles = all_products[0]
        description = all_products[1]


        button_list = []
        
        a = 1
        while a<11:
            button_list.append(InlineKeyboardButton(a, callback_data="prod_num " + str(product_number) + " " + str(a)))
            a += 1

        keyboard = build_menu(button_list, 3)
        markup = InlineKeyboardMarkup(keyboard)

        text = "Выбери количество:"
        
        message = bot.sendMessage(user, text, reply_markup=markup)

        with open(users_path+str(user)+"\\temp_id", "a", encoding="utf8") as file:
            file.write(str(message.message_id) +"\n")

        return

    if "prod_num " in recieved_text:
        value = recieved_text.replace("prod_num", "").split()
        product_number = value[0]
        quantity = value[1]

        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")
        orders.append("")

        count = check(user)
        
        with open(users_path+str(user)+"\\Orders\\order"+str(count), "w", encoding="utf8") as file:
            file.write("{}\n{}".format(product_number, quantity))

        bot.answerCallbackQuery(update.callback_query.id, text="Заказ добавлен в корзину")
        deleteTemp(bot, user)

        text = "Выбери действие"


        orders = []
        orders = os.listdir(users_path+str(user)+"\\Orders")
        orders.append("")

        count = len(orders) - 1
        if count!=0:
            double_text = " [{}]".format(count)
        else:
            double_text = ""

        keyboard = [["Меню"],["Корзина"+double_text]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        message = bot.sendMessage(user, text, reply_markup = markup)

        with open(users_path+str(user)+"\\temp_id", "a", encoding="utf8") as file:
            file.write(str(message.message_id) +"\n")
        return

    if "back_to_menu" in recieved_text:
        deleteTemp(bot, user)

        products = GetAllProducts()
        titles = products[0]

        button_list = []
        
        a = 0
        while a<len(titles):
            button_list.append(InlineKeyboardButton(titles[a], callback_data="prod " + str(a+1)))
            a += 1


        keyboard = build_menu(button_list, 2)
        markup = InlineKeyboardMarkup(keyboard)

        text = "Меню"
        
        message = bot.send_photo(chat_id=user, photo=open('menu.jpg', 'rb'), reply_markup=markup)
        with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")
        bot.deleteMessage(user, update.message.message_id)

        return


def send_invoice(bot, update, provider_token):

    chat_id = update.callback_query.from_user.id

    orders = []
    orders = os.listdir(users_path+str(chat_id)+"\\Orders")

    prices = []

    all_products = GetAllProducts()
    titles = all_products[0]
    price = all_products[2]

    for a in orders:
        with open(users_path+str(chat_id)+"\\Orders\\"+str(a),"r",encoding="utf8") as file:
            value = file.readlines()
            num = int(value[0].replace("\n",""))
            quan = int(value[1].replace("\n",""))
            cost = int(price[num-1])

            prices.append(LabeledPrice(str(quan) + " " + titles[num-1], cost * quan * 100))


    title = "Оплата заказа"
    description = "Сервис оплаты заказов Twice Spice"
    # select a payload just for you to recognize its the donation from your bot
    payload = str(chat_id)
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    start_parameter = "test-payment"
    currency = "UZS"
    # price in dollars
    
    
    # price * 100 so as to include 2 d.p.

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    bot.send_invoice(chat_id, title, description, payload,
                             provider_token, start_parameter, currency, prices)

    return


def precheckout_callback(bot, update):
    """Пречек оплаты"""
    query = update.pre_checkout_query
    user = update.pre_checkout_query.from_user.id

    if query.invoice_payload != str(user):
        print(query.invoice_payload)
        print(user)
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                      error_message="Что-то пошло не так")
    else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)

def successful_payment_callback(bot, update):

    user = update.message.from_user.id    

    with open(users_path+str(user)+"\\delivery", "r", encoding="utf8") as file:
            value = file.read()

    if value == "0":
        phrase = ""
    else:
        phrase = "и доставлен"

    text = "Вот и все. Заказ скоро будет готов {}".format(phrase)

    bot.sendMessage(user, text)

    text = "<b>Заказ</b>\n\n"

    orders = []
    orders = os.listdir(users_path+str(user)+"\\Orders")

    products = GetAllProducts()
    titles = products[0]
    price = products[2]

    for a in orders:
        with open(users_path+str(user)+"\\Orders\\"+str(a),"r",encoding="utf8") as file:
            value = file.readlines()
            num = int(value[0].replace("\n",""))
            quan = int(value[1].replace("\n",""))
            cost = int(price[num-1])

            position = "{} - {}: {} сум\n".format(quan, titles[num-1], cost)

            text = text + position

    markup = ""
    message = bot.sendMessage(user, text, reply_markup=markup, parse_mode=ParseMode.HTML)

    with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
        file.write(str(message.message_id)+"\n")


    text = "Выбери действие"


    orders = []
    orders = os.listdir(users_path+str(user)+"\\Orders")
    orders.append("")

    count = len(orders) - 1
    if count!=0:
        double_text = " [{}]".format(count)
    else:
        double_text = ""

    keyboard = [["Меню"],["Корзина"+double_text]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    message = bot.sendMessage(user, text, reply_markup = markup)

    with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
        file.write(str(message.message_id) +"\n")
    return
        
def LocationHandler(bot, update):
    user = update.message.from_user.id
    location = update.message.location

    longitude = location.longitude
    latitude = location.latitude

    with open(users_path+str(user)+"\\location", "w", encoding="utf8") as file:
        file.write("{}\n{}\n".format(longitude, latitude))

    markup = ""

    text = "Отлично! Теперь выбери способ оплаты"
    keyboard = [[InlineKeyboardButton("Нал", callback_data="cash") , InlineKeyboardButton("Безнал", callback_data="card")],
                    [InlineKeyboardButton("Отмена", callback_data="cancel")]
                    ]
    markup = InlineKeyboardMarkup(keyboard)

    message = bot.sendMessage(user, text, reply_markup = markup)
    with open(users_path+str(user)+"\\temp_id", "w", encoding="utf8") as file:
        file.write(str(message.message_id)+"\n")

    return


def Error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    print("Modules imported")

if __name__ == '__main__':
    main()