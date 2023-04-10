# -*- coding: utf-8 -*-
# Raspberrry Pi Pico W - #01 WEB サービスはじめの一歩 サンプル
# https://projects.raspberrypi.org/en/projects/get-started-pico-w/ をベースに作成しました。
# ・Wi-Fi 接続試行中は LED ゆっくり点滅、エラー発生時は LED 素早く点滅　を追加しました。
# ・Wi-Fi 切断チェックを追加しました。（10秒ごとにチェックして切断されていたら再起動→再接続）

import network
import socket
from time import sleep
import machine
from machine import Timer
from picozero import pico_temp_sensor, pico_led

########## 無線 LAN 設定 ##########
ssid = 'ESSID'
password = 'p@suwaad0'

########## IP アドレス設定 ##########
dhcp = False
# dhcp = True
# dhcp = True の場合は以下の ip, mask, gateway, dns を無視します。
static_ip = '192.168.1.81'
static_mask = '255.255.255.0'
static_gateway = '0.0.0.0'
static_dns = '0.0.0.0'


########## Wi-Fi 接続処理 ##########
mac = ""
WifiConnected = False
def connect():
    global wlan
    global WifiConnected
    wlan = network.WLAN(network.STA_IF)
    global mac
    mac = wlan.config('mac').hex().upper()
    print(f'MACアドレスは {mac}')
    wlan.active(True)
    print(f'Wi-Fi "{ssid}" へ接続しています...', end='')
    wlan.connect(ssid, password)
    if dhcp == False:
        wlan.ifconfig((static_ip, static_mask, static_gateway, static_dns))
    retry = 10
    while (wlan.isconnected() == False) and (retry > 0):
        print('.', end='')
        WLANstatus = wlan.status()
        sleep(2)
        retry -= 1
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f'\n接続しました。IP アドレスは {ip}')
        WifiConnected = True
        timer.deinit()
        timer2.init(freq=0.1, mode=Timer.PERIODIC, callback=checkWifi)
        return ip
    else:
        timer.deinit()
        timer.init(freq=5, mode=Timer.PERIODIC, callback=blink)
        if WLANstatus == 1:
            errmsg = 'パスワードが違います。'
        elif WLANstatus == -2:
            errmsg = 'アクセスポイントが見つからないか、応答がありません。'
        else:
            errmsg = f'その他のエラー({WLANstatus})'
        print(f'\n【エラー】Wi-Fi 接続に失敗しました: {errmsg}')
        WifiConnected = False
        sleep(10)
        machine.reset()   


########## ソケットを開く処理 ##########
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection


########## WEB コンテンツ生成 ##########
def webpage(temperature, state, macaddr):
    # HTML テンプレ
    # ・スマホだと小さくなりすぎてしまうので、<meta name="viewport" content="width=240"> を追加しました。
    # ・端末特定のために MAC アドレス表示を追加しました。
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <meta name="viewport" content="width=240">
            </head>
            <body>
            <form action="./lighton">
            <input type="submit" value="LED ON" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="LED OFF" />
            </form>
            <p>LED は {state}</p>
            <p>温度は {temperature} 度</p>
            <p>MAC アドレスは {macaddr}</p>
            </body>
            </html>
            """
    return str(html)


########## WEB サーバー稼働処理 ##########
def serve(connection):
    global WifiConnected
    state = '点灯'
    pico_led.on()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = '点灯'
        elif request == '/lightoff?':
            pico_led.off()
            state = '消灯'
        temperature = pico_temp_sensor.temp
        print(request)
        global mac
        html = webpage(temperature, state, mac)
        client.send(html)
        client.close()


########## 内蔵 LED 点滅処理 ##########
led = machine.Pin('WL_GPIO0', machine.Pin.OUT)
timer = Timer()
def blink(timer):
    led.toggle()


########## WI-Fi 切断検出処理 ##########
timer2 = Timer()
def checkWifi(timer2):
    if wlan.isconnected() == False:
        print('【エラー】Wi-Fi が切断されました。')
        WifiConnected = False
        machine.reset()



########## メイン プログラム ##########
try:
    # よくある電源投入時に LED がちょっとだけ全点灯するやつ
    led.on()
    sleep(1)
    led.off()
    sleep(1)
    timer.init(freq=1.8, mode=Timer.PERIODIC, callback=blink)

    # Wi-Fi 接続して IP アドレスを取得
    ip = connect()
    sleep(1)
    
    # 取得した IP アドレスでソケットを開く 
    connection = open_socket(ip)
    sleep(1)

    # 開いたソケットで、クライアントからの接続を待って応答する
    serve(connection)

except KeyboardInterrupt:
    # machine.reset()
    # 公式サンプルは Thonny の停止ボタンを押した時に不安定になるので、何もしないに変更
    pass


