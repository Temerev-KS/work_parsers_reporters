#!/usr/bin/python3

from selenium import webdriver
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scopes=scope)
client = gspread.authorize(creds)

sheet = client.open('Partially Shipped (MoySklad selenium parsed data)').sheet1

driver = webdriver.Firefox()
driver.get('https://online.moysklad.ru/')

login_box = driver.find_element_by_id("lable-login")
login_box.send_keys('')
password_box = driver.find_element_by_id("lable-password")
password_box.send_keys('')
login_button = driver.find_element_by_id("submitButton")
login_button.click()

time.sleep(3)  # Chance to do better in the future

driver.get('https://online.moysklad.ru/app/#customerorder?global_customerOrderShippingStatusFilter=partiallyshipped,')

time.sleep(3)  # Chance to do better in the future

time_period_button = driver.find_element_by_xpath(
    '/html/body/div[4]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/table/tbody/tr/td/div/div/table/tbody/tr[2]/td/div/div/div/div[1]/div[2]/div[2]/div[3]'
    )
time_period_button.click()
time.sleep(3) # Chance to do better in the future

find_button = driver.find_element_by_xpath(
    '/html/body/div[4]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/table/tbody/tr/td/div/div/table/tbody/tr[2]/td/div/div/div/table/tbody/tr/td[1]/div'
    )
find_button.click()

time.sleep(15)  # Chance to do better in the future

partially_shipped = driver.find_element_by_xpath(
    '/html/body/div[4]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/table/tbody/tr/td/div/div/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[3]/div'
    )

partially_shipped_string = partially_shipped.text

driver.quit()

partially_shipped_value = re.match('.*?([0-9]+)$', partially_shipped_string).group(1)

data = [
    time.strftime("%Y.%m.%d", time.localtime()),
    time.strftime("%H:%M:%S", time.localtime()),
    partially_shipped_value
    ]

sheet.append_row(data, value_input_option='USER_ENTERED')
