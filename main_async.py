##### APIキーの設定 #####
api_key = "AIzaSyBDd3EZXRcOPqObkWLj3TFGUocvX4brLcc"

##### 準備 #####
from gpiozero import LED, Button
from picamera2 import Picamera2
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
red_LED = LED(10)
green_LED = LED(9)
blue_LED = LED(11)

camera_button = Button(17)
main_button = Button(27)
sub_button = Button(22)
up_button = Button(23)
down_button = Button(24)


##### LED #####

def ready_LED():
    red_LED.off()
    green_LED.on()
    blue_LED.off()


def error_LED():
    red_LED.on()
    green_LED.off()
    blue_LED.off()


def connect_LED():
    red_LED.on()
    green_LED.on()
    blue_LED.off()


def speech_LED():
    red_LED.off()
    green_LED.off()
    blue_LED.on()


##### 音声再生 #####

async def stop_wav(proc):
    if proc is not None:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=1)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()

async def play_wav(path):
    proc = await asyncio.create_subprocess_exec(
        "aplay", "-q", path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return proc


##### API #####

async def vision_api(img):
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
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise httpx.HTTPError

        response_data = response.json()
        texts = response_data["responses"][0].get("textAnnotations", [])

        if len(texts) <= 0:
            raise ValueError

        text = texts[0]["description"]

    except httpx.HTTPError:
        raise

    except ValueError:
        raise

    return text


async def text_to_speech(text):
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
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise  httpx.HTTPError

        response_data = response.json()
        audio_content = response_data["audioContent"]

        with open(SPEECH_SOUND, "wb") as audio_file:
            audio_file.write(base64.b64decode(audio_content))

    except httpx.HTTPError:
        raise

    return SPEECH_SOUND

##### その他関数 #####
async def cancel_task(task):
    if task is not None and not task.done():
        task.cancel()
        await task
        

##### 時間がかかるタスク #####

# スタートサウンドを再生
async def play_start_sound():
    proc = None
    try:
        proc = await play_wav(START_SOUND)
        await proc.wait()

    except asyncio.CancelledError:
        await stop_wav(proc)
    
# トリガーからコネクトサウンドまで再生
async def play_trigger_connect_sound():
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
    proc = None
    sound_task = asyncio.create_task(play_trigger_connect_sound())

    connect_LED()
    try:
        try:
            text = await vision_api(image) # 文字認識
            speech = await text_to_speech(text) # 音声作成

        except httpx.HTTPError: # apiのエラー
            await cancel_task(sound_task)
            error_LED()
            proc = await play_wav(NETWORK_ERROR_SOUND)
            await proc.wait()
            ready_LED()
            return

        except ValueError: # 文字がないエラー
            await cancel_task(sound_task)
            error_LED()
            proc = await play_wav(NO_SOUND)
            await proc.wait()
            ready_LED()
            return

        except Exception: # カメラのエラー
            await cancel_task(sound_task)
            error_LED()
            proc = await play_wav(CAMERA_ERROR_SOUND)
            await proc.wait()
            ready_LED()
            return
        
        await cancel_task(sound_task)
        
        # 読み上げ
        speech_LED()
        proc = await play_wav(OK_SOUND)
        await proc.wait()
        proc = await play_wav(speech)
        await proc.wait()
        proc = await play_wav(FINISH_SOUND)
        await proc.wait()

        ready_LED()

    except asyncio.CancelledError:
        await cancel_task(sound_task)
        await stop_wav(proc)
        ready_LED()
        return
    

##### メインループ #####

async def main():
    print("起動！")

    # OSが安定するまで待機した方が良いかもしれない

    timer1_start = time.perf_counter()

    start_sound_task = asyncio.create_task(play_start_sound())

    try:
        camera = Picamera2()
        camera_config = camera.create_still_configuration(
            main={"size": (1920, 1080)}
        )
        camera.configure(camera_config)
        camera.options["quality"] = 90
        camera.start()
        camera.capture_file("image.jpg") # 試し撮影
        print("カメラOK！")

    except Exception:
        print("カメラNG...")
        error_LED()
        await cancel_task(start_sound_task)
        proc = await play_wav(CAMERA_ERROR_SOUND)
        await proc.wait()

        return
    

    ready_LED()

    # 押されてない-->押された のタイミングを判定するために、過去の状態を記録
    camera_was_pressed = False
    sub_was_pressed = False

    curr_task = None
    while True:
        # タイマー1: 5秒経っていたら、スタートサウンド停止
        if(time.perf_counter() - timer1_start > 5.0):
            await cancel_task(start_sound_task)

        camera_pressed = camera_button.is_pressed
        sub_pressed = sub_button.is_pressed

        if camera_pressed and not camera_was_pressed:
            await cancel_task(start_sound_task)
            await cancel_task(curr_task)
            camera.capture_file("image.jpg") # 撮影
            curr_task = asyncio.create_task(API_and_speech("image.jpg"))

        if sub_pressed and not sub_was_pressed:
            await cancel_task(start_sound_task)
            await cancel_task(curr_task)
            ready_LED()

        camera_was_pressed = camera_pressed
        sub_was_pressed = sub_pressed

        await asyncio.sleep(0.01)


asyncio.run(main())
