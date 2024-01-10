import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import RPi.GPIO as GPIO  # 追加: GPIO モジュールのインポート

# Google Sheets APIの認証情報をロード
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("path/to/your/credentials.json", scope)
gc = gspread.authorize(credentials)

# Google Sheetsのスプレッドシートキーを指定
spreadsheet_key = "elemental-axle-404504-ac76119fad9c"
worksheet_title = "dht11_spreadsheet"  # シートのタイトルを指定

# シートを開く
worksheet = gc.open_by_key(spreadsheet_key).worksheet(worksheet_title)

def collect_data(channel):
    # ここにデータ収集のコードを追加
    # 例: temperature, humidity = read_temperature_and_humidity(channel)
    data = []
    j = 0

    GPIO.setup(channel, GPIO.OUT)

    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(channel, GPIO.HIGH)

    GPIO.setup(channel, GPIO.IN)

    while GPIO.input(channel) == GPIO.LOW:
        continue

    while GPIO.input(channel) == GPIO.HIGH:
        continue

    while j < 40:
        k = 0
        while GPIO.input(channel) == GPIO.LOW:
            continue

        while GPIO.input(channel) == GPIO.HIGH:
            k += 1
            if k > 100:
                break

        if k < 8:
            data.append(0)
        else:
            data.append(1)

        j += 1

    return data

try:
    while True:
        GPIO.setmode(GPIO.BCM)
        channel = 18  # チャンネルを定義

        # ...（中略）...

        # 60秒待機（1分ごとにデータを更新）
        time.sleep(60)

except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Exiting.")
finally:
    GPIO.cleanup()
