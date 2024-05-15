import time
from datetime import datetime
import os
from os.path import join, dirname, abspath

import pandas as pd
import telebot
from telebot import types

from google.oauth2 import service_account
from googleapiclient.discovery import build

from dotenv import load_dotenv

abspath = os.path.dirname(os.path.abspath(__file__))
dotenv_path = join(abspath, '.env')
# print('Размести .env тут', dirname(dirname(__file__)))
load_dotenv(dotenv_path)

# Получение токена из конфигурационного файла
TOKEN = os.environ.get("TELEGRAM_TOKEN")
SAMPLE_SPREADSHEET_ID = os.environ.get("SAMPLE_SPREADSHEET_ID")
SAMPLE_RANGE_NAME = os.environ.get("SAMPLE_RANGE_NAME")

# Создаем экземпляр бота, используя полученный токен
bot = telebot.TeleBot(TOKEN)

# gc = gspread.service_account(path_to_credentials)
# table_name = "Здоровье"
# workfile = gc.open(table_name)


def get_table_scope():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = os.path.join(abspath, 'service_account.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

    # Retrieve values from the spreadsheet
    result = service.get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        raise ValueError("No data found in the specified range.")

    while True:
        try:
            # Create a pandas DataFrame from the retrieved values
            df = pd.DataFrame(values[1:], columns=values[0])  # Assuming headers in the first row
            break

        except ValueError as VE:
            print('ValueError:', VE)
            numb = int(time.time())
            values[0].append(f'New_Col_{numb}')
            time.sleep(5)

    df['line'] = df['line'].astype(int)
    df = df.sort_values(by='line').reset_index(drop=True)
    print(df)
    return df

# Определяем обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    global current_index
    current_index = -1
    welcome_message = """
Привет! Я телеграм-бот.
Помогу тебе с приемом лекарств."""

    # Создаем Inline-клавиатуру
    inline_keyboard = types.InlineKeyboardMarkup()
    next_button = types.InlineKeyboardButton("Далее", callback_data='next')
    inline_keyboard.add(next_button)

    # Отправляем приветственное сообщение с Inline-клавиатурой
    bot.send_message(message.chat.id, welcome_message, reply_markup=inline_keyboard, disable_notification=True)

# Обработчик нажатия на кнопку "Далее"
@bot.callback_query_handler(func=lambda call: call.data == 'next')
def next_data(call):
    chat_id = call.message.chat.id
    global current_index
    current_index += 1

    df = get_table_scope()

    if current_index < len(df):
        # Отправка следующей строки данных
        #send_next_data(chat_id)
        #bot.send_message(chat_id, current_index)

        next_button = types.InlineKeyboardButton("Далее", callback_data='next')
        inline_keyboard = types.InlineKeyboardMarkup()
        inline_keyboard.add(next_button)

        df['from'] = pd.to_datetime(df['from'])
        df['to'] = pd.to_datetime(df['to'])
        date = df.loc[current_index, 'date']
        when = df.loc[current_index, 'when']
        name = df.loc[current_index, 'name']
        from_ = df.loc[current_index, 'from']
        to = df.loc[current_index, 'to']

        date_now = datetime.now()  # .strftime('%Y-%m-%d')
        delta = to.date() - date_now.date()
        delta = delta.days
        print(delta)

        txt = f"""{date} {when}
{name}
Прием:
 С {from_.strftime('%Y-%m-%d')}
ПО {to.strftime('%Y-%m-%d')}
Осталось: {delta} д."""

        if pd.to_datetime(from_) <= date_now < pd.to_datetime(to):
            print(txt)
            bot.send_message(call.message.chat.id,
                             txt,
                             reply_markup=inline_keyboard, disable_notification=True)
        else:
            txt = f'Лекарство {name} пока/уже не принимать'
            print(txt)
            next_data(call)

    else:
        # Если достигнут конец данных
        bot.send_message(chat_id, 'Конец данных')

if __name__ == "__main__":
    print('Запуск бота')
    while True:
        try:
            bot.polling()
        except Exception as e:
            print('Произошла ошибка: ', e)
            print('Перезапуск бота через 10 секунд...')
            time.sleep(10)



