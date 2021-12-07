#!/usr/bin/python3

# Required libraries: pandas, xlsxwriter, xlrd, openpyxl, selenium

from selenium import webdriver
import time
import pandas as pd
from openpyxl import load_workbook


driver = webdriver.FireFox()
driver.get('https://online.moysklad.ru/')

login_box = driver.find_element_by_id("lable-login")
login_box.send_keys('')
password_box = driver.find_element_by_id("lable-password")
password_box.send_keys('')
login_button = driver.find_element_by_id("submitButton")
login_button.click()

time.sleep(3)  # TODO: IMPLEMENT A BETTER WAIT TIMER

driver.get('https://online.moysklad.ru/app/#customerorder?global_customerOrderShippingStatusFilter=partiallyshipped,')

time.sleep(10)  # TODO: IMPLEMENT A BETTER WAIT TIMER

partially_shipped = driver.find_element_by_xpath(
    '/html/body/div[4]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/table/tbody/tr/td/div/div/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[3]/div'
    )

partially_shipped_value = partially_shipped.text


driver.quit()

data_frame = pd.DataFrame({
    'Date': [time.strftime("%Y-%m-%d", time.localtime())],
    'Time': [time.strftime("%H:%M:%S", time.localtime())],
    'Partially shipped': [partially_shipped_value]
    })

file_name = 'partially_shipped.xlsx'

try:
    writer = pd.ExcelWriter(file_name, engine='openpyxl')
    writer.book = load_workbook(file_name)
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)  # I have no idea what that is
    reader = pd.read_excel(file_name)
    init_row = len(reader) + 1
    data_frame.to_excel(writer, index=False, header=False, startrow=init_row)
    writer.close()
except FileNotFoundError:
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    data_frame.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()

