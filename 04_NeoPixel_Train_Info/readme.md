# サンプル04_NeoPixel と Raspberry Pi Pico W で Yahoo! 運行情報おしらせ灯をつくろう

## できること
指定した路線の運行状況を Yahoo! 運行情報から取得して、LED ライトで知らせる。 

赤　運転見合わせ
黄　遅延・その他
緑　平常運行

## 必要なもの
・Raspberry Pi Pico W
・NeoPixel (本サンプルでは秋月電子のマイコン内蔵RGBLEDモジュール AE-WS2812B を使用)
・その他配線パーツ（ブレッドボード、ジャンプワイヤ、ピンヘッダ1x20を2本 など）

## ハードウェア構築
配線はサンプル03と同じです。
![配線図](https://github.com/user-attachments/assets/62dce2c3-d421-4cd9-8903-2a711e0763c0)

## ソフトウェア構築
サンプルコード main.py のコメントを参照ください。

