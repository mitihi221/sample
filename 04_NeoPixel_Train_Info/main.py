##### NeoPixel で Yahoo! 運行情報おしらせ灯をつくろう (SAMPLE) ##### 

import network
import utime
from machine import Pin, Timer, ADC
import config
import ure
import urequests
from neopixel import NeoPixel

# NeoPixel 通信ピン設定
NEOPIN = 15 # GP15

# NeoPixel 明るさ調整 (暗 0.1 <--> 1.0 明)
BRIGHTNESS = 0.2

# 運行情報更新間隔（秒）
INTERVAL = 180

########## 無線 LAN 設定 ##########
ssid = config.ssid
password = config.password

########## IP アドレス設定 ##########
dhcp = config.dhcp
# dhcp = True
# dhcp = True の場合は以下の ip, mask, gateway, dns を無視します。
static_ip = config.static_ip
static_mask = config.static_mask
static_gateway = config.static_gateway
static_dns = config.static_dns

########## Wi-Fi 接続処理 ##########
def connect():
    wlan = network.WLAN(network.STA_IF)
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
        utime.sleep(2)
        retry -= 1
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f'\n接続しました。IP アドレスは {ip}')
        WifiConnected = True
        timer.deinit()
        led0.on()
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
        utime.sleep(10)
        machine.soft_reset()   

timer = Timer()
led0 = Pin('WL_GPIO0', Pin.OUT)
def blink(timer):
    led0.toggle()

def main():
    #url = '' # 線
    url = 'https://transit.yahoo.co.jp/diainfo/22/0' # 京浜東北根岸線
    #url = 'https://transit.yahoo.co.jp/diainfo/50/0' # 埼京川越線[羽沢横浜国大～川越]
    #url = 'https://transit.yahoo.co.jp/diainfo/71/0' # 武蔵野線

    # FireFox からのアクセスに偽装
    headers = {
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'
    }

    # 運行状態フラグ初期化
    status = 'undefined'

    try:
        # 運行情報の取得
        html_data = urequests.get(url, headers=headers)
    except Exception as e:
        # ネットワークエラー処理（めんどくさいのでソフトリセットで再起動）
        np[0] = (round(134*BRIGHTNESS), round(0*BRIGHTNESS), round(255*BRIGHTNESS)) # 紫
        np.write()
        utime.sleep(INTERVAL) # 超頻度でリトライしないよう設定間隔秒待つ
        machine.soft_reset() # そふとりせっと
    
    # 平常運転
    match = ure.search('<dd class="normal">', html_data.text)
    if match:
        status = 'normal'
        np[0] = (round(0*BRIGHTNESS), round(255*BRIGHTNESS), round(0*BRIGHTNESS)) # 緑
        np.write()
    
    # 運転見合わせ
    match = ure.search('<dd class="trouble suspend">', html_data.text)
    if match:
        status = 'trouble suspend'
        np[0] = (round(255*BRIGHTNESS), round(0*BRIGHTNESS), round(0*BRIGHTNESS)) # 赤
        np.write()
        
    # 列車遅延・その他
    match = ure.search('<dd class="trouble">', html_data.text)
    if match:
        status = 'trouble'
        np[0] = (round(255*BRIGHTNESS), round(185*BRIGHTNESS), round(0*BRIGHTNESS)) # 黄
        np.write()
        
    # 状況不明（サイト構造の変化などにより状況の取得ができない状態）
    if status == 'undefined':
        np[0] = (round(134*BRIGHTNESS), round(0*BRIGHTNESS), round(255*BRIGHTNESS)) # 紫
        np.write()        
                
    # サーバーの HTTP レスポンスコードを Thonny に表示 (200 = OK)
    print(html_data.status_code)
    # 運行状況を Thonny に表示
    print('運行状況: '+status)
    
################# End of Main() #################

# NeoPixel 初期化
pin = Pin(NEOPIN, Pin.OUT)  
np = NeoPixel(pin, 1)   
np[0] = (0, 0, 0)
np.write()

# 起動時 LED テスト
led0.on()
np[0] = (round(255*BRIGHTNESS), round(255*BRIGHTNESS), round(255*BRIGHTNESS)) # 白
np.write()
utime.sleep(1)
led0.off()
np[0] = (0, 0, 0)
np.write()
utime.sleep(1)

timer.init(freq=1.8, mode=Timer.PERIODIC, callback=blink)
ip = connect()
utime.sleep(1)

while True:
    # 設定間隔で運行情報を取りに行く
    main()
    utime.sleep(INTERVAL)
