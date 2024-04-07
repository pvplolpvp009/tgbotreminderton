import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import time, threading


#output:
#Thu Dec 22 14:46:08 2011
#Thu Dec 22 14:46:18 2011
#Thu Dec 22 14:46:28 2011
#Thu Dec 22 14:46:38 2011

# Замените 'YOUR_BOT_TOKEN' на ваш токен бота
bot = telebot.TeleBot('1114064755:AAH0JClVbZndca_pulo-JV5lHn0cElJgpc8')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    price_button = InlineKeyboardButton("Текущая цена", callback_data="price")
    subscribe_button = InlineKeyboardButton("Подписаться на рассылку", callback_data="subscribe")
    markup.add(price_button, subscribe_button)

    bot.reply_to(message, "Привет! Я бот. Как я могу помочь?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "price":
        bot.send_message(call.message.chat.id, "Нажми -> /price")
    elif call.data == "subscribe":
        bot.send_message(call.message.chat.id, "Нажми -> /subscribe")

@bot.message_handler(commands=['subscribe'])
def subscribe_user(message):
    user_id = message.from_user.id
    with open('subscribers.txt', 'r') as file:
        existing_users = set(line.strip() for line in file)
        if str(user_id) in existing_users:
            bot.reply_to(message, "Вы уже подписаны!")
        else:
            with open('subscribers.txt', 'a') as file:
                file.write(f"{user_id}\n")
            bot.reply_to(message, "Вы успешно подписались на рассылку! Бот присылает уведомление каждые 60 минут.")

@bot.message_handler(commands=['price'])
def show_toncoin_price(message):
    url = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"  # Замените на ваш URL
    response = requests.get(url)
    data = json.loads(response.text)
    toncoin_price = data['rates']['TON']['prices']['USD']
    toncoin_change_24h = data['rates']['TON']['diff_24h']['USD']

    bot.reply_to(message, f"Текущая цена TonCoin: ${toncoin_price:.5f}, {toncoin_change_24h} за последние сутки")

def send_toncoin_price():
    url = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"  # Замените на ваш URL
    response = requests.get(url)
    data = json.loads(response.text)
    toncoin_price = data['rates']['TON']['prices']['USD']
    toncoin_change_24h = data['rates']['TON']['diff_24h']['USD']

    with open("subscribers.txt") as file_in:
        subscribers = []
        for line in file_in:
            subscribers.append(line)  # Загрузите список подписчиков из файла 'subscribers.txt'
    for user_id in subscribers:
        message = f"Текущая цена TonCoin: ${toncoin_price:.5f}, {toncoin_change_24h} за последние сутки"
        bot.send_message(user_id, message)
    threading.Timer(3600, send_toncoin_price).start()

send_toncoin_price()

# Запуск бота
bot.polling()
