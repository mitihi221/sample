import network
import socket
from time import sleep, sleep_ms
import machine
from machine import Pin, Timer, ADC
from picozero import pico_temp_sensor, pico_led
import urequests
import utime

import secrets
ssid = secrets.ssid
password = secrets.password
LINE_token = secrets.LINE_token

dhcp = True
static_ip = '192.168.1.81'
static_mask = '255.255.255.0'
static_gateway = '0.0.0.0'
static_dns = '0.0.0.0'

button1_pin = 19
debounce = 0
def button1_onClick(button1):
    global debounce
    if debounce+100 < utime.ticks_ms():
        print('Button1 Click')
        if WifiConnected == True:
            alert_led.on()
            pushLINE('てすと&stickerPackageId=8515&stickerId=16581242')
            alert_led.off()
        debounce = utime.ticks_ms()


led = machine.Pin('WL_GPIO0', machine.Pin.OUT)
timer = Timer()
def blink(timer):
    led.toggle()


alert_led = machine.Pin(22, machine.Pin.OUT)
timer4 = Timer()
def alert(timer4):
    alert_led.toggle()
    
timer5 = Timer()
def stop_alert(timer5):
    alert_led.off()
    timer4.deinit()

timer2 = Timer()
def checkWifi(timer2):
    if wlan.isconnected() == False:
        print('【エラー】Wi-Fi が切断されました。')
        WifiConnected = False
        machine.reset()

mac = ""
WifiConnected = False
def connect():
    # WiFi 接続
    global wlan
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
        global WifiConnected
        WifiConnected = True
        timer.deinit()
        timer2.init(freq=0.1, mode=Timer.PERIODIC, callback=checkWifi)
        timer3.init(freq=100, mode=Timer.PERIODIC, callback=adc_read)
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
        global WifiConnected
        WifiConnected = False
        sleep(10)
        machine.reset()   

def open_socket(ip):
    # ソケットを開きます
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection


def webpage(temperature, state, macaddr):
    # HTML テンプレ
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


def pushLINE(message):
    # LINE Notify API Document
    # https://notify-bot.line.me/doc/ja/
    #
    # db4linq/micropython-thailand
    # https://github.com/db4linq/micropython-thailand/blob/master/line_notify.py

    LINE_endpoint = "https://notify-api.line.me/api/notify"
    LINE_header = {'Content-Type':'application/x-www-form-urlencoded', 'Authorization':f'Bearer {LINE_token}'}
    LINE_data = f'message={message}'.encode('utf-8')
    # 送信可能なスタンプリスト
    # https://developers.line.biz/ja/docs/messaging-api/sticker-list/
    # LINE_data = f'message={message}&stickerPackageId=8515&stickerId=16581242'.encode('utf-8')
    print(LINE_data)
    res = urequests.post(url=LINE_endpoint, headers=LINE_header, data=LINE_data)
    print(res.text)
    res.close()


def serve(connection):
    # WEB サーバーを開始
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


adc = machine.ADC(Pin(26))
timer3 = Timer()
repeat_check = 0
# https://docs.arduino.cc/built-in-examples/sensors/Knock
def adc_read(timer3):
    val = adc.read_u16()
#    print(val)
    if val > 768:
        global repeat_check
        if repeat_check+10000 < utime.ticks_ms():
            timer3.deinit()
            timer4.init(freq=4, mode=Timer.PERIODIC, callback=alert)
            timer5.init(period=10000, mode=Timer.ONE_SHOT, callback=stop_alert)
            alert_led.on()
            pushLINE('👈ぴんぽ～ん！')
            repeat_check = utime.ticks_ms()
            timer3.init(freq=100, mode=Timer.PERIODIC, callback=adc_read)
    

# MAIN
led.on()
alert_led.on()
sleep(1)
led.off()
alert_led.off()
sleep(1)
timer.init(freq=1.8, mode=Timer.PERIODIC, callback=blink)
button1 = Pin(button1_pin, Pin.IN, Pin.PULL_UP)
button1.irq(trigger=Pin.IRQ_RISING, handler=button1_onClick)

ip = connect()
sleep(1)
connection = open_socket(ip)
sleep(1)
serve(connection)

