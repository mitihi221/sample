# 降水量色分け点灯例（気象庁ナウキャスト区分 https://www.jma.go.jp/bosai/nowc/）
# RGB-LED (NeoPixel) が np として割り当て済みで、2個目を増設した状態と仮定し、点灯制御をするサンプルコードです

if rain >= 80:
    np[1] = (255, 0, 255) # 紫
elif rain >= 50: 
    np[1] = (255, 0, 0) # 赤
elif rain >= 30:
    np[1] = (255, 128, 0) # 橙
elif rain >= 20:
    np[1] = (255, 255, 0) # 黄
elif rain >= 10:
    np[1] = (0, 0, 255) # 濃い青
elif rain >= 5:
    np[1] = (0, 128, 255) # 薄い青
elif rain >= 1:
    np[1] = (0, 255, 255) # 濃い水色
elif rain > 0:
    np[1] = (128, 255, 255) # 薄い水色
else: 
    np[1] = (0, 0, 0) # 消灯

np.write() # NeoPixel に送信
