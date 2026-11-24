#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) OTON GLASS Inc.
#
# PHOTON GLASS: Raspberry Pi の準備がどこまでできているかを確認するスクリプト
# 何も書き換えません（見るだけ）。API キーや Wi-Fi のパスワードは表示しません。
#
# 使い方
#   Mac から（Pi にコピーしなくてよい）:
#     ssh ユーザー名@ホスト名.local 'bash -s' < check_setup.sh   （例 ssh pi@photon01.local ...）
#   Pi の上で:
#     bash check_setup.sh [プログラムのフォルダ]      （初期値 ~/photonglass）

PATH="$PATH:/usr/sbin:/sbin"   # iw など管理用のコマンドの場所（ふつうのユーザーには入っていない）
DIR="${1:-$HOME/photonglass}"
CFG=/boot/firmware/config.txt
SVC=/etc/systemd/system/photonglass.service
NG=0
ok()   { echo "  [OK] $*"; }
ng()   { echo "  [NG] $*"; NG=$((NG + 1)); }
info() { echo "  [--] $*"; }

echo "== 1. OS・Wi-Fi =="
. /etc/os-release
info "OS: $PRETTY_NAME（$(getconf LONG_BIT) bit）／ユーザー: $(whoami)／ホスト名: $(hostname)"
ssid=$(iw dev wlan0 link 2>/dev/null | sed -n 's/^[[:space:]]*SSID: //p')
[ -n "$ssid" ] && ok "Wi-Fi に接続中（$ssid）" || ng "Wi-Fi に接続していない"
iw dev wlan0 get power_save 2>/dev/null | grep -q off && ok "Wi-Fi の省電力がオフ" \
  || ng "Wi-Fi の省電力がオン（SSH が遅くなる原因。setup/setup_pi.sh でオフになる）"
[ "$(systemctl get-default)" = multi-user.target ] && ok "デスクトップ画面を起動しない設定（メモリの節約）" \
  || info "デスクトップ画面が起動する設定（setup/setup_pi.sh で起動しない設定になる。推奨）"
ping -c1 -W3 8.8.8.8 >/dev/null 2>&1 && ok "インターネットにつながる" || ng "インターネットにつながらない"

A=/etc/avahi/avahi-daemon.conf
grep -q '^use-ipv6=no' "$A" 2>/dev/null && grep -q '^allow-interfaces=wlan0' "$A" 2>/dev/null \
  && ok "名前（$(hostname).local）が番号付きにならない設定" \
  || ng "avahi の設定がない（名前が $(hostname)-2.local のようになることがある。setup/setup_pi.sh で直る）"
systemctl is-enabled photonglass-fixname >/dev/null 2>&1 && ok "名前に番号が付いたら自動で戻す設定（photonglass-fixname）" \
  || ng "名前を自動で戻す設定がない（setup/setup_pi.sh で入る）"
ip4=$(ip -4 -o addr show wlan0 2>/dev/null | awk '{print $4}' | cut -d/ -f1 | head -1)
now=$([ -n "$ip4" ] && avahi-resolve -a "$ip4" 2>/dev/null | awk '{print $2}')
if [ -z "$now" ]; then
  info "今の名前（.local）を確かめられなかった（avahi-utils がない、または起動した直後）"
elif [ "$now" = "$(hostname).local" ]; then
  ok "今の名前は $now"
else
  ng "今の名前が $now になっている（起動した直後なら1分ほど待って、もう一度確かめる）"
fi

echo "== 2. SSH =="
systemctl is-enabled ssh >/dev/null 2>&1 && ok "SSH が有効" || ng "SSH が無効"

echo "== 3. スピーカー =="
grep -qE '^dtoverlay=hifiberry-dac' "$CFG" && ok "config.txt に dtoverlay=hifiberry-dac がある" \
  || ng "config.txt に dtoverlay=hifiberry-dac がない（必須）"
grep -qE '^dtoverlay=vc4-kms-v3d,noaudio' "$CFG" && ok "HDMI の音声がオフ（noaudio）" \
  || info "HDMI の音声オフ（dtoverlay=vc4-kms-v3d,noaudio）がない（推奨）"
if grep -qi hifiberry /proc/asound/cards 2>/dev/null; then
  ok "サウンドカード hifiberry を認識している"
else
  ng "サウンドカード hifiberry が見えない（config.txt を書き換えたあと再起動した？）"
fi

