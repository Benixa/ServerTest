import logging
from info import *
from gpt import count_tokens, gpt, text_to_speech, speech_to_text, create_new_token
from database import create_database, execute_query, execute_selection_query, create_database_2, successful_payment, delete
from content import *
import math
import time

bot = telebot.TeleBot(token)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

create_database()
create_database_2()

gl = {}



@bot.message_handler(commands=['debug'], func=toggle_debug_mode)

@bot.message_handler(commands=['buy'], func=buy)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'buy_1000':
        send_invoice(call.message.chat.id, PRICE_1000_TOKENS)
    elif call.data == 'buy_2000':
        send_invoice(call.message.chat.id, PRICE_2000_TOKENS)
    elif call.data == 'buy_3000':
        send_invoice(call.message.chat.id, PRICE_3000_TOKENS)

@bot.pre_checkout_query_handler(lambda query: True)
def pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'], func=successful_payment)

@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.from_user.id
    bot.send_photo(user_id, photo4, help_message)
    # п.с надпись с картинки переводится как "Help"
    choice(message)

@bot.message_handler(commands=['delete'], func=delete)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    if user_id in debug_modes and debug_modes[user_id]:
        bot.send_message(user_id, f'Пользователь с id: {user_id} начал разговор.')
    logging.info(f'Пользователь с id: {user_id} начал разговор.')
    user = execute_selection_query("SELECT * FROM database WHERE user_id = ?", (user_id,))
    all_user = execute_selection_query('''SELECT DISTINCT user_id FROM TOKENS_USERS''')
    if user:
        choice(message)
    else:
        if len(all_user) > max_project_user:
            bot.send_message(user_id, "Доступ к боту ограничен из-за привышения кол-во пользователей.")
        else:
            execute_query('''INSERT INTO TOKENS_USERS (user_id) VALUES (?)''', (user_id,))
            execute_query('''INSERT INTO database (user_id) VALUES (?)''', (user_id,))
            bot.send_photo(user_id, photo3, welcome_message)
            # п.с надпись с картинки переводится как "Здраствуйте"
            if user_id in debug_modes and debug_modes[user_id]:
                bot.send_message(user_id, f'Пользователю с id: {user_id} Создал новую запись в БД.')
            logging.info(f'Пользователю с id: {user_id} Создал новую запись в БД.')
            choice(message)

def handle_command(message):
    if message.text == "/start":
        handle_start(message)
        return True
    elif message.text == "/delete":
        delete(message)
        return True
    elif message.text == "/debug":
        toggle_debug_mode(message)
        return True
    elif message.text == "/help":
        send_help(message)
        return  True
    elif message.text == "/buy":
        buy(message)
        return True
    else:
        return False

def choice(message):
    user_id = message.chat.id
    keyboard = create_keyboard_choice()
    bot.send_message(user_id, f"Выберите функцию бота.", reply_markup=keyboard)
    bot.register_next_step_handler(message, detection_choice)

def detection_choice(message):
    if message.text == "YandexGPT":
        just_an_intermediate_function(message)
    elif message.text == "TTS":
        golos(message)
    else:
        command_handled = handle_command(message)
        if not command_handled:
            choice(message)

def mes(message):
    user_id = message.from_user.id
    execute_query('''INSERT INTO database (user_id) VALUES (?)''', (user_id,))
    bot.send_message(user_id, "Введите текст что бы потом его озвучить.")
    bot.register_next_step_handler(message, tts)

def golos(message):
    user_id = message.chat.id
    keyboard = create_keyboard_golos()
    bot.send_message(user_id, 'Выберите голос для озвучки.', reply_markup=keyboard)
    bot.register_next_step_handler(message, detection_golos)

def detection_golos(message):
    user_id = message.chat.id
    if message.text in golosa:
        gl[user_id] = message.text.lower()
        mes(message)
    else:
        command_handled = handle_command(message)
        if not command_handled:
            golos(message)
