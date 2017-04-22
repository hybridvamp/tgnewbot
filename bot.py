#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import json
import logging
import os
import subprocess

import time

import sys

from telegram import ChatAction
from telegram.ext import CommandHandler
from telegram.ext import Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('bot.ini')

updater = Updater(token=config['KEYS']['bot_api'])
path = config['PATH']['path']
sudo_users = json.loads(config['ADMIN']['sudo'])
dispatcher = updater.dispatcher

def build(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Building")
        os.chdir(path)
        build_command = ['./scripts/bacon.sh']
        subprocess.call(build_command)
        if os.path.exists("/tmp/randomness-bacon.zip"):
        	bot.sendMessage(chat_id=update.message.chat_id,
        					text="Build done, use /upload if you want zip")
        else:
        	bot.sendMessage(chat_id=update.message.chat_id,
        					text="RIP, Build failed LMAO")
    else:
        sendNotAuthorizedMessage(bot, update)

def upload(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                            action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Uploading to the chat")
        filename = "/tmp/randomness-bacon.zip"
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot,update)

def restart(bot, update):
    if isAuthorized(update):
         bot.sendMessage(update.message.chat_id, "Bot is restarting...")
         time.sleep(0.2)
         os.execl(sys.executable, sys.executable, *sys.argv)
    else:
         sendNotAuthorizedMessage()

def leave(bot, update):
	if isAuthorized(update):
		bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
		bot.sendMessage(update.message.chat_id, "Goodbye!")
		bot.leaveChat(update.message.chat_id)
	else:
		sendNotAuthorizedMessage(bot, update)


def sendNotAuthorizedMessage(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                        action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="You aren't authorized for this lulz @" + update.message.from_user.username)

def derp(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id,
						action=ChatAction.TYPING)
	bot.sendMessage(chat_id=update.message.chat_id,
					text="@" + update.message.from_user.username + " staph durpeeng")

def pizza(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id,
						action=ChatAction.TYPING)
	bot.sendMessage(chat_id=update.message.chat_id,
				text="Somone give @" + update.message.from_user.username + " pizza pl0x")

def help(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id,
						action=ChatAction.TYPING)
	bot.sendMessage(chat_id=update.message.chat_id,
				text="@" + update.message.from_user.username + ", here is some help for you.\n/build,\n/upload,\n/derp,\n/pizzaplz,\n/mml,\n/lazyaf,\n/restart,\n/leave, and\n/help for this menu.")

def lazy(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id,
						action=ChatAction.TYPING)
	bot.sendMessage(chat_id=update.message.chat_id,
						text="@" +  update.message.from_user.username + " is too lazy to do whatever he/she was told to do!")

def mml(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id,
						action=ChatAction.TYPING)
	bot.sendMessage(chat_id=update.message.chat_id,
						text="No u @" + update.message.from_user.username)

def isAuthorized(update):
	return update.message.from_user.id in sudo_users

buildHandler = CommandHandler('build', build)
uploadHandler = CommandHandler('upload', upload)
restartHandler = CommandHandler('restart', restart)
leaveHandler = CommandHandler('leave', leave)
derpHandler = CommandHandler('derp', derp)
pizzaHandler = CommandHandler('pizzaplz', pizza)
helpHandler = CommandHandler('help', help)
lazyHandler = CommandHandler('lazyaf', lazy)
mmlHandler = CommandHandler('mml', mml)

dispatcher.add_handler(buildHandler)
dispatcher.add_handler(uploadHandler)
dispatcher.add_handler(restartHandler)
dispatcher.add_handler(leaveHandler)
dispatcher.add_handler(derpHandler)
dispatcher.add_handler(pizzaHandler)
dispatcher.add_handler(helpHandler)
dispatcher.add_handler(lazyHandler)
dispatcher.add_handler(mmlHandler)

updater.start_polling()
updater.idle()
