# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2019-2026 OTON GLASS open hardware contributors
"""
OTON GLASS 本体プログラム（非同期版）
=====================================

カメラボタンを押すと、メガネのカメラで写真を撮り、写っている文字を読み上げます。

処理の流れ
----------
1. カメラボタンを押す → 写真を撮る（image.jpg）
2. Google Cloud Vision API に写真を送り、文字を読み取ってもらう（OCR）
3. 読み取った文字を Google Cloud Text-to-Speech API に送り、音声（speech.wav）にしてもらう
4. スピーカーから音声を流す

「非同期版」とは
----------------
asyncio という仕組みを使い、「通信の待ち時間」と「効果音の再生」と「ボタンの見張り」を同時に進めます。
そのため、次のことができます（逐次版 main_seq.py ではできません）。
- 通信を待っている間も、効果音を鳴らし続ける
- 読み上げの途中でカメラボタンを押すと、今の処理をやめて撮り直す
- 読み上げの途中でサブボタンを押すと、読み上げを止める

LED の色の意味
--------------
- 緑：待機中（ボタンを押せる）
- 黄（赤＋緑）：通信中
- 青：読み上げ中
- 赤：エラー

必要なもの
----------
- Raspberry Pi Zero 2 W ＋ OTON GLASS メイン基板・カメラ基板
- Python のライブラリ：gpiozero, picamera2, httpx
  （例：sudo apt install python3-gpiozero python3-picamera2 python3-httpx）
- 音声を再生するコマンド aplay（Raspberry Pi OS に最初から入っています）
- Google Cloud の API キー（Vision API と Text-to-Speech API を有効にしたもの）を、このファイルと同じフォルダの api_key.txt に1行で書いたもの

動かし方
--------
このファイルと sound フォルダがある場所に移動してから実行します。
    cd ~/photonglass
    python3 main_async.py
（音声ファイルの場所を「今いるフォルダから数えて」指定しているため、別の場所から実行すると音が出ません）
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
from gpiozero import LED, Button  # Raspberry Pi のピン（GPIO）で LED とボタンを扱うライブラリ
from picamera2 import Picamera2   # Raspberry Pi のカメラを扱うライブラリ
import subprocess                 # 別のプログラム（aplay）を動かすため
import base64                     # 画像や音声を、通信で送れる文字列に変換するため
import time                       # 経過時間を測るため
import asyncio                    # 複数の処理を同時に進めるため（非同期処理）
import httpx                      # インターネット経由で API と通信するため（非同期に対応）
import os                         # ファイルの場所を調べるため（api_key.txt を探す）
import sys                        # エラーのときにプログラムを終了するため

# 音声ファイルの場所（このプログラムを実行したフォルダから数えた場所）
START_SOUND = "sound/start.wav"                  # 起動したとき
TRIGGER_SOUND = "sound/trigger.wav"              # カメラボタンを押したとき（シャッター音）
CONNECT_SOUND = "sound/connect.wav"              # 通信中（終わるまでくり返し流す）
OK_SOUND = "sound/ok.wav"                        # 文字が読み取れて、これから読み上げるとき
NO_SOUND = "sound/no.wav"                        # 写真に文字が見つからなかったとき
FINISH_SOUND = "sound/finish.wav"                # 読み上げが終わったとき
CAMERA_ERROR_SOUND = "sound/camera_error.wav"    # カメラのエラー
NETWORK_ERROR_SOUND = "sound/network_error.wav"  # 通信のエラー（Wi-Fi が切れた、API キーが無効など）

# GPIO（ピン）の設定
# 数字は GPIO の番号です（40ピンヘッダの「ピン番号」とは違うので注意）。
# 2026年版の基板では RGB LED の部品を替えたため、色とピンの対応が元の基板から変わっています。
#   GPIO9 = 赤、GPIO11 = 緑、GPIO10 = 青
red_LED = LED(9)
green_LED = LED(11)
blue_LED = LED(10)

camera_button = Button(17)  # カメラボタン（カメラユニットのボタン）：撮影して読み上げる
main_button = Button(27)    # メインボタン：このプログラムでは使っていない
sub_button = Button(22)     # サブボタン：読み上げなどを途中で止める
up_button = Button(23)      # 上ボタン：このプログラムでは使っていない
down_button = Button(24)    # 下ボタン：このプログラムでは使っていない


##### LED #####
# RGB LED の3色の点け方で、今の状態を知らせます。

def ready_LED():
    """待機中：緑"""
    red_LED.off()
    green_LED.on()
    blue_LED.off()


def error_LED():
    """エラー：赤"""
    red_LED.on()
    green_LED.off()
    blue_LED.off()


def connect_LED():
    """通信中：黄（赤と緑を同時に点ける）"""
    red_LED.on()
    green_LED.on()
    blue_LED.off()


def speech_LED():
    """読み上げ中：青"""
    red_LED.off()
    green_LED.off()
    blue_LED.on()


##### 音声再生 #####
# 音声の再生には、Raspberry Pi OS に入っている aplay コマンドを使います。
# aplay は別のプログラムとして動くので、再生しながら他の処理を進められます。

async def stop_wav(proc):
    """再生中の音を止める。

    proc: play_wav() が返した「再生中のプログラム」。None なら何もしない。
    """
    if proc is not None:
        proc.terminate()  # 「止まって」とお願いする
        try:
            # 1秒以内に止まるのを待つ
            await asyncio.wait_for(proc.wait(), timeout=1)
        except asyncio.TimeoutError:
            # 止まらなかったら強制的に終わらせる
            proc.kill()
            await proc.wait()


async def play_wav(path):
    """音声ファイル（.wav）の再生を始める。

    再生の終わりは待たずにすぐ戻ります。終わるまで待ちたいときは、
    戻り値に対して await proc.wait() を呼びます。
    """
    proc = await asyncio.create_subprocess_exec(
        "aplay", "-q", path,          # -q：余計なメッセージを表示しない
        stdout=subprocess.DEVNULL,    # 画面への出力は捨てる
        stderr=subprocess.DEVNULL
    )
    return proc


##### APIキーの読み込み #####

def load_api_key():
    """api_key.txt から API キーを読み込んで返す。

    api_key.txt は、このプログラムのファイルと同じフォルダから探します
    （どのフォルダから実行しても、同じ api_key.txt を読むようにするため）。
    ファイルの中の空白・改行は取り除きます。
    読み込めなかったとき（ファイルがない・中身が空）は、理由を表示して None を返します。
    """
    folder = os.path.dirname(os.path.abspath(__file__))  # このプログラムのファイルがあるフォルダ
    path = os.path.join(folder, API_KEY_FILE)

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
#   httpx.HTTPError：通信の失敗（Wi-Fi が切れた、時間切れ、API キーが無効、課金が無効など）
#   ValueError     ：写真の中に文字が見つからなかった

async def vision_api(img):
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
    # Wi-Fi が切れている・時間切れなどの場合は、ここで httpx.HTTPError の仲間のエラーが起きる。
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, json=payload)

    # API が「失敗」を返した場合（API キーが無効、課金が無効、利用上限など）は、
    # httpx.HTTPStatusError（httpx.HTTPError の仲間）を起こして、通信エラーとして扱う。
    # ※以前は raise httpx.HTTPError と書いていたが、このエラーは説明文なしでは作れず、
    #   別のエラーになって「カメラのエラー」の音が鳴っていた。
    response.raise_for_status()

    # 返事の中から、読み取った文字を取り出す
    response_data = response.json()
    texts = response_data["responses"][0].get("textAnnotations", [])

    # 文字が1つも見つからなかった
    if len(texts) <= 0:
        raise ValueError("文字が見つかりませんでした")

    # textAnnotations の最初の要素に、画像全体の文字がまとめて入っている
    text = texts[0]["description"]
    return text


async def text_to_speech(text):
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
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, json=payload)

    # API が「失敗」を返した場合は、通信エラーとして扱う（vision_api と同じ）
    response.raise_for_status()

    # 返事の中の音声（base64 の文字列）を元に戻して、ファイルに保存する
    response_data = response.json()
    audio_content = response_data["audioContent"]

    with open(SPEECH_SOUND, "wb") as audio_file:
        audio_file.write(base64.b64decode(audio_content))

    return SPEECH_SOUND


##### その他の関数 #####

async def cancel_task(task):
    """同時に進めている処理（タスク）を途中で止め、止まるまで待つ。

    task が None、またはもう終わっている場合は何もしない。
    """
    if task is not None and not task.done():
        task.cancel()
        await task


##### 時間がかかる処理（タスク） #####
# ここにある関数は「タスク」として、メインループと同時に動かします。
# 途中で止められたとき（asyncio.CancelledError）は、鳴らしている音を止めてから終わります。

async def play_start_sound():
    """起動音を最後まで流す。"""
    proc = None
    try:
        proc = await play_wav(START_SOUND)
        await proc.wait()

    except asyncio.CancelledError:
        await stop_wav(proc)


async def play_trigger_connect_sound():
    """シャッター音を1回流し、そのあと通信中の音を止められるまでくり返す。"""
    proc = None
    try:
        proc = await play_wav(TRIGGER_SOUND)
        await proc.wait()

        while True:
            proc = await play_wav(CONNECT_SOUND)
            await proc.wait()

    except asyncio.CancelledError:
        await stop_wav(proc)


async def API_and_speech(image):
    """写真から文字を読み取り、読み上げるまでの一連の処理。

    image: 撮った写真ファイルの場所
    """
    proc = None
    # 通信している間、効果音を同時に流しておく
    sound_task = asyncio.create_task(play_trigger_connect_sound())

    connect_LED()
    try:
        try:
            text = await vision_api(image)       # 文字を読み取る
            speech = await text_to_speech(text)  # 読み上げ音声を作る

        except httpx.HTTPError:  # 通信のエラー
            await cancel_task(sound_task)
            error_LED()
            proc = await play_wav(NETWORK_ERROR_SOUND)
            await proc.wait()
            ready_LED()
            return

        except ValueError:  # 写真に文字がなかった
            await cancel_task(sound_task)
            error_LED()
            proc = await play_wav(NO_SOUND)
            await proc.wait()
            ready_LED()
            return

        except Exception:  # それ以外の思いがけないエラー（カメラのエラー扱いにしている）
            await cancel_task(sound_task)
            error_LED()
            proc = await play_wav(CAMERA_ERROR_SOUND)
            await proc.wait()
            ready_LED()
            return

        # 通信がうまくいったので、通信中の音を止める
        await cancel_task(sound_task)

        # 読み上げ：「OK」の音 → 読み上げ音声 → 「終わり」の音
        speech_LED()
        proc = await play_wav(OK_SOUND)
        await proc.wait()
        proc = await play_wav(speech)
        await proc.wait()
        proc = await play_wav(FINISH_SOUND)
        await proc.wait()

        ready_LED()

    except asyncio.CancelledError:
        # ボタンが押されて途中で止められたとき：音をすべて止めて待機に戻る
        await cancel_task(sound_task)
        await stop_wav(proc)
        ready_LED()
        return


##### メインループ #####

async def main():
    global api_key  # 関数の外の api_key に、読み込んだキーを入れるため
    print("起動！")

    # API キーを読み込む。読み込めないとき（ファイルがない・空）は、エラーを知らせて終了する
    api_key = load_api_key()
    if api_key is None:
        error_LED()
        proc = await play_wav(NETWORK_ERROR_SOUND)  # 通信のエラーの音（API キーが無効なときと同じ）
        await proc.wait()
        sys.exit(1)

    # OS が落ち着くまで少し待った方がよいかもしれない

    # 起動音を鳴らし始めた時刻（5秒たったら起動音を止めるため）
    timer1_start = time.perf_counter()

    # 起動音を、カメラの準備と同時に流す
    start_sound_task = asyncio.create_task(play_start_sound())

    # カメラの準備
    try:
        camera = Picamera2()
        camera_config = camera.create_still_configuration(
            main={"size": (1920, 1080)}  # 撮影サイズ（横 x 縦）
        )
        camera.configure(camera_config)
        camera.options["quality"] = 90   # JPEG の画質（0〜100）
        camera.start()
        camera.capture_file("image.jpg")  # 試しに1枚撮って、カメラが使えるか確かめる
        print("カメラOK！")

    except Exception:
        # カメラが見つからない（ケーブルの抜けなど）：エラーを知らせて終了する
        print("カメラNG...")
        error_LED()
        await cancel_task(start_sound_task)
        proc = await play_wav(CAMERA_ERROR_SOUND)
        await proc.wait()

        return

    ready_LED()

    # ボタンを「押した瞬間」だけ反応させるため、前回の状態を覚えておく
    # （押しっぱなしで何度も反応しないように）
    camera_was_pressed = False
    sub_was_pressed = False

    curr_task = None  # 今進めている「撮影→読み上げ」の処理
    while True:
        # 起動から5秒たっていたら、起動音を止める
        if (time.perf_counter() - timer1_start > 5.0):
            await cancel_task(start_sound_task)

        # 今のボタンの状態を読む
        camera_pressed = camera_button.is_pressed
        sub_pressed = sub_button.is_pressed

        # カメラボタンを押した瞬間：今の処理をやめて、撮影からやり直す
        if camera_pressed and not camera_was_pressed:
            await cancel_task(start_sound_task)
            await cancel_task(curr_task)
            camera.capture_file("image.jpg")  # 撮影
            curr_task = asyncio.create_task(API_and_speech("image.jpg"))

        # サブボタンを押した瞬間：今の処理（読み上げなど）を止めて待機に戻る
        if sub_pressed and not sub_was_pressed:
            await cancel_task(start_sound_task)
            await cancel_task(curr_task)
            ready_LED()

        # 次の回のために、今の状態を覚えておく
        camera_was_pressed = camera_pressed
        sub_was_pressed = sub_pressed

        # 0.01秒休む（この間に、効果音や通信のタスクが進む）
        await asyncio.sleep(0.01)


asyncio.run(main())