def tts(message):
    user_id = message.from_user.id
    txt = message.text
    if message.text:
        vox = gl[user_id]
        session_id = execute_selection_query('''SELECT MAX(id) FROM database WHERE user_id = ?''', (user_id,))[0][0]
        tts_len = execute_selection_query('''SELECT tts_len FROM TOKENS_USERS WHERE user_id = ?''', (user_id,))[0][0]
        long_txt = len(txt)
        print(message.text, long_txt)
        if tts_len <= 0:
            bot.send_message(user_id, "Вы привысили пользовательский лимит TTS символов.")
            return
        if long_txt > tts_len:
            bot.send_message(user_id, "Ваш Запрос слишком большой. Укоротите его.")
            mes(message)
            return

        status, content = text_to_speech(txt, vox)

        if status:
            msg = bot.send_message(message.chat.id, "Loading 🕦")
            for i in filter1:
                time.sleep(0.1)
                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=f"Loading: {i}")
            bot.send_voice(user_id, content)
            execute_query('''UPDATE database SET user_request = ?, answer = ? WHERE user_id = ? AND id = ?''', (txt, "TTS", user_id, session_id))
            execute_query('''UPDATE TOKENS_USERS SET tts_len = ? WHERE user_id = ?''', (tts_len - long_txt, user_id))
            execute_query('DELETE FROM database WHERE user_request IS NULL')
            table(message)
        else:
            bot.send_message(user_id, content)
    else:
        bot.send_photo(message.chat.id, photo1, "Вы отправили контент не того типа!")
        mes(message)

def table(message):
    user_id = message.chat.id
    keyboard = create_keyboard_table()
    bot.send_message(user_id, 'Что будем делать дальше?', reply_markup=keyboard)
    bot.register_next_step_handler(message, detection_table)

def detection_table(message):
    user_id = message.chat.id
    database = execute_selection_query('''SELECT tts_len FROM TOKENS_USERS WHERE user_id = ?''', (user_id,))[0]
    if message.text == "Новый запрос 🔄":
        golos(message)
    elif message.text == "Вернуться в начало 🔙":
        choice(message)
    elif message.text == "Посмотреть сколько токенов затрачено 🔎":
        bot.send_message(user_id, f"У вас осталось {database[0]} TTS символов.")
        table(message)
    else:
        command_handled = handle_command(message)
        if not command_handled:
            table(message)

def just_an_intermediate_function(message):
    user_id = message.chat.id
    execute_query('''INSERT INTO database (user_id) VALUES (?)''', (user_id,))
    bot.send_photo(user_id, photo2, "Введите Запрос или отправьте мне голосовое сообщение.")
    bot.register_next_step_handler(message, detection)

def detection(message):
    if message.text:
        user_request(message)
    elif message.voice:
        voiceover(message)
    else:
        command_handled = handle_command(message)
        if not command_handled:
            just_an_intermediate_function(message)

def voiceover(message):
    user_id = message.from_user.id
    duration = message.voice.duration
    audio_blocks = math.ceil(duration / 15)
    all_blocks = execute_selection_query('''SELECT stt_blocks FROM TOKENS_USERS WHERE user_id = ?''', (user_id, ))[0][0]
    table_audio_blocks = execute_selection_query('''SELECT stt_blocks FROM TOKENS_USERS WHERE user_id = ?''', (user_id, ))[0][0] - audio_blocks
    session_id = execute_selection_query('''SELECT MAX(id) FROM database WHERE user_id = ?''', (user_id,))[0][0]

    if all_blocks <= 0:
        bot.send_message(user_id, "Вы привысили пользовательский лимит STT блоков.")
        return
    if duration >= 30:
        bot.send_message(user_id, "Ваш Запрос слишком большой. Укоротите его.")
        just_an_intermediate_function(message)
        return

    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)

    status, text = speech_to_text(file)

    if text == "":
        bot.send_message(user_id, "Извините бот не смог распознать Аудио.")
        just_an_intermediate_function(message)
        return

    if status:
        execute_query('''UPDATE TOKENS_USERS SET stt_blocks = ? WHERE user_id = ?''', (table_audio_blocks, user_id))
        execute_query('''UPDATE database SET user_request = ? WHERE user_id = ? AND id = ?''', (text, user_id, session_id))
        new(message)
    else:
        bot.send_message(user_id, text)
