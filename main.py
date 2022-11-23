#!/usr/bin/python3
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram.ext import CallbackContext
from telegram import Update
import logging
from telegram.ext import Updater
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import requests

'''
变量填写区
'''
misskey_url = ""
misskey_token = ""
tg_token = ""

'''
变量填写结束
'''

updater = Updater(
    token=tg_token, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

is_allowed = True


def refresh():
    global is_allowed
    is_allowed = True


# 北京时间每天 0 点刷新
scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(refresh, 'cron', hour=18, minute='0')
scheduler.start()


def get_invite_code():
    r = requests.post(misskey_url+'/api/admin/invite',
                      json={"i": misskey_token})
    value = r.json()
    return value['code']


def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    if is_allowed:
        context.bot.send_message(
            chat_id=user['id'], text="问题：UTC 时区现在几号？（请输入数字）")
        context.bot.send_message(
            chat_id=user['id'], text="提示：UTC 时区比北京时间慢 8 个小时")
    else:
        context.bot.send_message(
            chat_id=user['id'], text="今日邀请码发放已达到上限")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def verify(update: Update, context: CallbackContext):
    user = update.message.from_user
    global is_allowed
    if is_allowed:
        if update.message.text == datetime.now(timezone.utc).strftime("%d"):
            context.bot.send_message(chat_id=user['id'], text="验证通过")
            context.bot.send_message(
                chat_id=user['id'], text="邀请码为 "+get_invite_code())
            is_allowed = False
        else:
            context.bot.send_message(chat_id=user['id'], text="回答错误")
    else:
        context.bot.send_message(
            chat_id=user['id'], text="今日邀请码发放已达到上限")


verify_handler = MessageHandler(Filters.text & (~Filters.command), verify)
dispatcher.add_handler(verify_handler)

updater.start_polling()