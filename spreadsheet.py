try:
    while True:
        GPIO.setmode(GPIO.BCM)
        channel = 18  # チャンネルを定義

        # データの収集
        data = collect_data(channel)
        print("sensor is working.")
        print(data)

        humidity_bit = data[0:8]
        humidity_point_bit = data[8:16]
        temperature_bit = data[16:24]
        temperature_point_bit = data[24:32]
        check_bit = data[32:40]

        humidity = 0
        humidity_point = 0
        temperature = 0
        temperature_point = 0
        check = 0

        for i in range(8):
            humidity += humidity_bit[i] * 2 ** (7 - i)
            humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
            temperature += temperature_bit[i] * 2 ** (7 - i)
            temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
            check += check_bit[i] * 2 ** (7 - i)

        tmp = humidity + humidity_point + temperature + temperature_point

        if check == tmp:
            print("temperature : ", temperature, ", humidity : ", humidity)
        else:
            print("wrong")
            print("temperature : ", temperature, ", humidity : ", humidity, " check : ", check, " tmp : ", tmp)

        # 現在時刻の取得
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # データをシートに書き込む
        worksheet.append_row([timestamp, temperature, humidity])

        print(f"Data written to Google Sheets: {timestamp} - Temperature: {temperature}, Humidity: {humidity}")

        # 60秒待機（1分ごとにデータを更新）
        time.sleep(60)

except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Exiting.")
finally:
    GPIO.cleanup()
