#! /usr/local/bin/python3.7

# Required libraries: pandas, xlsxwriter, xlrd, openpyxl, selenium

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import pandas as pd
from openpyxl import load_workbook

desired_capabilities = DesiredCapabilities.CHROME.copy()
desired_capabilities['acceptInsecureCerts'] = True

driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
driver.get('https://oqprint.megaplan.ru/newdashboard/')

login_box = driver.find_element_by_xpath('//*[@id="login"]')
login_box.send_keys('')
password_box = driver.find_element_by_xpath('//*[@id="password"]')
password_box.send_keys('')
login_button = driver.find_element_by_xpath('//*[@id="mp-btn_default-login-enter"]')
login_button.click()

time.sleep(10)  # TODO: IMPLEMENT A BETTER WAIT TIMER

tuning = driver.find_element_by_xpath(
    '/html/body/div[1]/div[2]/div[2]/div/div[1]/div/div/div/div/div[3]/div/div[1]/div[1]/div[1]/div[2]'
    )
tuning_it = driver.find_element_by_xpath(
    '/html/body/div[1]/div[2]/div[2]/div/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div[2]'
    )
failure = driver.find_element_by_xpath(
    '/html/body/div[1]/div[2]/div[2]/div/div[1]/div/div/div/div/div[5]/div/div[1]/div[1]/div[1]/div[2]'
    )

tuning_value = tuning.text
tuning_it_value = tuning_it.text
failure_value = failure.text

driver.quit()

data_frame = pd.DataFrame({
    'Date': [time.strftime("%Y-%m-%d", time.localtime())],
    'Time': [time.strftime("%H:%M:%S", time.localtime())],
    'Tuning': [tuning_value],
    'Tuning IT': [tuning_it_value],
    'Malfunction': [failure_value]
    })

file_name = 'pandas_simple.xlsx'

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

