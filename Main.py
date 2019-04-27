import json
import os
import requests
import telebot
import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from PIL import Image

token = os.environ['TOKEN']

# Relative paths of pictures
# Proportions of pictures should be constant
DEF_PIC_RPATH: str = "media/obivan.png"  # default response pic
BUF_PIC_RPATH: str = "media/plt_pic.jpg"  # buffer picture for plotting plot_graph()
RES_PIC_RPATH: str = "media/res.jpg"  # result last week pic
LOGO_PIC_RPATH: str = "media/logo.jpg"  # syn logo pic

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['get_temp'])
def get_temp(message):
    """
    Sends current temperature by sensor id
    :param message: message that user sent
    """
    bot.reply_to(message, "It's around " + get_anything(1) + "°C at FICT")


@bot.message_handler(commands=['get_hum'])
def get_hum(message):
    """
    Sends current humidity by sensor id
    :param message: message of user
    """
    bot.reply_to(message, "It's around " + get_anything(2) + "% at FICT")


@bot.message_handler(commands=['get_pres'])
def get_pres(message):
    """
    Sends current pressure by sensor id
    :param message: message of user
    """
    bot.reply_to(message, "It's around " + get_anything(3) + "hPa at FICT")


@bot.message_handler(commands=['get_alt'])
def get_alt(message):
    """
    Sends current altitude by sensor id
    :param message: message of user
    """
    bot.reply_to(message, "FICT is around at " + get_anything(4) + "m above the height of the sea")


@bot.message_handler(commands=['get_light'])
def get_light(message):
    """
    Sends last current amount of luminous flux by sensor id
    :param message: message of user
    """
    bot.reply_to(message, "It's around " + get_anything(5) + "lx at FICT")


@bot.message_handler(commands=['get_last_week'])
def get_week(message):
    """
    Send to user picture with graph of the last week temperature
    :param message: message of user
    """
    r = requests.get(os.environ["GET_WEEK"])

    x = plot_graph(r)

    if x is None:
        # open and sens week stat picture
        photo = open(RES_PIC_RPATH, 'rb')
        bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "Oops...something went wrong, try later!")


@bot.message_handler(commands=['start', 'help'])
def start_help_response(message):
    """
    Sends help message
    :param message: message of user
    """
    bot.send_message(message.chat.id,
                     "Hi, I can help you with situation with current temperature, humidity and other stuff in "
                     "FICT.\nCheck out commands:\n\n"
                     "/get_temp - current temperature\n"
                     "/get_hum - current humidity\n"
                     "/get_pres - current pressure (in hectopascals)\n"
                     "/get_alt - current altitude\n"
                     "/get_light - current amount of luminous flux")


def get_anything(sens_id: int) -> str:
    """
    Extract 'values' from JSON-response
    :param sens_id: id of sensor
    :return: string with float number
    """
    request_url = os.environ['GET_REQUEST'].format(str(sens_id))
    r = requests.get(request_url)
    data = r.json()
    return str(data['values'])


@bot.message_handler(func=lambda message: True)
def default_response(message):
    """
    Sends picture each time when event is not handled
    :param message: message that user sent
    """
    photo = open(DEF_PIC_RPATH, 'rb')
    bot.send_photo(message.chat.id, photo)


def plot_graph(r: requests.Response):
    """
    Extract from request float-list and build graph with dependency temperature from time
    :param r: response which contains 7 average values of temperature for the last week
    """
    # generating list of last 7 days
    start = datetime.datetime.today().date()
    x = [(start - datetime.timedelta(days=x)) for x in range(0, 7)]
    x.reverse()

    try:
        y: list = r.json()['values']
    except json.decoder.JSONDecodeError:
        return -1

    # graph's configurations
    plt.title("Last Week")
    plt.xlabel('Days')
    plt.ylabel('Temperature °C')
    plt.grid(True)
    # formats date for x axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()

    plt.plot(x, y, "bo")

    plt.savefig(RES_PIC_RPATH)

    try:
        # pasting logo into graph
        img = Image.open(RES_PIC_RPATH)
        img2 = Image.open(LOGO_PIC_RPATH)
        img.paste(img2, (10, 10))  # (590, 430)
        img.save(RES_PIC_RPATH)

    except IOError:
        pass


bot.polling(none_stop=True)
