import pandas as pd

import os
import time
from os.path import join

from google.oauth2 import service_account
from googleapiclient.discovery import build

from dotenv import load_dotenv

abspath = os.path.dirname(os.path.dirname(__file__))
print(abspath)
dotenv_path = join(abspath, '.env')
print(dotenv_path)
# print('Размести .env тут', dirname(dirname(__file__)))
load_dotenv(dotenv_path)

# Получение токена из конфигурационного файла
SAMPLE_SPREADSHEET_ID = os.environ.get("SAMPLE_SPREADSHEET_ID")
SAMPLE_RANGE_NAME = os.environ.get("SAMPLE_RANGE_NAME")
print(SAMPLE_RANGE_NAME)

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

#asyncio.run(get_table_scope())