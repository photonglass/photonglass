#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) OTON GLASS Inc.
#
# PHOTON GLASS: Raspberry Pi の準備をまとめて行うスクリプト（何度実行しても大丈夫）
#
# 使い方（Pi の上で。software フォルダを ~/photonglass にコピーしてから）:
#   sudo bash ~/photonglass/setup/setup_pi.sh [名前]
#     名前 … この Pi の名前（ホスト名。例 photon01）。何台も使うときは1台ずつ変える。省略すると名前は変えない
#
# やること
#   1. 必要なソフトを入れる（gpiozero, picamera2, httpx, requests, aplay）
#   2. スピーカー基板を使う設定（config.txt に dtoverlay=hifiberry-dac、HDMI の音声をオフ）
#      Wi-Fi の省電力をオフ・登録済みの Wi-Fi に自動でつなぐ（SSH が遅い・つながらないのを防ぐ）
#      デスクトップ画面を起動しない（Pi Zero 2 W はメモリが 512 MB しかないため）
#      名前（ホスト名.local）が「photon01-2.local」のように番号付きにならないようにする（avahi の設定）
#   3. Pi の名前を変える（引数を付けたとき）
#   4. 電源を入れたら main_async.py が自動で動く設定（photonglass.service）
#   5. 今のプログラムを /opt/photonglass/original に保存し、元に戻すコマンド photonglass-reset を入れる
#      （プログラムを直したときは、このスクリプトをもう一度実行すると保存し直せる）
# 最後に再起動すると、すべて反映されます。
set -e
[ "$(id -u)" -eq 0 ] || { echo "sudo を付けて実行してください: sudo bash $0 [名前]"; exit 1; }
NAME="$1"
HERE=$(cd "$(dirname "$0")" && pwd)
APP_DIR=$(dirname "$HERE")                     # software フォルダ（例 /home/photonglass/photonglass）
USER_NAME=${SUDO_USER:-$(stat -c %U "$APP_DIR")}
CFG=/boot/firmware/config.txt
[ -f "$APP_DIR/main_async.py" ] || { echo "$APP_DIR に main_async.py がありません"; exit 1; }
echo "プログラムのフォルダ: $APP_DIR（ユーザー $USER_NAME）"

echo "== 1. ソフトを入れる =="
# 前回のインストールが途中で止まっていたら（電源が切れたなど）、先に続きを済ませる
dpkg --configure -a
apt-get update -q
apt-get install -y -q -f
apt-get install -y -q python3-gpiozero python3-picamera2 python3-httpx python3-requests alsa-utils

echo "== 2. スピーカー基板の設定 =="
cp -n "$CFG" "$CFG.orig" || true               # 最初の1回だけ、元の config.txt を残す
grep -qE '^dtoverlay=hifiberry-dac' "$CFG" || echo 'dtoverlay=hifiberry-dac' >> "$CFG"
sed -i 's/^dtoverlay=vc4-kms-v3d$/dtoverlay=vc4-kms-v3d,noaudio/' "$CFG"
grep -E '^dtoverlay=(hifiberry-dac|vc4-kms-v3d)' "$CFG"

echo "== Wi-Fi の省電力をオフ（SSH の反応が遅くなる・つながらなくなるのを防ぐ） =="
mkdir -p /etc/NetworkManager/conf.d
printf '[connection]\n# 2 = Wi-Fi power saving off\nwifi.powersave = 2\n' > /etc/NetworkManager/conf.d/99-photonglass-wifi-powersave.conf
iw dev wlan0 set power_save off 2>/dev/null || true
# 登録済みの Wi-Fi は、起動したら自動でつなぐ（再起動後につながらないのを防ぐ）
nmcli -t -f NAME,TYPE connection show | awk -F: '$2=="802-11-wireless"{print $1}' | while read -r c; do
  nmcli connection modify "$c" connection.autoconnect yes && echo "  自動接続オン: $c"
done
nmcli radio wifi on

echo "== デスクトップ画面を起動しない（メモリの節約。SSH での操作には影響なし） =="
if [ "$(systemctl get-default)" != multi-user.target ]; then
  raspi-config nonint do_boot_behaviour B1     # 画面に戻すときは B4
fi
systemctl get-default

echo "== 名前が番号付き（例 photon01-2.local）にならないようにする =="
# Wi-Fi の IPv4 だけで名前を知らせる。IPv6 や複数の口から同じ名前を知らせると、自分どうしで
# 「名前がぶつかった」と判断して、名前の後ろに -2 などの番号を付けてしまうことがあるため
AVAHI=/etc/avahi/avahi-daemon.conf
if [ -f "$AVAHI" ]; then
  sed -i -e 's/^#*use-ipv6=.*/use-ipv6=no/' -e 's/^#*allow-interfaces=.*/allow-interfaces=wlan0/' "$AVAHI"
  grep -E '^(use-ipv6|allow-interfaces)=' "$AVAHI"
fi

if [ -n "$NAME" ]; then
  echo "== 3. 名前を $NAME にする（再起動後に $NAME.local でつながる） =="
  raspi-config nonint do_hostname "$NAME"
fi

echo "== 4. 自動起動の設定 =="
sed -e "s#APP_DIR#$APP_DIR#g" -e "s#^User=USER#User=$USER_NAME#" "$HERE/photonglass.service" \
  > /etc/systemd/system/photonglass.service
systemctl daemon-reload
systemctl enable photonglass.service

echo "== 5. 今のプログラムを「元の状態」として保存 =="
mkdir -p /opt/photonglass
rm -rf /opt/photonglass/original && mkdir -p /opt/photonglass/original
cp "$APP_DIR"/main_async.py "$APP_DIR"/main_seq.py /opt/photonglass/original/
cp -r "$APP_DIR/sound" /opt/photonglass/original/
echo "$APP_DIR" > /opt/photonglass/app_dir
install -m 755 "$HERE/photonglass-reset" /usr/local/bin/photonglass-reset
echo "元に戻すコマンド: photonglass-reset"

if [ ! -s "$APP_DIR/api_key.txt" ]; then
  echo
  echo "※ API キーがまだありません。次のコマンドでファイルを開き、キーを1行で書いて保存してください:"
  echo "   nano $APP_DIR/api_key.txt"
else
  chown "$USER_NAME": "$APP_DIR/api_key.txt"; chmod 600 "$APP_DIR/api_key.txt"
fi
echo
echo "完了しました。再起動してください: sudo reboot"
