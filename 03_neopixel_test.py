# 秋月電子 マイコン内蔵RGBLEDモジュール AE-WS2812B てすと
# Raspberry Pi Pico / Pico W 用

from machine import Pin
from neopixel import NeoPixel
import utime

# NeoPixel 通信ピン設定
NEOPIN = 15 # GP15

# 明るさ設定 (0-255: 大きいほど明るい)
BLIGHTNESS = 255

# 速度設定 (0-∞: 色変化時間のウェイトをミリ秒で指定。小さいほど速い)
SPEED = 33

# nilci - pythonで色を連続的に変化させる方法
# https://tori29.jp/blog/export_17
def hsv_to_rgb(h, s, v):
    """ Convert hsv color code to rgb color code.
        Naive implementation of Wikipedia method.
        See https://ja.wikipedia.org/wiki/HSV%E8%89%B2%E7%A9%BA%E9%96%93
        Args:
        h (int): Hue 0 ~ 360
        s (int): Saturation 0 ~ 1
        v (int): Value 0 ~ 1
    """

    if s < 0 or 1 < s:
        raise ValueError("Saturation must be between 0 and 1")
    if v < 0 or 1 < v:
        raise ValueError("Value must be between 0 and 1")

    c = v * s
    h_dash = h / 60
    x = c * (1 - abs(h_dash % 2 - 1))
    rgb_dict = {
        0: (c, x, 0),
        1: (x, c, 0),
        2: (0, c, x),
        3: (0, x, c),
        4: (x, 0, c),
        5: (c, 0, x),
    }
    default = (0, 0, 0)
    rgb = [0, 0, 0]
    for i in range(len(rgb)):
#        rgb[i] = (v - c + rgb_dict.get(int(h_dash), default)[i]) * 255
        rgb[i] = (v - c + rgb_dict.get(int(h_dash), default)[i]) * BLIGHTNESS
    rgb = map(int, rgb)
    return tuple(rgb)


pin = Pin(NEOPIN, Pin.OUT)   # NeoPixel 駆動のための GPIO 15 を出力に設定
np = NeoPixel(pin, 8)   # 8ピクセル用の NeoPixel ドライバーを GPIO 15 で作成
np[0] = (0, 0, 0)
np.write()

while True:
    for i in range(360):
        color = hsv_to_rgb(i, 1, 1)
        r, g, b = color
        np[0] = (r, g, b)
        np.write()
        utime.sleep_ms(SPEED)
