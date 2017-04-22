#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import json
import logging
import os
import subprocess

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
    if update.message.from_user.id in sudo_users:
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
    if update.message.from_user.id in sudo_users:
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

def sendNotAuthorizedMessage(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                        action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="You aren't authorized for this lulz")

def derp(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id,
						action=ChatAction.TYPING)
	bot.sendMessage(chat_id=update.message.chat_id,
					text="Staph durpeeng")

def pizza(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id,
						action=ChatAction.TYPING)
	bot.sendMessage(chat_id=update.message.chat_id,
					text="@akhilnarang, stop eating so much pizza")

def kick(bot, update):
	if update.message.from_user.id not in sudo_users:
		bot.sendMessage(update.message.chat_id,
						text="y u wanna kick him :(")
	else:
		bot.sendMessage(update.message.chat_id,
						text="Someone gib Akhil pizza and I'll do it")

buildHandler = CommandHandler('build', build)
uploadHandler = CommandHandler('upload', upload)
derpHandler = CommandHandler('derp', derp)
kickHandler = CommandHandler('kick', kick)
pizzaHandler = CommandHandler('pizza', pizza)


dispatcher.add_handler(buildHandler)
dispatcher.add_handler(uploadHandler)
dispatcher.add_handler(derpHandler)
dispatcher.add_handler(kickHandler)
dispatcher.add_handler(pizzaHandler)

updater.start_polling()
updater.idle()
