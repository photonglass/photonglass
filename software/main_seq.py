# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2019-2026 OTON GLASS open hardware contributors
"""
PHOTON GLASS 本体プログラム（逐次版）
===================================

カメラボタンを押すと、メガネのカメラで写真を撮り、写っている文字を読み上げます。

処理の流れ
----------
1. カメラボタンを押す → 写真を撮る（image.jpg）
2. Google Cloud Vision API に写真を送り、文字を読み取ってもらう（OCR）
3. 読み取った文字を Google Cloud Text-to-Speech API に送り、音声（speech.wav）にしてもらう
4. スピーカーから音声を流す

「逐次版」とは
--------------
上の1〜4を、1つずつ順番に（前の処理が終わるのを待ってから次へ）進めます。
仕組みが単純で読みやすい代わりに、処理の途中ではボタンを受け付けません
（読み上げを途中で止める、撮り直す、はできません）。
途中で止めたい場合は、非同期版 main_async.py を使います。

LED の色の意味
--------------
- 緑：待機中（ボタンを押せる）
- 黄（赤＋緑）：通信中
- 青：読み上げ中
- 赤：エラー

必要なもの
----------
- Raspberry Pi Zero 2 W ＋ PHOTON GLASS メイン基板・カメラ基板
- Python のライブラリ：gpiozero, picamera2, requests
  （例：sudo apt install python3-gpiozero python3-picamera2 python3-requests）
- 音声を再生するコマンド aplay（Raspberry Pi OS に最初から入っています）
- Google Cloud の API キー（Vision API と Text-to-Speech API を有効にしたもの）

動かし方
--------
このファイルと sound フォルダがある場所に移動してから実行します。
    cd software          # リポジトリの場合
    cd ~/photonglass     # docs/SETUP_RASPBERRY_PI.md の手順で Raspberry Pi にコピーした場合
    python3 main_seq.py
（音声ファイルの場所を「今いるフォルダから数えて」指定しているため、別の場所から実行すると音が出ません）
"""

##### APIキーの設定 #####
# Google Cloud で作った API キーをここに書きます。
# 注意：キーを書き込んだファイルを GitHub などで公開しないでください。
#       他人に使われて、利用料金が請求されることがあります。
api_key = "YOUR API KEY"


##### 準備 #####
from gpiozero import LED          # Raspberry Pi のピン（GPIO）で LED を扱うライブラリ
from gpiozero import Button       # 同じく、ボタンを扱うライブラリ
from picamera2 import Picamera2   # Raspberry Pi のカメラを扱うライブラリ
import requests                   # インターネット経由で API と通信するため
import subprocess                 # 別のプログラム（aplay）を動かすため
import base64                     # 画像や音声を、通信で送れる文字列に変換するため
import time                       # 待ち時間を作るため
import asyncio                    # このプログラムでは使っていない（非同期版の名残）
import httpx                      # このプログラムでは使っていない（非同期版の名残）

# 音声ファイルの場所（このプログラムを実行したフォルダから数えた場所）
START_SOUND = "sound/start.wav"                  # 起動したとき
TRIGGER_SOUND = "sound/trigger.wav"              # カメラボタンを押したとき（シャッター音）
CONNECT_SOUND = "sound/connect.wav"              # 通信中
OK_SOUND = "sound/ok.wav"                        # 文字が読み取れて、これから読み上げるとき
NO_SOUND = "sound/no.wav"                        # 写真に文字が見つからなかったとき
FINISH_SOUND = "sound/finish.wav"                # 読み上げが終わったとき
CAMERA_ERROR_SOUND = "sound/camera_error.wav"    # カメラのエラー
NETWORK_ERROR_SOUND = "sound/network_error.wav"  # 通信のエラー（Wi-Fi が切れた、API キーが無効など）

