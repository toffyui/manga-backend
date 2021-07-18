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


# 漫画化フィルタ（エフェクトなし）
def manga_filter(src, screen, th1=60, th2=150):
    
    # グレースケール変換
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    # スクリーントーン画像を入力画像と同じ大きさにリサイズ
    screen = cv2.resize(screen,(gray.shape[1],gray.shape[0]))

    # Cannyアルゴリズムで輪郭検出し、色反転
    edge = 255 - cv2.Canny(gray, 80, 120)


    # 三値化
    gray[gray <= th1] = 0
    gray[gray >= th2] = 255
    gray[ np.where((gray > th1) & (gray < th2)) ] = screen[ np.where((gray > th1)&(gray < th2)) ]

    supergray = cv2.bitwise_and(gray, edge)

    return supergray

# 背景エフェクトをつける
def back_filter(src, manga, effect, th):
    # グレースケール変換
    img = cv2.bitwise_not(src)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    effect = cv2.cvtColor(effect, cv2.COLOR_BGR2GRAY)

    # スクリーントーン画像を入力画像と同じ大きさにリサイズ
    effect = cv2.resize(effect,(img_gray.shape[1],img_gray.shape[0]))

    # 2値化
    ret, img_binary = cv2.threshold(img_gray, th, 255,cv2.THRESH_BINARY)

    # # 輪郭抽出する。
    contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # # 面積が最大の輪郭を取得する
    contour = max(contours, key=lambda x: cv2.contourArea(x))

    mask = np.zeros_like(img_binary)
    cv2.drawContours(mask, [contour], -1, color=255, thickness=-1)
    effect = np.where(mask == 0, effect, manga)

    # 三値画像と輪郭画像を合成
    return effect

# フロントエフェクト
def front_filter(manga, effect):
    
    effect = cv2.resize(effect,(manga.shape[1], manga.shape[0]))
    #マスク画像作成
    mask = effect[:,:,3]

    # エフェクトをグレースケール化
    effect = cv2.cvtColor(effect, cv2.COLOR_BGR2GRAY)
    
    # 三値画像と輪郭画像を合成
    manga = np.where(mask == 0, manga, effect)
    return manga


# eventでjsonを受け取る { 'img': base64img, 'back_effect': number, 'front_effect': number }
def handler(event, context):
    # eventに辞書型に変化されて保存されている
    base_64ed_image = event.get('img', 'none')
    back_effect = event.get('back_effect', 'none')
    front_effect = event.get('front_effect', 'none')

    # 入力画像をcv2で扱える形式に変換
    cvimg = base64_to_cv2(base_64ed_image)

    #トーン画像を読み込み
    screen = cv2.imread('images/screen.png')
    
    # 漫画化
    manga = manga_filter(cvimg, screen, 70, 120)
    
    # 背景エフェクトがあれば適用する
    if back_effect == 'none':
        pass
    else:
        back_effect_name = 'images/back_effects/{}.jpg'.format(str(back_effect))
        back_img = cv2.imread(back_effect_name)
        manga = back_filter(cvimg, manga, back_img, 70)

    # 全面エフェクトがあれば適用する
    if front_effect == 'none':
        pass
    else:
        front_effect_name = 'images/front_effects/{}.png'.format(str(front_effect))
        front_img = cv2.imread(front_effect_name, -1)
        manga = front_filter(manga, front_img)

    manga = cv2_to_base64(manga)
    
    # 表示ようにcv2画像のまま返す
    return {"image": manga}
