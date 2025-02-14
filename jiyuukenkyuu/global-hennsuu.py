### 値の保存にグローバル変数を使う例
###（概念を説明するための例であり、そのままでは動作しません）
## 参考:［解決！Python］global文で変数がグローバルであると宣言するには：解決！Python - ＠IT
## https://atmarkit.itmedia.co.jp/ait/articles/2310/10/news013.html

import machine
import utime
from dfplayer import DFPlayer

# チェック間隔を設定（秒）
INTERVAL = 300 

# いろいろ初期化
rain_led = machine.Pin(8, machine.Pin.OUT)
df = DFPlayer(uart_id=0,tx_pin_id=12,rx_pin_id=13)

# 【rain をグローバル変数としてゼロで作成】
rain = 0

# 降雨＆鉄道チェック処理
def main():
    # 【グローバル変数 rain へ書き込めるようにする＝１回のチェックが済んでも雨量を忘れない】
    global rain
    
    # 以前の雨量を rain から取得して prev_rain にコピーしておく (prev は previous の略)
    # prev_rain は前回との比較用に使うだけなので、ローカル変数（ここでは main() の中でのみ有効＝1回のチェックごとに忘れる）として作成
    prev_rain = rain 

    # rain を最新の降水量に更新
    url = 'https://map.yahooapis.jp/weather/~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    json_data = urequests.get(url)
    ## この rain は main() の冒頭で global 宣言をしたので、今回のチェックが終わっても忘れない
    rain = json_data.json().get('Feature')[0].get('Property').get('WeatherList').get('Weather')[0].get('Rainfall')

    # 状況判定とアラーム動作
    if rain > 0: # 雨量 rain が 0 "より大きい" 場合(★)
        rain_led.on() # 雨ランプ光る
        if prev_rain == 0: # ★かつ、以前の雨量 prev_rain が 0 だった場合
            df.play(1,1) # 鳴る
    else: # ★以外の場合
        rain_led.off() # 雨ランプ消す


# メインループ
while True:
    main() # 降雨＆鉄道チェック
    utime.sleep(INTERVAL) # 指定時間待機