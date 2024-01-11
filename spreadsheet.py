#!/usr/bin/env python3

import os
import time
import pickle
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = '16rgnCIIEmjWwqkg_9WjHKy-hde8Atj_pVLx9f6Y-iJs'  # ここにGoogle SheetsのスプレッドシートのIDを入力
SERVICE_ACCOUNT_FILE = 'elemental-axle-404504-ac76119fad9c'  # サービスアカウントのJSONファイルへのパス

def authenticate_google_sheets():
    creds = None
    # サービスアカウントを使用した認証
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

        values = [temperature_data]

        body = {'values': values}
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1',  # 適切な範囲を指定するか、新しいシートを作成してデータを書き込む
            valueInputOption='RAW',
            body=body
        ).execute()
        print('Data written to Google Sheets:', result)
    except Exception as e:
        print('Error writing to Google Sheets:', e)
    
# 以下、readSensor関数を変更して、温度データをGoogle Sheetsに書き込むようにします
def readSensor(id):
    tfile = open("/sys/bus/w1/devices/"+id+"/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature / 1000
    print("Sensor: " + id + " - Current temperature : %0.3f C" % temperature)

    # 温度データをGoogle Sheetsに書き込む
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

if __name__ == "__main__":
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
