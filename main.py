import asyncio
from datetime import datetime
import os
from os.path import join, dirname, abspath

import pandas as pd

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from dotenv import load_dotenv

from utils.gs_module import get_table_scope

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

@dp.message(Command("start"))
async def start_bot(message: Message):
    global df
    df = await get_table_scope()

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

        global df
        try:
            len_df = len(df)
        except:

            df = await get_table_scope()
            len_df = len(df)

        if current_index < len_df:
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
{name}
Прием:
_С: {from_.strftime('%Y-%m-%d')}
ПО: {to.strftime('%Y-%m-%d')}
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
            await start_bot(call.message)


# if __name__ == "__main__":
#     executor.start_polling(dp, skip_updates=True)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    print('Запуск бота')
    asyncio.run(main())


