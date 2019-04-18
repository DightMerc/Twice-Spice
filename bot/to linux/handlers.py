from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

import telegram

import logging
import config
from functools import wraps

import datetime
import os
from client import Client
import threading
from telegram import ParseMode

from emoji import emojize

users_path = os.getcwd() + "/Users/"

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
    for a in products_payload:
        prod_title.append(a.title)
        prod_description.append(a.description)
    
    product_list.append(prod_title)
    product_list.append(prod_description)



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
        with open(users_path+str(user)+"/temp_id", "r", encoding="utf8") as file:
            value = file.readlines()
            for a in value:
                temp_id = int(a.replace("\n",""))
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
        with open(users_path+str(user)+"/temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")
        bot.deleteMessage(user, update.message.message_id)

        return

    if "Корзина" in recieved_text:
        bot.deleteMessage(user, update.message.message_id)
        deleteTemp(bot, user)
        orders = []
        orders = os.listdir(users_path+str(user)+"/Orders")
        orders.append("")

        if len(orders)<2:
            orders = []
            orders = os.listdir(users_path+str(user)+"/Orders")
            orders.append("")

            count = len(orders) - 1
            if count!=0:
                double_text = " [{}]".format(count)
            else:
                double_text = ""

            keyboard = [["Меню"],["Корзина"+double_text]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Ваша корзина пуста"
            
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"/temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")
        else:

            all_products = GetAllProducts()
            titles = all_products[0]
            description = all_products[1]

            orders = []
            orders = os.listdir(users_path+str(user)+"/Orders")

            button_list = []

            for a in orders:
                with open(users_path+str(user)+"/Orders/"+str(a),"r",encoding="utf8") as file:
                    value = file.readlines()
                    num = int(value[0].replace("\n",""))
                    quan = int(value[1].replace("\n",""))
        
                    button_list.append(InlineKeyboardButton("{} - {}".format(titles[num-1],quan), callback_data="empty"))
                    button_list.append(InlineKeyboardButton(emojize("❎"), callback_data="delete {}".format(str(a))))

                    keyboard = build_menu(button_list, 2)
                    markup = InlineKeyboardMarkup(keyboard)
                    

            text = "Ваша корзина"

        
        message = bot.sendMessage(user, text, reply_markup = markup)
        with open(users_path+str(user)+"/temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")
    
        return
        


