import telebot
import requests
from telebot import types
import config
import json
import datetime

bot = telebot.TeleBot("7896735623:AAFuA-tW8Rzh56HRyTbrVw8xnhji4oRWaUk")

DEBUG = True


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Получить бронирования", callback_data='get_reserws'))
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
   



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'get_reserws':
        data = get_reserws(call.message.chat.id)
        sending_data = ',\n'.join([f'время: {i["time"]}, имя: {i["name"]}' for i in data])
        bot.send_message(call.message.chat.id, f'Ваши бронирования: {sending_data}')
        


def get_reserws(user_id):
    if DEBUG:
        return [{'time': datetime.datetime.now(), 'name': 'name1'}, {'time': datetime.datetime.now()- datetime.timedelta(days=1), 'name': 'name2'}]
    response = requests.get(config.GET_RESERVATION_URL, params={'user_id': user_id})
    if response.status_code == 200:
        return response.json()
    return None



bot.polling(non_stop=True)