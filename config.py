
import telebot
from database import db
import datetime
import threading
import os
import re
from dotenv import load_dotenv
load_dotenv()

ADMIN = []
TOKEN = os.getenv("TOKEN")
admin_env = os.getenv("ADMIN")
URL = os.getenv("URL")
DEBUG = (os.getenv("DEBUG") == 'True')

if admin_env == None:
    print("\u001b[31mCannot read ADMIN IDs from environment variable file. Create ADMIN variable in .env file")
else:
    ADMIN = [int(i) for i in admin_env.split(' ')]
if URL == None:
    print("\u001b[31mCannot read TOKEN from environment variable file. Create URL variable in .env file")
if TOKEN==None:
    print("\u001b[36mCannot read TOKEN from environment variable file. Create TOKEN in .env file")

bot = telebot.TeleBot(TOKEN, threaded=True, skip_pending=True)

############################################################ MARKUPS

register_markup = telebot.types.InlineKeyboardMarkup()
register_button = telebot.types.InlineKeyboardButton(text="✅ Register", callback_data="register_member")
register_markup.add(register_button)

force_reply = telebot.types.ForceReply()

dashboard_markup = telebot.types.InlineKeyboardMarkup()
dashboard_button = telebot.types.InlineKeyboardButton(text="📊 Dashboard", callback_data="dashboard")
dashboard_markup.add(dashboard_button)

dashview_markup = telebot.types.InlineKeyboardMarkup()
u_btn = telebot.types.InlineKeyboardButton("✏️ Change Username", callback_data="input_user")
e_btn = telebot.types.InlineKeyboardButton("📊 Engagement", callback_data="engagement")
w_btn = telebot.types.InlineKeyboardButton("⚠️ Warnings", callback_data="warns")
dashview_markup.add(u_btn)
dashview_markup.add(e_btn, w_btn)
