import telebot
from telebot import types
from secret import *

bot = telebot.TeleBot(token)

debug_modes = {}

filter1 = ["🕧", "🕜", "🕝", "🕞", "🕠", "️🕢", "🕣", "🕤", "✔️"]
filter2 = ["🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔", "🌕","✔️"]
welcome_message = 'приветствую вас! Я бот - Помощник могу отвечать на вопросы, Генерировать разные текста и т.д. Tакже я могу озвучивать текст. (Перед использованием бота рекомендую просмотреть как им пользоваться /help)'
help_message = "YandexGPT - Бот который будет отвечать на вопросы, TTS - Озвучка текста. У каждого из этих функций есть свои ограничения в токенах и т.д. (их можно посмотреть нажав на кнопку 'Посмотреть сколько токенов затрачено 🔎' после использования. В функции YandexGPT и TTS есть ограничения на длинну запроса (Для аудио не больше 30 секунд, а для текста где-то не больше 80 символов. TTS изначально где-то 200, но оно постоянно меняется) "
photo1 = "https://avatars.mds.yandex.net/i?id=6af5966e54b0d6e9ac885315546b6bba_l-9181443-images-thumbs&n=13"
photo2 = "https://avatars.mds.yandex.net/i?id=47722801f350b4a63c9314a9606d772f9a4d18ef-4552023-images-thumbs&n=13"
photo3 = "https://sun9-77.userapi.com/impg/kMucUQ8s5l6yl4q00UOpfXYh-_7ZuGddZ1JzPw/Yv2cOf7gkOM.jpg?size=1920x1080&quality=95&sign=8ce033ad81604db02fd0d89b39ea7a32&type=album"

photo4 = "https://sun9-27.userapi.com/impg/bU-7-sLYi-tjTTnPJwxAMdLIGpdHP1Ae8sjIkQ/kodJlPX9-Eg.jpg?size=480x160&quality=95&sign=f5240c6d557ab446be80aa1c81c17e77&type=album"

golosa = ["Alena", "Filipp", "Ermil", "Jane", "Madirus", "Zahar", "Marina"]

PRICE_1000_TOKENS = types.LabeledPrice(label='Пакет на 1000 токенов, 12 SST блоков и 1000 TTS символов', amount=1000)
PRICE_2000_TOKENS = types.LabeledPrice(label='Пакет на 2000 токенов, 24 SST блоков и 2000 TTS символов', amount=2000)
PRICE_3000_TOKENS = types.LabeledPrice(label='Пакет на 3000 токенов, 36 SST блоков и 3000 TTS символов', amount=3000)

def create_keyboard_new():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Другой Запрос 🔄")
    button2 = telebot.types.KeyboardButton(text="Подтвердить ✔️")
    keyboard.add(button1, button2)
    return keyboard

def create_keyboard_table():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Новый запрос 🔄")
    button2 = telebot.types.KeyboardButton(text="Вернуться в начало 🔙")
    button3 = telebot.types.KeyboardButton(text="Посмотреть сколько токенов затрачено 🔎")
    keyboard.add(button1, button2, button3)
    return keyboard

def create_keyboard_choice():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="YandexGPT")
    button2 = telebot.types.KeyboardButton(text="TTS")
    keyboard.add(button1, button2)
    return keyboard

def create_keyboard_continued_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button2 = telebot.types.KeyboardButton(text="Новый Запрос 🔄")
    button5 = telebot.types.KeyboardButton(text="Посмотреть сколько токенов затрачено 🔎")
    button3 = telebot.types.KeyboardButton(text="Вернуться в начало 🔙")
    keyboard.add(button2, button5, button3)
    return keyboard

def create_keyboard_golos():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in golosa:
        button1 = telebot.types.KeyboardButton(text=i)
        keyboard.add(button1)
    return keyboard

def toggle_debug_mode(message):
    user_id = message.chat.id
    if user_id not in debug_modes:
        debug_modes[user_id] = False
    debug_modes[user_id] = not debug_modes[user_id]
    if debug_modes[user_id]:
        bot.send_message(user_id, "Режим отладки включён")
    else:
        bot.send_message(user_id, "Режим отладки выключен")

def buy(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Пакет на 10 рублей", callback_data='buy_1000'),
        types.InlineKeyboardButton("Пакет на 20 рублей", callback_data='buy_2000')
    )
    keyboard.row(types.InlineKeyboardButton("Пакет на 30 рублей", callback_data='buy_3000'))
    bot.send_message(message.chat.id, "Выберите нужной вам пакет услуг:", reply_markup=keyboard)

def send_invoice(chat_id, price):
    bot.send_invoice(
        chat_id=chat_id,
        title="Покупка пакета услуг",
        description=price.label,
        invoice_payload='payload',
        provider_token=PAYMENTS_TOKEN,
        start_parameter='start_parameter',
        currency='rub',
        prices=[price],
        is_flexible=False
    )