@send_typing_action
def Start(bot, update):

    user = update.message.from_user.id

    if not os.path.exists(users_path+str(user)):
        os.mkdir(users_path+str(user), 0o777)
        my_thread = threading.Thread(target=CreateTelegramUser, args=(user, update.message.from_user.full_name, update.message.from_user.username, "0",))
        my_thread.start()
    if not os.path.exists(users_path+str(user)+"/Orders"):
        os.mkdir(users_path+str(user)+"/Orders")

    text = "Привет! Это бот от Twice Spice! \n{}\n\n{}".format(config.description,"Давай подумаем, что можно сделать")
    
    orders = []
    orders = os.listdir(users_path+str(user)+"/Orders")
    orders.append("")

    count = len(orders) - 1
    if count!=0:
        double_text = " [{}]".format(count)
    else:
        double_text = ""

    keyboard = [["Меню"],["Корзина"+double_text]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    bot.sendMessage(user, text, reply_markup = markup)
    
    return

@send_typing_action
def ContactHandler(bot, update):
    """
    user = update.message.from_user.id
    contact = update.message.contact

    if user!= contact.user_id:
        bot.sendMessage(user, "К большому сожалению, нужно отправить именно свой номер :)")
    else:

        file = open(users_path + str(user)+"/phone_number.cfg","w")
        file.write(contact.phone_number)
        file.close()

        text = "Регистрация завершена. Теперь вы можете отправить контрольные данные для получения Ключа Активации"

        keyboard = [[ "СТРЕЛЬНУТЬ" ]]
        markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        bot.sendMessage(user, text, markup)
        
    return
    """
    pass


#@send_typing_action
def InlineKeyboardHandler(bot, update):
    user = update.callback_query.from_user.id
    recieved_text = update.callback_query.data


    if "empty" in recieved_text:
        bot.answerCallbackQuery(update.callback_query.id)
        return

    if "delete " in recieved_text:
        value = recieved_text.replace("delete ","")
        os.remove(users_path+str(user)+"/Orders/"+str(value))

        orders = []
        orders = os.listdir(users_path+str(user)+"/Orders")
        orders.append("")

        if len(orders)<2:
            deleteTemp(bot, user)

            orders = []
            orders = os.listdir(users_path+str(user)+"/Orders")
            orders.append("")

            count = len(orders) - 1
            if count!=0:
                double_text = " [{}]".format(count)
            else:
                double_text = ""

            keyboard = [["Меню"],["Корзина"+double_text]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            text = "Ваша корзина пуста"
            
            message = bot.sendMessage(user, text, reply_markup = markup)
            with open(users_path+str(user)+"/temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

        else:

            all_products = GetAllProducts()
            titles = all_products[0]
            description = all_products[1]

            orders = []
            orders = os.listdir(users_path+str(user)+"/Orders")

            button_list = []

            for a in orders:
                with open(users_path+str(user)+"/Orders/"+str(a),"r",encoding="utf8") as file:
                    value = file.readlines()
                    num = int(value[0].replace("\n",""))
                    quan = int(value[1].replace("\n",""))
        
                    button_list.append(InlineKeyboardButton("{} - {}".format(titles[num-1],quan), callback_data="empty"))
                    button_list.append(InlineKeyboardButton(emojize("❎"), callback_data="delete {}".format(str(a))))

                    keyboard = build_menu(button_list, 2)
                    markup = InlineKeyboardMarkup(keyboard)
                    

            text = "Ваша корзина"

        
            message = bot.editMessageReplyMarkup(user, update.callback_query.message.message_id, reply_markup = markup)
            with open(users_path+str(user)+"/temp_id", "w", encoding="utf8") as file:
                file.write(str(message.message_id)+"\n")

            return

        

    if "prod " in recieved_text:

        deleteTemp(bot, user)
        product_number = int(recieved_text.replace("prod ",""))

        all_products = GetAllProducts()
        titles = all_products[0]
        description = all_products[1]

        text = "<b>" + titles[product_number-1] + "</b>\n\n{}".format(description[product_number-1])+"\n\n<b>Цена: 50 000 сум</b>"
        
        keyboard = [[InlineKeyboardButton("Добавить в корзину", callback_data="add_to_cart " + str(product_number))],
                    [InlineKeyboardButton("Назад", callback_data="back_to_menu")]
                    ]
        markup = InlineKeyboardMarkup(keyboard)

        message = bot.send_photo(chat_id=user, photo=open('roll.jpg', 'rb'), caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
        with open(users_path+str(user)+"/temp_id", "w", encoding="utf8") as file:
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

        text = "Выберите количество:"
        
        message = bot.sendMessage(user, text, reply_markup=markup)

        with open(users_path+str(user)+"/temp_id", "a", encoding="utf8") as file:
            file.write(str(message.message_id) +"\n")

        return

    if "prod_num " in recieved_text:
        value = recieved_text.replace("prod_num", "").split()
        product_number = value[0]
        quantity = value[1]

        orders = []
        orders = os.listdir(users_path+str(user)+"/Orders")
        orders.append("")

        count = len(orders)

        with open(users_path+str(user)+"/Orders/order"+str(count), "w", encoding="utf8") as file:
            file.write("{}\n{}".format(product_number, quantity))

        bot.answerCallbackQuery(update.callback_query.id, text="Заказ добавлен в корзину")
        deleteTemp(bot, user)

        text = "Выбери действие"


        orders = []
        orders = os.listdir(users_path+str(user)+"/Orders")
        orders.append("")

        count = len(orders) - 1
        if count!=0:
            double_text = " [{}]".format(count)
        else:
            double_text = ""

        keyboard = [["Меню"],["Корзина"+double_text]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        message = bot.sendMessage(user, text, reply_markup = markup)

        with open(users_path+str(user)+"/temp_id", "a", encoding="utf8") as file:
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
        with open(users_path+str(user)+"/temp_id", "w", encoding="utf8") as file:
            file.write(str(message.message_id)+"\n")
        bot.deleteMessage(user, update.message.message_id)

        return
        


def Error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    print("Modules imported")

if __name__ == '__main__':
    main()