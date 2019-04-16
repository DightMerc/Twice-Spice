#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Empty Project Bot from Dight with Love

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

from handlers import start, contact_handler, 



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)




def main():
    print(str(datetime.datetime.now()) + " " + config.name + " Bot started...")

    if not os.path.exists(users_path):
        os.mkdir(users_path, 0o777)
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    
    # log all errors
    dispatcher.add_error_handler(error)

    #Command Handler
    dispatcher.add_handler(CommandHandler("start", start))

    #Contact Handler
    dispatcher.add_handler(MessageHandler(Filters.contact,contact_handler))

    dispatcher.add_handler(CallbackQueryHandler(InlineKeyboardHandler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()