# GPIO（ピン）の設定
# 数字は GPIO の番号です（40ピンヘッダの「ピン番号」とは違うので注意）。
# 2026年版の基板では RGB LED の部品を替えたため、色とピンの対応が元の基板から変わっています。
#   GPIO9 = 赤、GPIO11 = 緑、GPIO10 = 青
redLED = LED(9)
greenLED = LED(11)
blueLED = LED(10)
cameraButton = Button(17)  # カメラボタン（カメラユニットのボタン）：撮影して読み上げる
mainButton = Button(27)    # メインボタン：このプログラムでは使っていない
subButton = Button(22)     # サブボタン：このプログラムでは使っていない
upButton = Button(23)      # 上ボタン：このプログラムでは使っていない
downButton = Button(24)    # 下ボタン：このプログラムでは使っていない

# 再生中の音声プログラム（aplay）を入れておく変数。
# いくつかの関数から共通で使うので、関数の外（グローバル変数）に置いている。
# 関数の中で書き換えるときは、その関数で global と宣言する必要がある。
wavplayer_proc = None


##### 音声再生 #####
# 音声の再生には、Raspberry Pi OS に入っている aplay コマンドを使います。
# 同時に鳴らせるのは1つだけです（新しく鳴らすと wavplayer_proc が上書きされる）。

def stop_wav():
    """再生中の音を止める。"""
    global wavplayer_proc
    # poll() が None ＝ まだ再生中
    if wavplayer_proc is not None and wavplayer_proc.poll() is None:
        wavplayer_proc.terminate()  # 「止まって」とお願いする
        try:
            wavplayer_proc.wait(timeout=1)  # 1秒以内に止まるのを待つ
        except subprocess.TimeoutExpired:
            wavplayer_proc.kill()  # 止まらなかったら強制的に終わらせる


def wait_wav():
    """再生中の音が最後まで鳴り終わるのを待つ。"""
    global wavplayer_proc
    if wavplayer_proc is not None and wavplayer_proc.poll() is None:
        wavplayer_proc.wait()


def play_wav(path):
    """音声ファイル（.wav）の再生を始める（終わるのは待たない）。"""
    global wavplayer_proc
    wavplayer_proc = subprocess.Popen(
        ["aplay", "-q", path],        # -q：余計なメッセージを表示しない
        stdout=subprocess.DEVNULL,    # 画面への出力は捨てる
        stderr=subprocess.DEVNULL
    )


##### API #####
# Google Cloud の API とのやりとりです。
# うまくいかなかったときは、次の2種類のエラーを「呼び出し元」に知らせます（raise）。
#   requests.exceptions.RequestException：通信の失敗（Wi-Fi が切れた、時間切れ、API キーが無効など）
#   ValueError                          ：写真の中に文字が見つからなかった

def vision_api(img):
    """写真を Vision API に送り、写っている文字を返す（OCR）。

    img: 写真ファイルの場所
    戻り値: 読み取った文字（改行を含む1つの文字列）
    """
    # 写真を読み込み、通信で送れる文字列（base64）に変換する
    with open(img, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode("utf-8")

    url = "https://vision.googleapis.com/v1/images:annotate?key=" + api_key
    headers = {
        "Content-Type": "application/json"
    }
    # 送る内容：「この画像の文字を読み取って（TEXT_DETECTION）」
    payload = {
        "requests": [
            {
                "image": {
                    "content": image_content
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION"
                    }
                ]
            }
        ]
    }

    # 送信して、返事を待つ（最大20秒）。
    # Wi-Fi が切れている・時間切れなどの場合は、ここで RequestException の仲間のエラーが起きる。
    response = requests.post(url, headers=headers, json=payload, timeout=20)

    # API が「失敗」を返した場合（API キーが無効、課金が無効、利用上限など）も、通信エラーとして扱う
    if response.status_code != 200:
        raise requests.exceptions.HTTPError

    # 返事の中から、読み取った文字を取り出す
    response_data = response.json()
    texts = response_data["responses"][0].get("textAnnotations", [])

    # 文字が1つも見つからなかった
    if len(texts) <= 0:
        raise ValueError

    # textAnnotations の最初の要素に、画像全体の文字がまとめて入っている
    text = texts[0]["description"]
    return text


