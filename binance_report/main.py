#!/usr/bin/python3

import json
import time
import gspread
import os
import platform
import pandas
import datetime
import requests
from binance.client import Client
from oauth2client.service_account import ServiceAccountCredentials

if __name__ == '__main__':
    # +++++++++++++++++++++++++++++++++ SETUP VARIABLES AND CONSTANTS +++++++++++++++++++++++++++++++++ #
    
    if platform.system() == 'Linux':
        CURRENT_DIRECTORY = '/home/comet/PycharmProjects/megaplan_data_parser/binance_report'
    else:
        CURRENT_DIRECTORY = os.getcwd()
    
    CURRENT_TIME = datetime.datetime.now().time()
    CURRENT_DATE = datetime.datetime.now().date()
    YESTERDAY_DATE = CURRENT_DATE - datetime.timedelta(days=1)

    CHAT_ID = 'хххххххххх'
    SECOND_CHAT_ID = 'хххххххххх'

# +++++++++++++++++++++++++++++++++ CONNECT TO BINANCE +++++++++++++++++++++++++++++++++ #

    binance_json_key_path = ''.join((CURRENT_DIRECTORY, '/binance_api.json'))

    with open(binance_json_key_path, mode='r') as binance_api_keys:
        keys = json.load(binance_api_keys)
        api_key = keys['api_key']
        api_secret = keys['api_secret']
    
    binance_client = Client(api_key, api_secret)
    
# +++++++++++++++++++++++++++++++++ GET ACCOUNT BALANCE AND PNL +++++++++++++++++++++++++++++++++ #

    futures_balance_request = binance_client.futures_account_balance()
    account_info = binance_client.futures_account()
    balance = float(account_info['totalWalletBalance'])
    pnl = float(account_info['totalCrossUnPnl'])
    
# +++++++++++++++++++++++++++++++++ CONNECT TO GOOGLE SHEETS +++++++++++++++++++++++++++++++++ #
    gspread_json_key_path = ''.join((CURRENT_DIRECTORY, '/creds.json'))
    auth_scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gspread_json_key_path, scopes=auth_scopes)
    gspread_client = gspread.authorize(credentials)
    work_sheet = gspread_client.open('Binance_balance_log').sheet1

# +++++++++++++++++++++++++++++++++ LOAD AND CONVERT DATA +++++++++++++++++++++++++++++++++ #

    table_data = work_sheet.get_all_values()
    
    dataframe = pandas.DataFrame(table_data)
    dataframe.columns = dataframe.iloc[0]
    dataframe = dataframe.drop(0).reset_index(drop=True)
    
    today = datetime.datetime.now().strftime("%Y.%m.%d")
    today_records = dataframe.loc[dataframe["Date"] == today]
    dataframe.Date = pandas.to_datetime(dataframe.Date)
    dataframe.Time = pandas.to_timedelta(dataframe.Time)

# +++++++++++++++++++++++++++++++++ LOCATE LAST CLOSING DATA +++++++++++++++++++++++++++++++++ #
    
    def convert_to_python_float(item):
        result = float(str(item).replace('$', '').replace(u'\xa0', '').replace(',', '.'))
        return result
    
    
    records_yesterday = dataframe[dataframe['Date'] == str(YESTERDAY_DATE)]
    yesterday_closing = records_yesterday[records_yesterday['Time'] > datetime.timedelta(hours=21, minutes=50)]
    yesterday_closing = yesterday_closing[yesterday_closing['Time'] < datetime.timedelta(hours=22, minutes=20)]
    
    try:
        yesterday_last_balance = convert_to_python_float(yesterday_closing['Balance'].item())
    except ValueError:
        yesterday_last_balance = 0
    day_delta = balance - yesterday_last_balance
    
    previous_record_balance = convert_to_python_float(dataframe.iloc[-1:]['Balance'].item())
    current_delta = balance - previous_record_balance

# +++++++++++++++++++++++++++++++++ FORMAT AND ORGANISE DATA TO SEND +++++++++++++++++++++++++++++++++ #

    data = [
        time.strftime("%Y.%m.%d", time.localtime()),
        time.strftime("%H:%M:%S", time.localtime()),
        balance,
        current_delta,
        pnl
    ]
    if 21 < CURRENT_TIME.hour < 23:
        data.append(day_delta)
        
    print(data)

# +++++++++++++++++++++++++++++++++ WRITE DATA +++++++++++++++++++++++++++++++++ #

    work_sheet.append_row(data, value_input_option='USER_ENTERED')


# +++++++++++++++++++++++++++++++++ SEND NOTIFICATION +++++++++++++++++++++++++++++++++ #
def send_notification(msg: str, recipient: str):
    """
    Sends text message via Telegram bot.
    :param msg: String of characters to send.
    :param recipient: Telegram chat_id (lookup Telegram API for details)
    """
    credentials_path = ''.join((CURRENT_DIRECTORY, '/credentials.json'))
    with open(credentials_path, mode='r') as telegram_credentials:
        telegram_token = json.load(telegram_credentials)['telegram']['BOT_TOKEN']
    telegram_api_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {
        'chat_id': recipient,
        'text': msg
    }
    response = requests.get(telegram_api_url, data=payload, timeout=10)
    response.raise_for_status()
    print(response.json())


message_to_send = f'{time.strftime("%Y.%m.%d", time.localtime())}, {time.strftime("%H:%M:%S", time.localtime())}\n' \
          f'Balance: {round(balance, 3)}\n' \
          f'Delta: {round(current_delta, 3)}\n' \
          f'PNL: {round(pnl, 3)}\n'

send_notification(message_to_send, CHAT_ID)
send_notification(message_to_send, SECOND_CHAT_ID)
