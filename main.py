import asyncio
import time
import traceback
from datetime import datetime
import os
from os.path import join, dirname, abspath

import pandas as pd

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

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

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

current_index = -1

next_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Далее', callback_data='next')]])

async def get_table_scope():
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
    #print(df)
    return df


@dp.message(Command("start"))
async def start_bot(message: Message):
    global current_index
    current_index = -1
    welcome_message = """
Привет! Я телеграм-бот.
Помогу тебе с приемом лекарств."""

    # Создаем Inline-клавиатуру


    #next_button = types.InlineKeyboardButton(text='Далее', callback_data='next')
    #inline_keyboard = types.InlineKeyboardMarkup.add(next_button)

    # Отправляем приветственное сообщение с Inline-клавиатурой
    await bot.send_message(message.chat.id, welcome_message, reply_markup=next_button, disable_notification=True)

# Обработчик нажатия на кнопку "Далее"
#@dp.callback_query(func=lambda call: call.data == 'next')
@dp.callback_query()
async def next_data(call: types.CallbackQuery):
    if call.data == 'next':

        chat_id = call.message.chat.id
        global current_index
        current_index += 1

        df = await get_table_scope()

        if current_index < len(df):
            # Отправка следующей строки данных
            #send_next_data(chat_id)
            #bot.send_message(chat_id, current_index)

            # next_button = types.InlineKeyboardButton("Далее", callback_data='next')
            # inline_keyboard = types.InlineKeyboardMarkup()
            # inline_keyboard.add(next_button)

            df['from'] = pd.to_datetime(df['from'], dayfirst=True)
            df['to'] = pd.to_datetime(df['to'], dayfirst=True)
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
💊{name}
Прием:
 С {from_.strftime('%Y-%m-%d')}
ПО {to.strftime('%Y-%m-%d')}
Осталось: {delta} д.
"""

            if pd.to_datetime(from_) <= date_now < pd.to_datetime(to):
                print(txt)
                await bot.send_message(call.message.chat.id,
                                 txt,
                                 reply_markup=next_button, disable_notification=True)
            else:
                txt = f'Лекарство {name} пока/уже не принимать'
                print(txt)
                await next_data(call)

        else:
            # Если достигнут конец данных
            await bot.send_message(chat_id, 'Конец данных')


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    print('Запуск бота')
    while True:
        try:
            asyncio.run(main())

        except Exception as e:
            print('Произошла ошибка: ', e)
            print('Перезапуск бота через 10 секунд...')
            traceback.print_exc()
            time.sleep(10)



