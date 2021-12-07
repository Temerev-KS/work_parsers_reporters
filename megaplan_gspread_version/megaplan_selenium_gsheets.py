#!/usr/bin/python3

from selenium import webdriver
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scopes=scope)
client = gspread.authorize(creds)

sheet = client.open('Megaplan Tech Tasks (left by the end of the day)').sheet1

driver = webdriver.Firefox()
# driver = webdriver.Chrome()
driver.get('https://oqprint.megaplan.ru/newdashboard/')

login_box = driver.find_element_by_xpath('//*[@id="login"]')
login_box.send_keys('')
password_box = driver.find_element_by_xpath('//*[@id="password"]')
password_box.send_keys('')
login_button = driver.find_element_by_xpath('//*[@id="mp-btn_default-login-enter"]')
login_button.click()

time.sleep(10)  # Chance to do batter in the future

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
total = int(tuning_value) + int(tuning_it_value) + int(failure_value)

driver.quit()

data = [
    time.strftime("%Y.%m.%d", time.localtime()),
    time.strftime("%H:%M:%S", time.localtime()),
    tuning_value,
    tuning_it_value,
    failure_value,
    total
        ]

sheet.append_row(data, value_input_option='USER_ENTERED')
