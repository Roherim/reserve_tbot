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
    markup.add(types.InlineKeyboardButton("Забронировать", callback_data='create_reserw'))
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
   



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'get_reserws':
        new_reserve = {'chat_id': call.message.chat.id}
        data = get_reserws(call.message.chat.id)
        sending_data = ',\n'.join([f'столик в ресторане по адресу {i['address']}, на: {datetime.datetime.strftime(i["time"], "%d.%m.%Y %H:%M")}, имя: {i["name"]}' for i in data['res']])
        bot.send_message(call.message.chat.id, f'Ваши бронирования: {sending_data}')
    elif call.data =='create_reserw':
        markup = types.InlineKeyboardMarkup()
        for address in config.ADDRESSES:
            markup.add(types.InlineKeyboardButton(address, callback_data=address))
        bot.send_message(call.message.chat.id, 'Выберите ресторан', reply_markup=markup)
    elif call.data in config.ADDRESSES:


def change_data(data):
    return data

def get_reserws(user_id):
    if DEBUG:
        return {'err':None, 'status_code':200, 'res':[{'time': datetime.datetime.now()+ datetime.timedelta(days=3),
                                                        'name': 'Иван',
                                                          'address': 'ул. Ленина, д. 1'},
                                                       {'time': datetime.datetime.now()+ datetime.timedelta(days=21),
                                                         'name': 'Иван',
                                                           'address': 'ул. Ленина, д. 1'}]}
    response = requests.get(config.GET_RESERVATION_URL, params={'user_id': user_id})
    if response.status_code == 200:
        return response.json()
    return None

def add_reserws(user_id, address,date, time):
    if DEBUG:
        return {'err':None, 'status_code':200}
    response = requests.post(config.ADD_RESERVATION_URL, json={'user_id': user_id, 'address': address, 'date': date, 'time': time})
    if response.status_code == 200:
        return response.json()
    return None





bot.polling(non_stop=True)