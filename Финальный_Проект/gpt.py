from secret import *
import requests
from info import *
import time
import json

GPT_MODEL = 'yandexgpt-lite'

def count_tokens(promt) -> int:
    TOKEN = get_creds()
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    result = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
        headers = headers,
        json = {
            "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
            "text": promt
        }
    ).json()['tokens']
    return len(result)

def gpt(database, tok):
    TOKEN = get_creds()
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": MODEL_TEMPERATURE,
            "maxTokens": MAX_MODEL_TOKENS
        },
        "messages": [
            {"role": "system",
             "text": f"Ты Бот - Помощник, твоя задача отвечать на вопросы пользователя в области математики, Истории, Информатики, грамматики и так далее. Ограничься примерно 80 словами если ты не можешь всё уместить в 80 словах то просто ставь точку, также я запрещаю тебе писать такой символ как * "},
            {"role": "user", "text": f"Ответь на этот вопрос: {database[0]}"},
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        text_system = data["messages"][0]["text"]
        text_user = data["messages"][1]["text"]
        vol_tokens = tok - count_tokens(result) - count_tokens(text_system) - count_tokens(text_user)
        return True, result, vol_tokens
    else:
        return False, "При запросе к YandexGPT возникла ошибка."

def speech_to_text(data):
    TOKEN = get_creds()
    params = "&".join([
        "topic=general",
        f"folderId=b1g23q9ip6n1jnscc7v7",
        "lang=ru-RU"
    ])
    url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
    }

    response = requests.post(url=url, headers=headers, data=data)
    decoded_data = response.json()

    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")
    else:
        return False, "При запросе в SpeechKit возникла ошибка"

def text_to_speech(txt, vox):
    TOKEN = get_creds()
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': f"Bearer {TOKEN}"
    }

    data = {
        'text': txt,
        'lang': 'ru-RU',
        'folderId': FOLDER_ID,
        'voice': vox
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return True, response.content
    else:
        return False, "При запросе в SpeechKit возникла ошибка"

def create_new_token():
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    token_data = response.json()
    token_data["expires_at"] = time.time() + token_data["expires_in"]
    with open("TOKEN_PATH.json", "w") as token_file:
        json.dump(token_data, token_file)

def get_creds():
    try:
        with open("TOKEN_PATH.json", "r") as f:
            d = json.load(f)
            expiration = d["expires_at"]
        if expiration < time.time():
            create_new_token()
    except:
        create_new_token()
    with open("TOKEN_PATH.json", "r") as f:
        d = json.load(f)
        token = d["access_token"]

    return token