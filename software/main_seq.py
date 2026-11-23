# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) OTON GLASS Inc.
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
- Google Cloud の API キー（Vision API と Text-to-Speech API を有効にしたもの）を、このファイルと同じフォルダの api_key.txt に1行で書いたもの

動かし方
--------
    python3 ~/photonglass/main_seq.py
（どのフォルダから実行しても動きます。音声ファイルや api_key.txt は、このファイルがあるフォルダから探します）
電源を入れると自動で動く設定にしている場合は、先にそちらを止めてから実行します
（同時に2つ動かすと、カメラが「使用中」になって動きません）。
    sudo systemctl stop photonglass     … 自動で動いている方を止める
    sudo systemctl start photonglass    … 試し終わったら、自動の方を動かし直す
"""

##### APIキーの設定 #####
# Google Cloud で作った API キーは、プログラムには書きません。
# このファイルと同じフォルダにある api_key.txt に、キーを1行で書きます（見本：api_key.txt.example）。
# 起動したときに読み込み、ファイルがない・空のときは、エラーを知らせて終了します。
# 注意：api_key.txt を GitHub などで公開しないでください。
#       他人に使われて、利用料金が請求されることがあります。
API_KEY_FILE = "api_key.txt"  # API キーを書くファイルの名前
api_key = None                # 起動したときに API_KEY_FILE から読み込んだキーを入れる


##### 準備 #####
from gpiozero import LED          # Raspberry Pi のピン（GPIO）で LED を扱うライブラリ
from gpiozero import Button       # 同じく、ボタンを扱うライブラリ
from picamera2 import Picamera2   # Raspberry Pi のカメラを扱うライブラリ
import requests                   # インターネット経由で API と通信するため
import subprocess                 # 別のプログラム（aplay）を動かすため
import base64                     # 画像や音声を、通信で送れる文字列に変換するため
import time                       # 待ち時間を作るため
import asyncio                    # このプログラムでは使っていない（非同期版の名残）
import os                         # ファイルの場所を調べるため（api_key.txt や音声ファイルを探す）
import sys                        # エラーのときにプログラムを終了するため

# このプログラムがあるフォルダ。音声ファイル・写真・読み上げ音声は、ここを基準にする
# （どのフォルダから実行しても、同じ場所を使うようにするため）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 音声ファイルの場所（このプログラムがあるフォルダの中の sound フォルダ）
SOUND_DIR = os.path.join(BASE_DIR, "sound")
START_SOUND = os.path.join(SOUND_DIR, "start.wav")                  # 起動したとき
TRIGGER_SOUND = os.path.join(SOUND_DIR, "trigger.wav")              # カメラボタンを押したとき（シャッター音）
CONNECT_SOUND = os.path.join(SOUND_DIR, "connect.wav")              # 通信中
OK_SOUND = os.path.join(SOUND_DIR, "ok.wav")                        # 文字が読み取れて、これから読み上げるとき
NO_SOUND = os.path.join(SOUND_DIR, "no.wav")                        # 写真に文字が見つからなかったとき
FINISH_SOUND = os.path.join(SOUND_DIR, "finish.wav")                # 読み上げが終わったとき
CAMERA_ERROR_SOUND = os.path.join(SOUND_DIR, "camera_error.wav")    # カメラのエラー
NETWORK_ERROR_SOUND = os.path.join(SOUND_DIR, "network_error.wav")  # 通信のエラー（Wi-Fi が切れた、API キーが無効など）

IMAGE_FILE = os.path.join(BASE_DIR, "image.jpg")    # 撮った写真の保存先
SPEECH_FILE = os.path.join(BASE_DIR, "speech.wav")  # 読み上げ音声の保存先

# 音を出す先：スピーカー基板（hifiberry-dac）に直接送る。
# デスクトップの音声設定（右上のアイコン）に関係なく、SSH から実行しても同じスピーカーから鳴る。
# スピーカー基板が見つからないときは、Raspberry Pi の標準の出力を使う。
try:
    with open("/proc/asound/cards") as cards:
        has_speaker = "sndrpihifiberry" in cards.read()
except OSError:
    has_speaker = False
AUDIO_DEVICE = ["-D", "plughw:CARD=sndrpihifiberry"] if has_speaker else []

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
        ["aplay", "-q"] + AUDIO_DEVICE + [path],  # -q：余計なメッセージを表示しない
        stdout=subprocess.DEVNULL,    # 画面への出力は捨てる
        stderr=subprocess.DEVNULL
    )


##### APIキーの読み込み #####

def load_api_key():
    """api_key.txt から API キーを読み込んで返す。

    api_key.txt は、このプログラムのファイルと同じフォルダから探します
    （どのフォルダから実行しても、同じ api_key.txt を読むようにするため）。
    ファイルの中の空白・改行は取り除きます。
    読み込めなかったとき（ファイルがない・中身が空）は、理由を表示して None を返します。
    """
    path = os.path.join(BASE_DIR, API_KEY_FILE)

    if not os.path.isfile(path):
        print(f"エラー：API キーのファイルが見つかりません（{path}）")
        print("このプログラムと同じフォルダに api_key.txt を作り、Google Cloud の API キーを1行で書いてください（見本：api_key.txt.example）。")
        return None

    with open(path, encoding="utf-8-sig") as key_file:  # utf-8-sig：先頭に BOM があっても読める
        key = "".join(key_file.read().split())         # 空白・改行をすべて取り除く

    if key == "":
        print(f"エラー：API キーのファイルが空です（{path}）")
        print("api_key.txt に、Google Cloud の API キーを1行で書いてください。")
        return None

    return key


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
    戻り値: 作った音声ファイルの場所（SPEECH_FILE）
    """
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

    with open(SPEECH_FILE, "wb") as audio_file:
        audio_file.write(base64.b64decode(audio_content))

    return SPEECH_FILE


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

# API キーを読み込む。読み込めないとき（ファイルがない・空）は、エラーを知らせて終了する
api_key = load_api_key()
if api_key is None:
    errorLed()
    play_wav(NETWORK_ERROR_SOUND)  # 通信のエラーの音（API キーが無効なときと同じ）
    wait_wav()
    sys.exit(1)

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
            camera.capture_file(IMAGE_FILE)

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
            text = vision_api(IMAGE_FILE)    # 文字を読み取る
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