echo "== 4. カメラ =="
if command -v rpicam-hello >/dev/null; then CAM=rpicam-hello; else CAM=libcamera-hello; fi
if $CAM --list-cameras 2>&1 | grep -qE '^ *[0-9]+ : '; then
  ok "カメラを認識している（$($CAM --list-cameras 2>&1 | grep -E '^ *[0-9]+ : ' | head -1 | sed 's/^ *//' | cut -c1-40)）"
else
  ng "カメラが見えない（フレキケーブルの向き・差し込みを確認）"
fi

echo "== 5. Python のライブラリ =="
for m in gpiozero picamera2 httpx requests; do
  python3 -c "import $m" 2>/dev/null && ok "$m" || ng "$m がない（sudo apt install -y python3-$m）"
done
command -v aplay >/dev/null && ok "aplay（音声の再生）" || ng "aplay がない（sudo apt install -y alsa-utils）"

echo "== 6. プログラムと音声ファイル（$DIR） =="
if [ -d "$DIR" ]; then
  for f in main_async.py main_seq.py; do
    [ -f "$DIR/$f" ] && ok "$f がある" || ng "$f がない"
  done
  miss=""
  for w in start trigger connect ok no finish camera_error network_error; do
    [ -f "$DIR/sound/$w.wav" ] || miss="$miss $w.wav"
  done
  [ -z "$miss" ] && ok "sound/ の音声ファイル 8 個がそろっている" || ng "sound/ に足りないファイル:$miss"
  if [ -s "$DIR/api_key.txt" ]; then
    k=$(tr -d '[:space:]' < "$DIR/api_key.txt")
    case "$k" in AIza*) ok "api_key.txt に API キーがある（中身は表示しません）";;
                 *) ng "api_key.txt の中身が API キーの形ではない（AIza で始まる1行）";; esac
  else
    ng "api_key.txt がない（nano $DIR/api_key.txt でキーを1行書く）"
  fi
  for f in main_async.py main_seq.py; do
    [ -f "$DIR/$f" ] || continue
    grep -q 'API_KEY_FILE' "$DIR/$f" && ok "$f は api_key.txt からキーを読む新しい版" || ng "$f が古い版（新しいものをコピーし直す）"
    grep -qE '^[a-z_A-Z]+ = LED\(9\)' "$DIR/$f" && ok "$f は 2026年版の基板の LED 設定" || ng "$f の LED 設定が古い"
  done
else
  ng "フォルダ $DIR がない（software フォルダを Pi にコピーしていない）"
fi
[ -f "$HOME/main.py" ] && info "古い ~/main.py が残っている（自動起動がこれを動かしていないか下で確認）"

echo "== 7. 電源を入れたら自動で起動 =="
if [ -f "$SVC" ]; then
  ok "photonglass.service がある"
  exe=$(grep -E '^ExecStart=' "$SVC" | cut -d= -f2-)
  wd=$(grep -E '^WorkingDirectory=' "$SVC" | cut -d= -f2-)
  info "動かすプログラム: $exe"
  info "作業フォルダ　　: $wd"
  prog=$(echo "$exe" | awk '{print $NF}')
  [ -f "$prog" ] && ok "そのプログラムが存在する" || ng "そのプログラムが見つからない（$prog）"
  case "$prog" in *main_async.py|*main_seq.py) ok "新しいプログラムを動かす設定";; *) ng "古いプログラムを動かす設定（main_async.py に変える）";; esac
  [ -d "$wd/sound" ] && ok "作業フォルダに sound/ がある" || ng "作業フォルダに sound/ がない（音が出ない）"
  grep -q '^Wants=network-online.target' "$SVC" && ok "ネットワークを待つ設定（Wants=）がある" \
    || info "Wants=network-online.target がない（After= だけだと待たないことがある。追加推奨）"
  systemctl is-enabled photonglass >/dev/null 2>&1 && ok "自動起動が有効（enable 済み）" || ng "自動起動が無効（sudo systemctl enable photonglass）"
  systemctl is-active photonglass >/dev/null 2>&1 && ok "いま動いている" || ng "いま動いていない"
  echo "  --- 最近のログ（最後の 10 行）---"
  journalctl -u photonglass -n 10 --no-pager 2>/dev/null | sed 's/^/  /'
else
  ng "photonglass.service がない（自動起動の設定をしていない → sudo bash $DIR/setup/setup_pi.sh 名前）"
fi
command -v photonglass-reset >/dev/null && ok "元に戻すコマンド photonglass-reset がある" \
  || ng "photonglass-reset がない（setup/setup_pi.sh を実行する）"

echo
[ "$NG" -eq 0 ] && echo "すべて OK です。" || echo "NG が $NG 個あります。上の [NG] の行を確認してください。"
