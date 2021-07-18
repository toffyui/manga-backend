import json
import cv2
import base64
import numpy as np

def base64_to_cv2(image_base64):
    # base64 image to cv2
    image_bytes = base64.b64decode(image_base64)
    np_array = np.fromstring(image_bytes, np.uint8)
    image_cv2 = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image_cv2

def cv2_to_base64(image_cv2):
    # cv2 image to base64
    image_bytes = cv2.imencode('.jpg', image_cv2)[1].tostring()
    image_base64 = base64.b64encode(image_bytes).decode()
    return image_base64


# 漫画化フィルタ
def manga_filter(src, screen, th1, th2, effect):
    
    # グレースケール変換
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    effect = cv2.cvtColor(effect, cv2.COLOR_BGR2GRAY)

    # スクリーントーン画像を入力画像と同じ大きさにリサイズ
    screen = cv2.resize(screen,(gray.shape[1],gray.shape[0]))
    effect = cv2.resize(effect,(gray.shape[1],gray.shape[0]))

    # Cannyアルゴリズムで輪郭検出し、色反転
    edge = 255 - cv2.Canny(gray, 80, 120)

    # 三値化
    gray[gray <= th1] = 0
    gray[gray >= th2] = 255
    gray[ np.where((gray > th1) & (gray < th2)) ] = screen[ np.where((gray > th1)&(gray < th2)) ]

    # 三値画像と輪郭画像を合成
    manga_image = cv2.bitwise_and(gray, edge)
    return cv2.bitwise_and(effect, manga_image)

# eventでjsonを受け取る { 'img': base64img, 'style': string }
def handler(event, context):
    input_img = event['img'] #画つ目の像を読み出しオブジェクトtrimed_imgに代入
    effect_cv = cv2.imread('effects/{}.jpg'.format(event['style']))
    input_img = base64_to_cv2(input_img)
    screen_image = cv2.imread('effects/screen.png')
    result = manga_filter(input_img, screen_image, 70, 140, effect_cv)
    result = cv2_to_base64(result)
    
    return {'data': result}

