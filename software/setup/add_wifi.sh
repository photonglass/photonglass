#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) OTON GLASS Inc.
# PHOTON GLASS: Wi-Fi を登録する（その場所にいなくても、先に登録しておける）
# 使い方:  sudo bash add_wifi.sh "Wi-Fiの名前" [優先度]
#   パスワードは実行したあとに聞かれます（画面にもコマンドの履歴にも残りません）。
#   優先度は数字が大きいほど先につなぎます（初期値 10）。いくつでも登録できます。
set -e
[ "$(id -u)" -eq 0 ] || { echo "sudo を付けて実行してください"; exit 1; }
SSID="$1"; PRIO="${2:-10}"
[ -n "$SSID" ] || { echo '使い方: sudo bash add_wifi.sh "Wi-Fiの名前" [優先度]'; exit 1; }
read -r -s -p "「$SSID」のパスワード: " PSK; echo
nmcli connection delete "$SSID" >/dev/null 2>&1 || true
nmcli connection add type wifi con-name "$SSID" ssid "$SSID" \
  wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PSK" \
  connection.autoconnect yes connection.autoconnect-priority "$PRIO" >/dev/null
echo "登録しました: $SSID（優先度 $PRIO）"
echo "登録済みの Wi-Fi:"; nmcli -f NAME,AUTOCONNECT-PRIORITY connection show | grep -v -E '^lo |ethernet'
