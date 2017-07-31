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
from telegram.ext import Filters
from telegram.ext import MessageHandler
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

logfile = '/home/akhil/Kronicbot/log'

def build(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        os.chdir(path)
        bot.sendMessage(update.message.chat_id, "Building!")
        os.system('bash aosip.sh %s %s' % (update.message.chat_id, update.message.text))
    else:
        sendNotAuthorizedMessage(bot, update)

def sync(bot, update):
    if isAuthorized(update):
        bot.sendMessage(update.message.chat_id, text="Starting repo sync")
        os.system("bash ~/Kronicbot/sync.sh %s" % update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot, update)

def pick(bot, update):
    if isAuthorized(update):
        bot.sendMessage(update.message.chat_id, text="Picking stuff")
        os.system("bash ~/Kronicbot/pick.sh %s %s" % (update.message.chat_id, update.message.text))
    else:
        sendNotAuthorizedMessage(bot, update)

def clean(bot, update):
    if isAuthorized(update):
        bot.sendMessage(update.message.chat_id, text="Cleaning")
        os.system("bash ~/Kronicbot/clean.sh %s" % update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot, update)

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
    bot.sendMessage(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                    text="You aren't authorized for this lulz!")

def help(bot, update):
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id,
        text="I've sent you help via PM @" + update.message.from_user.username + ".")
    bot.sendMessage(update.message.from_user.id,
        text="Here is some help for you.\n/build,\n/upload,\n/restart,\n/leave, and\n/help for this menu.")


def isAuthorized(update):
    return update.message.from_user.id in sudo_users

def pull(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Fetching remote repo")
        subprocess.call(['git', 'fetch', 'origin', 'master', '--force'])
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Resetting to latest commit")
        subprocess.call(['git', 'reset', '--hard', 'origin/master'])
        restart(bot, update)
    else:
        sendNotAuthorizedMessage(bot, update)

def push(bot, update):
    if isAuthorized(update):
        subprocess.call(['git', 'push', 'origin', 'master', '--force'])
        bot.sendMessage(update.message.chat_id, text="K pushed")
    else:
        sendNotAuthorizedMessage(bot, update)

def id(bot, update):
    chatid=str(update.message.chat_id)
    try:
        username=str(update.message.reply_to_message.from_user.username)
        userid=str(update.message.reply_to_message.from_user.id)
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        time.sleep(1)
        bot.sendMessage(update.message.chat_id, text="ID of @" + username + " is " +userid, reply_to_message_id=update.message.reply_to_message.message_id)
    except AttributeError:
        bot.sendMessage(update.message.chat_id, text="ID of this group is " + chatid, reply_to_message_id=update.message.message_id)

def trigger_characters(bot, update):
    try:
        msg=str(update.message.text).lower()
        if msg[0]=='!':
            mod_command=msg.replace("!", "")
            eval(mod_command)(bot, update)
        elif msg[0]=='#':
            mod_command=msg.replace("#", "")
            eval(mod_command)(bot, update)
    except UnicodeEncodeError:
        pass
    except NameError:
        pass

def get_admin_ids(bot, chat_id):
    return [admin.user.id for admin in bot.getChatAdministrators(chat_id)]

def kick(bot, update):
    if update.message.from_user.id in get_admin_ids(bot, update.message.chat_id):
        bot.kickChatMember(update.message.chat_id, update.message.reply_to_message.from_user.id)
    else:
        update.message.reply_text("Meh")

def shrug(bot, update):
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    time.sleep(1)
    bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="¯\_(ツ)_/¯")

def mirror(bot, update):
    if isAuthorized(update):
        msg=update.message.text
        link=msg.split(' ')[1]
        file=msg.split(' ')[2]
        output='upload/' + file
        subprocess.call(['wget', link, '-O', output])
        bot.sendDocument(update.message.chat_id, open(output, 'rb'))
        os.chdir('/home/akhil/Kronicbot/upload')
        subprocess.call(['rm', '-rfv', file])
        os.chdir('/home/akhil/Kronicbot/')
    else:
        sendNotAuthorizedMessage(bot, update)

def clearlog(bot, update):
    if isAuthorized(update):
        subprocess.call(['rm', '-fv', logfile])
        bot.sendMessage(update.message.chat_id, "Cleared logs.")

def getlog(bot, update):
    bot.sendDocument(update.message.chat_id, open(logfile, 'rb'))


buildHandler = CommandHandler('build', build)
restartHandler = CommandHandler('restart', restart)
leaveHandler = CommandHandler('leave', leave)
helpHandler = CommandHandler('help', help)
idHandler = CommandHandler('id', id)
pullHandler = CommandHandler('pull', pull)
pushHandler = CommandHandler('push', push)
idHandler = CommandHandler('id', id)
kickHandler = CommandHandler('kick', kick)
shrugHandler = CommandHandler('shrug', shrug)
syncHandler = CommandHandler('sync', sync)
pickHandler = CommandHandler('pick', pick)
cleanHandler = CommandHandler('clean', clean)

dispatcher.add_handler(buildHandler)
dispatcher.add_handler(restartHandler)
dispatcher.add_handler(leaveHandler)
dispatcher.add_handler(helpHandler)
dispatcher.add_handler(idHandler)
dispatcher.add_handler(pullHandler)
dispatcher.add_handler(pushHandler)
dispatcher.add_handler(idHandler)
dispatcher.add_handler(kickHandler)
dispatcher.add_handler(shrugHandler)
dispatcher.add_handler(syncHandler)
dispatcher.add_handler(pickHandler)
dispatcher.add_handler(cleanHandler)
dispatcher.add_handler(MessageHandler(Filters.text, trigger_characters))

updater.start_polling()
updater.idle()
