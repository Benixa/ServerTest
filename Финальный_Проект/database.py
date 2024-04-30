import sqlite3
from info import *
def create_database():
    connection = sqlite3.connect('sqlite3.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS database (
            id INTEGER PRIMARY KEY, 
            user_id INTEGER, 
            user_request TEXT, 
            answer TEXT
        )
    ''')
    connection.close()

def create_database_2():
    connection = sqlite3.connect('sqlite3.db')
    cursor = connection.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS TOKENS_USERS (
            id INTEGER PRIMARY KEY, 
            user_id INTEGER, 
            tokens INTEGER DEFAULT {DEFAULT_USER_TOKENS}, 
            stt_blocks INTEGER DEFAULT {MAX_USER_STT_BLOCKS},
            tts_len INTEGER DEFAULT {max_sum_user_id}
        )
    ''')
    connection.close()

def execute_query(sql_query, data=None):

    connection = sqlite3.connect('sqlite3.db')
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)

    connection.commit()
    connection.close()

def execute_selection_query(sql_query, data=None):

    connection = sqlite3.connect('sqlite3.db')
    cursor = connection.cursor()

    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    connection.close()
    return rows

def successful_payment(message):
    user_id = message.from_user.id
    tokens = execute_selection_query("SELECT * FROM TOKENS_USERS WHERE user_id = ?", (user_id, ))[0]
    amount = message.successful_payment.total_amount
    if amount == 1000:
        execute_query('''UPDATE TOKENS_USERS SET tokens = ?, stt_blocks = ?, tts_len = ? WHERE user_id = ?''',
                      (tokens[2] + 1000, tokens[3] + 12, tokens[4] + 1000, user_id))
    elif amount == 2000:
        execute_query('''UPDATE TOKENS_USERS SET tokens = ?, stt_blocks = ?, tts_len = ? WHERE user_id = ?''',
                      (tokens[2] + 2000, tokens[3] + 24, tokens[4] + 2000, user_id))
    elif amount == 3000:
        execute_query('''UPDATE TOKENS_USERS SET tokens = ?, stt_blocks = ?, tts_len = ? WHERE user_id = ?''',
                      (tokens[2] + 3000, tokens[3] + 36, tokens[4] + 3000, user_id))

def delete(message):
    user_id = message.from_user.id
    execute_query('''DELETE FROM database WHERE user_id = ?''', (user_id,))
    execute_query('''DELETE FROM TOKENS_USERS WHERE user_id = ?''', (user_id,))