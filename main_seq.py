##### APIキーの設定 #####
api_key = "AIzaSyBDd3EZXRcOPqObkWLj3TFGUocvX4brLcc"

##### 準備 #####
from gpiozero import LED
from gpiozero import Button
from picamera2 import Picamera2
import requests
import subprocess
import base64
import time
import asyncio
import httpx

# 音声ファイルのパス
START_SOUND = "sound/start.wav"
TRIGGER_SOUND = "sound/trigger.wav"
CONNECT_SOUND = "sound/connect.wav"
OK_SOUND = "sound/ok.wav"
NO_SOUND = "sound/no.wav"
FINISH_SOUND = "sound/finish.wav"
CAMERA_ERROR_SOUND = "sound/camera_error.wav"
NETWORK_ERROR_SOUND = "sound/network_error.wav"

# GPIOの設定
redLED = LED(10)
greenLED = LED(9)
blueLED = LED(11)
cameraButton = Button(17)
mainButton = Button(27)
subButton = Button(22)
upButton = Button(23)
downButton = Button(24)

# プロセスのインスタンスを格納するグローバル変数
# (関数内でglobalとして取り込むことで初めてグローバル変数として使える)
wavplayer_proc = None

##### 関数定義 #####

def stop_wav():
    global wavplayer_proc # pythonはglobal宣言しないとグローバル変数を使ってくれない
    if wavplayer_proc is not None and wavplayer_proc.poll() is None:
        wavplayer_proc.terminate()
        try:
            wavplayer_proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            wavplayer_proc.kill()

def wait_wav():
    global wavplayer_proc
    if wavplayer_proc is not None and wavplayer_proc.poll() is None:
        wavplayer_proc.wait()


def play_wav(path):
    global wavplayer_proc
    wavplayer_proc = subprocess.Popen(
        ["aplay", "-q", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# vision API との通信
def vision_api(img):
    with open(img, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode("utf-8")

    url = "https://vision.googleapis.com/v1/images:annotate?key=" + api_key
    headers = {
        "Content-Type": "application/json"
    }
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

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            raise requests.exceptions.HTTPError

        response_data = response.json()
        texts = response_data["responses"][0].get("textAnnotations", [])

        if len(texts) <= 0:
            raise ValueError

        text = texts[0]["description"]

    except requests.exceptions.RequestException:
        raise

    except ValueError:
        raise

    return text


# text-speech APIとの通信
def text_to_speech(text):
    SPEECH_SOUND = "speech.wav"
    url = "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + api_key
    headers = {
        "Content-Type": "application/json"
    }
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

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            raise requests.exceptions.HTTPError

        response_data = response.json()
        audio_content = response_data["audioContent"]

        with open(SPEECH_SOUND, "wb") as audio_file:
            audio_file.write(base64.b64decode(audio_content))

    except requests.exceptions.RequestException:
        raise

    return SPEECH_SOUND


# 待機LED(緑)
def readyLed():
    redLED.off()
    greenLED.on()
    blueLED.off()


# エラーLED(赤)
def errorLed():
    redLED.on()
    greenLED.off()
    blueLED.off()


# 接続LED(黄)
def connectLed():
    redLED.on()
    greenLED.on()
    blueLED.off()


# 読み上げLED(青)
def speechLed():
    redLED.off()
    greenLED.off()
    blueLED.on()


##### 起動 #####

print("起動！")

try:
    camera = Picamera2()
    camera_config = camera.create_still_configuration(
        main={"size": (1920, 1080)}
    )
    camera.configure(camera_config)
    camera.options["quality"] = 90
    camera.start()
    print("カメラOK！")

except Exception:
    print("カメラNG...")
    errorLed()
    play_wav(CAMERA_ERROR_SOUND)
    wait_wav()

    while True:
        errorLed()
        time.sleep(1)


play_wav(START_SOUND)
time.sleep(5)
stop_wav()


##### メインループ #####

while True:
    readyLed()

    if cameraButton.is_pressed:
        play_wav(TRIGGER_SOUND)

        try:
            camera.capture_file("image.jpg")

        except Exception:
            errorLed()
            stop_wav()
            play_wav(CAMERA_ERROR_SOUND)
            wait_wav()
            continue
        
        wait_wav()
        play_wav(CONNECT_SOUND)
        connectLed()

        try:
            text = vision_api("image.jpg")
            speech = text_to_speech(text)

            speechLed()
            stop_wav()

            play_wav(OK_SOUND)
            wait_wav()
            play_wav(speech)
            wait_wav()
            play_wav(FINISH_SOUND)
            wait_wav()

        except requests.exceptions.RequestException:
            errorLed()
            stop_wav()
            play_wav(NETWORK_ERROR_SOUND)
            wait_wav()
            continue

        except ValueError:
            errorLed()
            stop_wav()
            play_wav(NO_SOUND)
            wait_wav()
            continue

        while cameraButton.is_pressed:
            time.sleep(0.05)

    time.sleep(0.05)