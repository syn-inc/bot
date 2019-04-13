import os
import requests
import telebot

token = os.environ['TOKEN']

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['get_temp'])
def get_temp(message):
    bot.reply_to(message, "It's around " + get_anything(1) + "°C at FICT")


@bot.message_handler(commands=['get_hum'])
def get_hum(message):
    bot.reply_to(message, "It's around " + get_anything(2) + "% at FICT")


@bot.message_handler(commands=['start', 'help'])
def start_help_response(message):
    bot.send_message(message.chat.id,
                     "Hi, I can help you with situation with current temperature, humidity and other stuff in "
                     "FICT.\nCheck out commands:\n\n /get_temp - current temperature\n /get_hum - current humidity")


def get_anything(sens_id: int) -> str:
    request_url = os.environ['GET_REQUEST'].format(str(sens_id))
    r = requests.get(request_url)
    data = r.json()
    return str(data['Values'][0])


@bot.message_handler(func=lambda message: True)
def default_response(message):
    photo = open('media/obivan.png', 'rb')
    bot.send_photo(message.chat.id, photo)


bot.polling(none_stop=True)
