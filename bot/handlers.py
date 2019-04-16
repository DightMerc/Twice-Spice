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



users_path = os.getcwd() + "\\Users\\"


def CreateTelegramUser(user, full_name, username, phone):

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

    return cli.GetAllProducts()


def send_typing_action(func):

    @wraps(func)
    def command_func(*args, **kwargs):
        bot, update = args
        bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(bot, update, **kwargs)

    return command_func


@send_typing_action
def start(bot, update):

    user = update.message.from_user.id

    if not os.path.exists(users_path+str(user)):
        os.mkdir(users_path+str(user), 0o777)

    text = "Привет! Это бот от Twice Spice! \n{}".format(config.description)
    bot.sendMessage(user, text)

    print("Creating new user...", end = " ")
    my_thread = threading.Thread(target=CreateTelegramUser, args=(user, update.message.from_user.full_name, update.message.from_user.username, "0",))
    my_thread.start()
    
    return

@send_typing_action
def contact_handler(bot, update):
    """
    user = update.message.from_user.id
    contact = update.message.contact

    if user!= contact.user_id:
        bot.sendMessage(user, "К большому сожалению, нужно отправить именно свой номер :)")
    else:

        file = open(users_path + str(user)+"\\phone_number.cfg","w")
        file.write(contact.phone_number)
        file.close()

        text = "Регистрация завершена. Теперь вы можете отправить контрольные данные для получения Ключа Активации"

        keyboard = [[ "СТРЕЛЬНУТЬ" ]]
        markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        bot.sendMessage(user, text, markup)
        
    return
    """
    pass


@send_typing_action
def InlineKeyboardHandler(bot, update):
    user = update.callback_query.from_user.id
    recieved_text = update.callback_query.data

    



def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)