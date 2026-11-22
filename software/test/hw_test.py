#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) OTON GLASS Inc.
"""OG19 基板の動作テスト（LED → ボタン → スピーカー → カメラ の順に1つずつ確認）

使い方（Raspberry Pi 上で）:
    python3 hw_test.py            # 全部のテスト
    python3 hw_test.py led        # LED だけ
    python3 hw_test.py button     # ボタンだけ
    python3 hw_test.py sound      # スピーカーだけ
    python3 hw_test.py camera     # カメラだけ
"""
import os
import subprocess
import sys
import time

# 今回の基板（JLCPCB版）のピン割り当て。RGB LED を代替品に替えたため、色と GPIO の対応が元の基板と違う
LED_PINS = {'赤': 9, '緑': 11, '青': 10}
BUTTON_PINS = {'カメラボタン（カメラ基板）': 17, 'メイン（SW_MAIN）': 27, 'サブ（SW_SUB）': 22,
               'UP（SW_UP）': 23, 'DOWN（SW_DOWN）': 24}


def test_led():
    from gpiozero import LED
    print('\n=== LED テスト ===')
    leds = {name: LED(pin) for name, pin in LED_PINS.items()}
    for name, led in leds.items():
        print(f'  {name} を2秒点灯（GPIO{LED_PINS[name]}）… 本当に{name}色に光っているか見てください')
        led.on(); time.sleep(2); led.off(); time.sleep(0.3)
    print('  3色同時（白っぽく光れば OK）')
    for led in leds.values(): led.on()
    time.sleep(2)
    for led in leds.values(): led.off()


def test_button():
    from gpiozero import Button
    print('\n=== ボタンテスト ===')
    print('  各ボタンを1回ずつ押してください（全部押せたら自動で終了、Ctrl+C で中断）')
    left = dict(BUTTON_PINS)
    buttons = {name: Button(pin) for name, pin in BUTTON_PINS.items()}
    try:
        while left:
            for name in list(left):
                if buttons[name].is_pressed:
                    print(f'  OK: {name}（GPIO{BUTTON_PINS[name]}）')
                    left.pop(name)
                    while buttons[name].is_pressed: time.sleep(0.02)
            time.sleep(0.02)
        print('  すべてのボタンが反応しました')
    except KeyboardInterrupt:
        print('  中断。反応しなかったボタン:', ', '.join(left) or 'なし')


def test_sound():
    print('\n=== スピーカーテスト ===')
    out = subprocess.run(['aplay', '-l'], capture_output=True, text=True).stdout
    if 'hifiberry' not in out.lower():
        print('  ✗ 音声ボード（snd_rpi_hifiberry_dac）が見つかりません。')
        print('    /boot/firmware/config.txt に dtoverlay=hifiberry-dac があるか確認して再起動してください')
        print(out)
        return
    print('  ✓ 音声ボードを認識しています')
    # software/sound/start.wav を使う（どのフォルダから実行しても見つかるように、このファイルの場所から数える）
    wav = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sound', 'start.wav'))
    print('  ボリューム（VR1）を少し上げて、ヘッドホンは抜いておいてください')
    if os.path.exists(wav):
        print(f'  {wav} を再生します')
        subprocess.run(['aplay', '-D', 'plughw:CARD=sndrpihifiberry', wav])
    else:
        print('  左右交互にテスト音を出します（Ctrl+C で止める）')
        subprocess.run(['speaker-test', '-D', 'plughw:CARD=sndrpihifiberry', '-c', '2', '-t', 'wav', '-l', '1'])
    print('  ヘッドホンを挿すとスピーカーの音が止まり、ヘッドホンから聞こえれば OK です')


def test_camera():
    print('\n=== カメラテスト ===')
    try:
        from picamera2 import Picamera2
    except ImportError:
        print('  ✗ picamera2 がありません: sudo apt install -y python3-picamera2'); return
    cams = Picamera2.global_camera_info()
    if not cams:
        print('  ✗ カメラが見つかりません。FFC ケーブルの向き・差し込み、HDMI ケーブル、カメラ基板を確認してください')
        return
    print('  ✓ 検出:', cams[0].get('Model'))
    cam = Picamera2()
    cam.start(); time.sleep(2)
    path = os.path.expanduser('~/test.jpg')
    cam.capture_file(path); cam.stop()
    print(f'  撮影しました: {path}（Mac に scp で持ってきて確認できます）')


TESTS = {'led': test_led, 'button': test_button, 'sound': test_sound, 'camera': test_camera}

if __name__ == '__main__':
    names = sys.argv[1:] or list(TESTS)
    for n in names:
        TESTS[n]()
    print('\nテスト終了')
