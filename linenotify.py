#!/usr/bin/env python3

import os
import time
from datetime import datetime
import pickle
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import requests  # 追加

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = '16rgnCIIEmjWwqkg_9WjHKy-hde8Atj_pVLx9f6Y-iJs'
SERVICE_ACCOUNT_FILE = 'elemental-axle-404504-ac76119fad9c.json'
LINE_NOTIFY_TOKEN = '7r1zTM6lJHWBuzNTFGpUr8VhQoOIcVb37at8dslWggS'  # ここに自分のLINE Notifyのトークンを入力

def authenticate_google_sheets():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        try:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        except Exception as e:
            print('Error authenticating with Service Account:', e)
            creds = None
    return creds

def write_to_google_sheets(temperature_data):
    try:
        creds = authenticate_google_sheets()
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temperature_data_with_timestamp = [timestamp] + temperature_data

        values = [temperature_data_with_timestamp]

        body = {'values': values}
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1',
            valueInputOption='RAW',
            body=body
        ).execute()
        print('Data written to Google Sheets:', result)

        # 温度が18度以下の場合にLINE Notifyで通知を送る
        if float(temperature_data[1]) <= 18:
            send_line_notify(f"Temperature is below 18°C: {temperature_data[1]}°C")

    except Exception as e:
        print('Error writing to Google Sheets:', e)

def readSensor(id):
    tfile = open("/sys/bus/w1/devices/"+id+"/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature / 1000
    print("Sensor: " + id + " - Current temperature : %0.3f C" % temperature)

    temperature_data = [id, temperature]
    write_to_google_sheets(temperature_data)

def readSensors():
    count = 0
    sensor = ""
    for file in os.listdir("/sys/bus/w1/devices/"):
        if file.startswith("28-"):
            readSensor(file)
            count += 1
    if count == 0:
        print("No sensor found! Check connection")

def loop():
    while True:
        readSensors()
        time.sleep(2)

def destroy():
    pass

def send_line_notify(message):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}
    payload = {'message': message}
    requests.post(line_notify_api, headers=headers, data=payload)

if __name__ == "__main__":
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
