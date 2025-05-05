import telebot
import requests
from telebot import types
import config
import json
import datetime

bot = telebot.TeleBot("7896735623:AAFuA-tW8Rzh56HRyTbrVw8xnhji4oRWaUk")

DEBUG = True

active_reservations = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Получить бронирования", callback_data='get_reserws'))
    markup.add(types.InlineKeyboardButton("Забронировать", callback_data='create_reserw'))
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
   



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in active_reservations:
        active_reservations[chat_id] = {}

    if call.data == 'get_reserws':
        data = get_reserws(chat_id)
        if data and data.get('status_code') == 200:
            sending_data = ',\n'.join([f'столик в ресторане по адресу {i["address"]}, на: {datetime.datetime.strftime(i["time"], "%d.%m.%Y %H:%M:%S")}, имя: {i["name"]}' for i in data['res']])
            bot.send_message(chat_id, f'Ваши бронирования: {sending_data}' if sending_data else 'У вас нет бронирований')
        else:
            bot.send_message(chat_id, 'Ошибка при получении бронирований')

    elif call.data == 'create_reserw':
        markup = types.InlineKeyboardMarkup()
        for address in config.ADDRESSES:
            markup.add(types.InlineKeyboardButton(address, callback_data=address))
        bot.send_message(chat_id, 'Выберите ресторан', reply_markup=markup)

    elif call.data in config.ADDRESSES:
        active_reservations[chat_id]['address'] = call.data
        markup = types.InlineKeyboardMarkup()
        for date in config.FREE_DATES:
            markup.add(types.InlineKeyboardButton(date, callback_data=date))
        bot.send_message(chat_id, 'Выберите дату', reply_markup=markup)

    elif call.data in config.FREE_DATES:
        active_reservations[chat_id]['date'] = call.data
        markup = types.InlineKeyboardMarkup()
        for time in config.FREE_TIME:
            markup.add(types.InlineKeyboardButton(time, callback_data=time))
        bot.send_message(chat_id, 'Выберите время', reply_markup=markup)

    elif call.data in config.FREE_TIME:
        active_reservations[chat_id]['time'] = call.data
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Подтвердить', callback_data='confirm'))
        bot.send_message(chat_id, 'Подтвердите выбор', reply_markup=markup)

    elif call.data == 'confirm':
        bot.send_message(chat_id, 'Ваша бронь: \n' + str(active_reservations[chat_id]))
        msg = bot.send_message(chat_id, 'Введите имя')
        bot.register_next_step_handler(msg, process_name, chat_id)

def process_name(message, chat_id):
    active_reservations[chat_id]['name'] = message.text
    result = add_reserws(chat_id, active_reservations[chat_id]['address'], 
                         active_reservations[chat_id]['date'], 
                         active_reservations[chat_id]['time'])
    if result and result.get('status_code') == 200:
        bot.send_message(chat_id, f'Бронь успешно создана для {active_reservations[chat_id]["name"]}!')
    else:
        bot.send_message(chat_id, 'Ошибка при создании брони')
    del active_reservations[chat_id]  

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