def text_to_speech(text):
    """文字を Text-to-Speech API に送り、読み上げ音声のファイルを作る。

    text: 読み上げる文字
    戻り値: 作った音声ファイルの場所（speech.wav）
    """
    SPEECH_SOUND = "speech.wav"
    url = "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + api_key
    headers = {
        "Content-Type": "application/json"
    }
    # 送る内容：読み上げる文字、声の種類（日本語）、音声の形式（wav と同じ LINEAR16）
    payload = {
        "input": {
            "text": text
        },
        "voice": {
            "languageCode": "ja-JP",
            "ssmlGender": "NEUTRAL"
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16"
        }
    }

    # 送信して、返事を待つ（最大20秒）
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError

    # 返事の中の音声（base64 の文字列）を元に戻して、ファイルに保存する
    response_data = response.json()
    audio_content = response_data["audioContent"]

    with open(SPEECH_SOUND, "wb") as audio_file:
        audio_file.write(base64.b64decode(audio_content))

    return SPEECH_SOUND


##### LED #####
# RGB LED の3色の点け方で、今の状態を知らせます。

def readyLed():
    """待機中：緑"""
    redLED.off()
    greenLED.on()
    blueLED.off()


def errorLed():
    """エラー：赤"""
    redLED.on()
    greenLED.off()
    blueLED.off()


def connectLed():
    """通信中：黄（赤と緑を同時に点ける）"""
    redLED.on()
    greenLED.on()
    blueLED.off()


def speechLed():
    """読み上げ中：青"""
    redLED.off()
    greenLED.off()
    blueLED.on()


##### 起動 #####

print("起動！")

# カメラの準備
try:
    camera = Picamera2()
    camera_config = camera.create_still_configuration(
        main={"size": (1920, 1080)}  # 撮影サイズ（横 x 縦）
    )
    camera.configure(camera_config)
    camera.options["quality"] = 90   # JPEG の画質（0〜100）
    camera.start()
    print("カメラOK！")

except Exception:
    # カメラが見つからない（ケーブルの抜けなど）：エラー音を鳴らし、赤く光らせたまま止まる
    print("カメラNG...")
    errorLed()
    play_wav(CAMERA_ERROR_SOUND)
    wait_wav()

    while True:
        errorLed()
        time.sleep(1)


# 起動音を5秒だけ流す
play_wav(START_SOUND)
time.sleep(5)
stop_wav()


##### メインループ #####
# 0.05秒ごとにカメラボタンを見て、押されていたら撮影→読み上げを最後まで行う。

while True:
    readyLed()

    if cameraButton.is_pressed:
        play_wav(TRIGGER_SOUND)  # シャッター音

        # 撮影
        try:
            camera.capture_file("image.jpg")

        except Exception:
            errorLed()
            stop_wav()
            play_wav(CAMERA_ERROR_SOUND)
            wait_wav()
            continue  # 待機に戻る

        # シャッター音が鳴り終わるのを待ってから、通信中の音を流す
        wait_wav()
        play_wav(CONNECT_SOUND)
        connectLed()

        try:
            text = vision_api("image.jpg")    # 文字を読み取る
            speech = text_to_speech(text)     # 読み上げ音声を作る

            # 読み上げ：「OK」の音 → 読み上げ音声 → 「終わり」の音
            speechLed()
            stop_wav()  # 通信中の音を止める

            play_wav(OK_SOUND)
            wait_wav()
            play_wav(speech)
            wait_wav()
            play_wav(FINISH_SOUND)
            wait_wav()

        except requests.exceptions.RequestException:  # 通信のエラー
            errorLed()
            stop_wav()
            play_wav(NETWORK_ERROR_SOUND)
            wait_wav()
            continue  # 待機に戻る

        except ValueError:  # 写真に文字がなかった
            errorLed()
            stop_wav()
            play_wav(NO_SOUND)
            wait_wav()
            continue  # 待機に戻る

        # ボタンが離されるまで待つ（押しっぱなしで、もう一度撮影しないように）
        while cameraButton.is_pressed:
            time.sleep(0.05)

    time.sleep(0.05)