def new(message):
    user_id = message.chat.id
    session_id = execute_selection_query('''SELECT MAX(id) FROM database WHERE user_id = ?''', (user_id,))[0][0]
    text = execute_selection_query('''SELECT user_request FROM database WHERE user_id = ? AND id = ?''', (user_id, session_id))[0][0]
    user_id = message.chat.id
    keyboard = create_keyboard_new()
    bot.send_message(user_id, f"Вы отправили: {text}", reply_markup=keyboard)
    bot.register_next_step_handler(message, detection_new)
def detection_new(message):
    if message.text == "Другой Запрос 🔄":
        just_an_intermediate_function(message)
    elif message.text == "Подтвердить ✔️":
        answer(message)
    else:
        command_handled = handle_command(message)
        if not command_handled:
            new(message)

def user_request(message):
    request = message.text
    user_id = message.chat.id
    tokens = execute_selection_query('''SELECT tokens FROM TOKENS_USERS WHERE user_id = ?''', (user_id,))[0][0]
    session_id = execute_selection_query('''SELECT MAX(id) FROM database WHERE user_id = ?''', (user_id,))[0][0]
    if count_tokens(request) > MAX_MODEL_TOKENS:
        bot.send_message(user_id, "Сообщение слишком большое. Сократите его пожалуйста.")
        if user_id in debug_modes and debug_modes[user_id]:
            bot.send_message(user_id, f"Пользователю с id: {user_id} было отказано в запросе из-за слишком большой длины Сообщения.")
        logging.info(f'Пользователю с id: {user_id} было отказано в запросе из-за слишком большой длины Сообщения.')
        just_an_intermediate_function(message)
    elif tokens <= 0:
        bot.send_message(user_id, "Вы привысили пользовательский лимит токенов.")
    else:
        execute_query('''UPDATE database SET user_request = ? WHERE user_id = ? AND id = ?''', (request, user_id, session_id))
        answer(message)

def answer(message):
    user_id = message.chat.id
    session_id = execute_selection_query('''SELECT MAX(id) FROM database WHERE user_id = ?''', (user_id,))[0][0]
    database = execute_selection_query('''SELECT user_request FROM database WHERE user_id = ? AND id = ?''', (user_id, session_id))[0]
    tok = execute_selection_query('''SELECT tokens FROM TOKENS_USERS WHERE user_id = ?''', (user_id, ))[0][0]

    status, content, tokens = gpt(database, tok)

    if status:
        msg = bot.send_message(message.chat.id, "Loading: 🌕")
        for i in filter2:
            time.sleep(0.1)
            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=f"Loading: {i}")
        bot.send_message(user_id, content)
        execute_query('''UPDATE database SET answer = ? WHERE user_id = ? AND id = ?''', (content, user_id, session_id))
        execute_query('''UPDATE TOKENS_USERS SET tokens = ? WHERE user_id = ?''', (tokens, user_id))
        execute_query('DELETE FROM database WHERE user_request IS NULL')
        continued_keyboard(message)
    else:
        if user_id in debug_modes and debug_modes[user_id]:
            bot.send_message(user_id, content)
        logging.error(f"Произошла непредвиденная ошибка: {content}")

def continued_keyboard(message):
    user_id = message.chat.id
    keyboard = create_keyboard_continued_keyboard()
    bot.send_message(user_id, 'Что будем делать дальше?', reply_markup=keyboard)
    bot.register_next_step_handler(message, tracking_continued_keyboard)

def tracking_continued_keyboard(message):
    user_id = message.chat.id
    database = execute_selection_query('''SELECT tokens, stt_blocks FROM TOKENS_USERS WHERE user_id = ?''', (user_id, ))[0]
    msg_continued = message.text
    if msg_continued == "Новый Запрос 🔄":
        just_an_intermediate_function(message)
    elif msg_continued == "Посмотреть сколько токенов затрачено 🔎":
        bot.send_message(user_id, f"У вас осталось токенов: {database[0]} и stt-Блококов: {database[1]}.")
        continued_keyboard(message)
    elif message.text == "Вернуться в начало 🔙":
        choice(message)
    else:
        command_handled = handle_command(message)
        if not command_handled:
            continued_keyboard(message)

bot.polling()