# -*- coding: utf-8 -*-
from os import environ
from flask import Flask, request
from telebot import types, TeleBot
from random import randint, choice
from requests import get


TOKEN = environ.get('API_TOKEN')
YA_API = environ.get('YA_API')
my_domain = '<your_domain>'

bot = TeleBot(TOKEN)
server = Flask(__name__)

keyboard1 = types.ReplyKeyboardMarkup(True, True)
keyboard1.row('🎁 Рандомайзер', '🎲 Игральная кость', '🎭 Орёл-решка')


def rand_func(a, b):
    return randint(a, b)


def numbers_api(num):
    try:
        api_url = 'http://numbersapi.com/{}/trivia'
        params = {
            'json': True,
            'notfound': 'floor'
        }
        res = get(api_url.format(num), params=params)
        res.raise_for_status()
        if res.status_code == 200:
            return ya_translate(res.json()['text'])
    except BaseException as e:
        return e


def ya_translate(text):
    try:
        url = r'https://translate.yandex.net/api/v1.5/tr.json/translate'
        params = {
            'key': YA_API,
            'text': text,
            'lang': 'en-ru'
        }
        res = get(url, params=params)
        res.raise_for_status()
        if res.status_code == 200:
            return res.json()['text'][0]
    except BaseException as e:
        return e


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Привет, чем могу помочь?\n'
                     'В данный момент я могу выбирать случайные числа из '
                     'заданного диапазона. Это можно сделать, даже не нажимая '
                     'специальной кнопки, просто введя два любых числа.'
                     'Попробуй 😉',
                     reply_markup=keyboard1)


@bot.message_handler(regexp=r"^-?(\d+)\s-?(\d+)$", content_types=['text'])
def random_bone(message):
    a, b = (int(float(i)) for i in message.text.lower().split())
    if a > b:
        a, b = b, a
    num = rand_func(a, b)
    bot.send_message(message.chat.id, num)
    bot.send_message(message.chat.id, numbers_api(num), reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == '🎁 рандомайзер':
        bot.send_message(message.chat.id,
                         'Введите два числа из необходимого '
                         'диапазона через пробел. Например: 16 48')
    elif message.text.lower() == '🎲 игральная кость':
        bot.send_message(message.chat.id, rand_func(1, 6),
                         reply_markup=keyboard1)
    elif message.text.lower() == '🎭 орёл-решка':
        mon = choice(['Орёл', 'Решка'])
        bot.send_message(message.chat.id, mon, reply_markup=keyboard1)


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates(
        [types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url='https://%s/%s' % (my_domain, TOKEN))
    server.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
