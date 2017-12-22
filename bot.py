#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import json
import logging
import os
import subprocess

import time

import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, ChatAction, InputTextMessageContent
from uuid import uuid4

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('bot.ini')

updater = Updater(token=config['KEYS']['bot_api'])
path = config['PATH']['path']
sudo_users = [138554855,92027269]
dispatcher = updater.dispatcher

def build(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        os.chdir(path)
        bot.sendMessage(update.message.chat_id, "Building!")
        os.system('cd ~/src && bash aosip.sh %s %s' % (update.message.chat_id, update.message.text))
        bot.sendMessage(update.message.chat_id, "Build is done, bot is usable again!")
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

def inlinequery(bot, update):
    query = update.inline_query.query
    o = execute(query, update, direct=False)
    results = list()

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title=query,
                                            description=o,
                                            input_message_content=InputTextMessageContent(
                                                '*{0}*\n\n{1}'.format(query, o),
                                                parse_mode="Markdown")))

    bot.answerInlineQuery(update.inline_query.id, results=results, cache_time=10)

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
    chat=update.message.chat_id
    try:
        sender=update.message.from_user.id
        quoted=update.message.reply_to_message.from_user.id
        if sender in get_admin_ids(bot, chat) and quoted not in get_admin_ids(bot, chat):
            bot.kickChatMember(chat, quoted)
            bot.unbanChatMember(chat, quoted)
            update.message.reply_text(update.message.reply_to_message.from_user.first_name+ " kicked!")
        else:
            update.message.reply_text("Meh, either you're not an admin or the quoted user is one!")
    except AttributeError:
            update.message.reply_text(reply_to_message_id=update.message.message_id, text="Please quote a user to kick!")

def ban(bot, update):
    chat=update.message.chat_id
    try:
        sender=update.message.from_user.id
        quoted=update.message.reply_to_message.from_user.id
        if sender in get_admin_ids(bot, chat) and quoted not in get_admin_ids(bot, chat):
            bot.kickChatMember(chat, quoted)
            update.message.reply_text(update.message.reply_to_message.from_user.first_name+ " cannot join back now!")
        else:
            update.message.reply_text("Meh, either you're not an admin or the quoted user is one!")
    except AttributeError:
            update.message.reply_text(reply_to_message_id=update.message.message_id, text="Please quote a user to ban!")

def unban(bot, update):
    chat=update.message.chat_id
    try:
        sender=update.message.from_user.id
        quoted=update.message.reply_to_message.from_user.id
        if sender in get_admin_ids(bot, chat) and quoted not in get_admin_ids(bot, chat):
            bot.unbanChatMember(chat, quoted)
            update.message.reply_text(update.message.reply_to_message.from_user.first_name+ " can join this chat now!")
        else:
            update.message.reply_text("Meh, either you're not an admin or the quoted user is one!")
    except AttributeError:
            update.message.reply_text(reply_to_message_id=update.message.message_id, text="Please quote a user to unban!")

def mute(bot, update):
    chat=update.message.chat_id
    try:
        sender=update.message.from_user.id
        quoted=update.message.reply_to_message.from_user.id
        if sender in get_admin_ids(bot, chat) and quoted not in get_admin_ids(bot, chat):
            bot.restrictChatMember(chat, quoted, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
            update.message.reply_text(update.message.reply_to_message.from_user.first_name+ " cannot speak now!")
        else:
            update.message.reply_text("Meh, either you're not an admin or the quoted user is one!")
    except AttributeError:
            update.message.reply_text(reply_to_message_id=update.message.message_id, text="Please quote a user to mute!")

def unmute(bot, update):
    chat=update.message.chat_id
    try:
        sender=update.message.from_user.id
        quoted=update.message.reply_to_message.from_user.id
        if sender in get_admin_ids(bot, chat) and quoted not in get_admin_ids(bot, chat):
            bot.restrictChatMember(chat, quoted, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
            update.message.reply_text(update.message.reply_to_message.from_user.first_name+ " can speak now!")
        else:
            update.message.reply_text("Meh, either you're not an admin or the quoted user is one!")
    except AttributeError:
            update.message.reply_text(reply_to_message_id=update.message.message_id, text="Please quote a user to unmute!")

def shrug(bot, update):
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    time.sleep(1)
    bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="¯\_(ツ)_/¯")

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
banHandler = CommandHandler('ban', ban)
unbanHandler = CommandHandler('unban', unban)
muteHandler = CommandHandler('mute', mute)
unmuteHandler = CommandHandler('unmute', unmute)

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
dispatcher.add_handler(banHandler)
dispatcher.add_handler(unbanHandler)
dispatcher.add_handler(muteHandler)
dispatcher.add_handler(unmuteHandler)
dispatcher.add_handler(InlineQueryHandler(inlinequery))

updater.start_polling()
updater.idle()
