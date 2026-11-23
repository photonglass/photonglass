# Raspberry Pi のセットアップ

PHOTON GLASS の Raspberry Pi を、OS のインストールから、動作テスト、プログラムの自動起動まで準備する手順です。
組み立て（[`BUILD_GUIDE.md`](BUILD_GUIDE.md) の 1〜4）が終わっていることを前提にしています。

## 必要なもの
- Raspberry Pi Zero 2 WH（メイン基板を載せ、カメラユニット・スピーカー・電源ケーブルをつないだもの）
- microSD カード（SanDisk Ultra 32GB を使っています）
- PC（Mac）と、microSD カードを読み書きする機器
- Wi-Fi（Google Cloud と通信するために使います）
- 初期設定に使う、モニター・キーボード・マウス（[`BUILD_GUIDE.md` の「0. 必要なもの」](BUILD_GUIDE.md#0-必要なもの)）
- Google Cloud の API キー（「[7. API キーを用意する](#7-api-キーを用意する)」）

このページでは、次の名前を使います。

| 項目 | このページで使う名前 |
|---|---|
| ユーザー名 | `photonglass` |
| ホスト名 | `raspberrypi`（Raspberry Pi Imager の初期値。PC からは `raspberrypi.local` でつなぐ） |
| プログラムを置く場所 | `~/photonglass`（`/home/photonglass/photonglass`） |

パスワードや Wi-Fi の名前は、`<パスワード>` のように書いています。自分のものに置き換えてください。
違うユーザー名やホスト名にした場合は、このページのコマンドも読み替えてください。

## 1. OS を microSD カードに書き込む
1. PC に [Raspberry Pi Imager](https://www.raspberrypi.com/software/) を入れて、起動する。
2. 次のように選ぶ。
   - デバイス：Raspberry Pi Zero 2 W
   - OS：Raspberry Pi OS (32-bit)（デスクトップ付き。Bookworm 以降）
   - 書き込み先：microSD カード
3. OS のカスタマイズ（詳細設定）で、次を設定してから書き込む。
   - ホスト名：`raspberrypi`
   - ユーザー名：`photonglass`、パスワード：`<パスワード>`
   - Wi-Fi：SSID は `<Wi-Fi の名前>`、パスワードは `<Wi-Fi のパスワード>`、国は `JP`

Imager の画面や項目の名前は、版によって少し違います。

## 2. 初めて起動して、SSH を有効にする
1. microSD カードを Raspberry Pi に挿す。
2. モニターを Raspberry Pi の mini HDMI 端子に、キーボードとマウスを Raspberry Pi の USB 端子（micro USB の、電源用ではない方）につなぐ。
3. 電源ケーブルでモバイルバッテリーをつなぎ、バッテリーの電源ボタンを押す（[`enclosure/usb-power-cable/README.md` の「使うモバイルバッテリー」](../enclosure/usb-power-cable/README.md#使うモバイルバッテリー)）。
4. デスクトップが表示されたら、メニューの「設定（Preferences）」から「Raspberry Pi の設定（Raspberry Pi Configuration）」を開き、「インターフェイス（Interfaces）」で SSH を有効にする。OS の版によって、メニューの名前や場所が少し違うことがあります。
5. PC のターミナルから、SSH でつながることを確かめる。
   ```bash
   ssh photonglass@raspberrypi.local
   ```
   初めてつなぐときに `Are you sure you want to continue connecting` と聞かれたら `yes` と入力し、続けてパスワードを入力します（入力しても画面には何も表示されません）。

この後のコマンドは、SSH でつないだ PC のターミナルからでも、Raspberry Pi のデスクトップのターミナルからでも実行できます。
SSH でつながれば、モニター・キーボード・マウスは外して構いません（このあとの手順は、すべて SSH から行えます）。

## 3. 音声出力（DAC）を設定する
メイン基板の音声出力（DAC）を、Raspberry Pi で使えるようにします。
1. 設定ファイルを開く。
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
2. ファイルの末尾に、次の1行を追加する（必須）。
   ```
   dtoverlay=hifiberry-dac
   ```
3. （推奨）`dtoverlay=vc4-kms-v3d` と書かれた行を、次のように書き換える。HDMI からの音声出力を使わない設定です。
   ```
   dtoverlay=vc4-kms-v3d,noaudio
   ```
4. 保存して閉じ（nano では Ctrl+O → Enter → Ctrl+X）、再起動する。
   ```bash
   sudo reboot
   ```
5. 再起動したら、音声出力が認識されているか確かめる。
   ```bash
   aplay -l
   ```
   一覧に `hifiberry`（`snd_rpi_hifiberry_dac`）が出れば OK です。

本体プログラム（`main_async.py`・`main_seq.py`）と動作テスト（`test/hw_test.py`）は、スピーカー基板に直接音を送ります。デスクトップのサウンドの設定で出力先を選ぶ必要はありません。

## 4. 必要なソフトを入れる
```bash
sudo apt update
```
```bash
sudo apt install -y python3-gpiozero python3-picamera2 python3-httpx python3-requests
```
音を鳴らすコマンド `aplay` は、Raspberry Pi OS に最初から入っています。

## 5. カメラについて
カメラのための追加の設定はいりません（`config.txt` の変更も不要です）。
カメラが認識されているかは「[8. 動作テストをする](#8-動作テストをする)」で確かめます。

## 6. プログラムを Raspberry Pi にコピーする
PC にまだこのリポジトリがない場合は、GitHub のリポジトリのページで「Code」→「Download ZIP」を選んでダウンロードして展開するか、次のコマンドで取得します。
```bash
git clone https://github.com/photonglass/photonglass.git
```
PC（Mac）のターミナルで、このリポジトリのフォルダ（`git clone` なら `photonglass`、ZIP なら `photonglass-main`）に移動してから実行します。
`software` フォルダの中身を、Raspberry Pi の `~/photonglass` にコピーします。
```bash
ssh photonglass@raspberrypi.local "mkdir -p ~/photonglass"
```
```bash
scp -r software/main_async.py software/main_seq.py software/sound software/test software/setup software/check_setup.sh photonglass@raspberrypi.local:photonglass/
```
コピーしたあとの Raspberry Pi の中は、次のようになります（`api_key.txt` は次の手順で置きます）。
```
~/photonglass/
├── main_async.py     本体プログラム（普段使う）
├── main_seq.py       本体プログラム（流れの読みやすい版）
├── sound/            効果音
├── test/hw_test.py   動作テスト
├── setup/            準備をまとめて行うスクリプト（「13.」で使う）
├── check_setup.sh    準備ができているかを確認するスクリプト
└── api_key.txt       Google Cloud の API キー
```
プログラムを書き換えたときも、同じ `scp` のコマンドでコピーし直します。

### 元のプログラムを保存し、元に戻すコマンドを入れる
プログラムを書き換え始める前に、コピーしたばかりのプログラムを「元の状態」として保存し、元に戻すコマンド `photonglass-reset` を入れます。「[13. 準備をまとめて行うスクリプト](#13-準備をまとめて行うスクリプト)」の `setup_pi.sh` が行うのと同じ作業です。ここからは Raspberry Pi で（SSH でつないで）実行します。
1. 保存先のフォルダを作る。
   ```bash
   sudo mkdir -p /opt/photonglass/original
   ```
2. プログラムと効果音を保存する。
   ```bash
   sudo cp -r ~/photonglass/main_async.py ~/photonglass/main_seq.py ~/photonglass/sound /opt/photonglass/original/
   ```
3. プログラムのフォルダの場所を書いておく（`photonglass-reset` が使います）。
   ```bash
   echo "$HOME/photonglass" | sudo tee /opt/photonglass/app_dir
   ```
4. `photonglass-reset` を入れる。
   ```bash
   sudo install -m 755 ~/photonglass/setup/photonglass-reset /usr/local/bin/photonglass-reset
   ```

書き換えて動かなくなったときは、`photonglass-reset` を実行すると、ここで保存した状態に戻ります。API キー（`api_key.txt`）はそのまま残り、書き換えた方は `~/photonglass/backup_日時/` に残ります。「10.」の自動起動を設定する前に使うと、最後の「動かし直し」でエラーが表示されますが、元に戻す作業は済んでいます。

## 7. API キーを用意する
1. Google Cloud で API キーを作り、**Cloud Vision API** と **Cloud Text-to-Speech API** を有効にする。
   - キーには「使える API の制限」（この2つだけ）を付けておくと安全です。
   - プロジェクトの課金（請求先アカウント）が有効になっていないと、通信のエラーになります。
2. PC で、見本のファイルをコピーして `api_key.txt` を作り、中身を自分のキー1行に書き換える。
   ```bash
   cp software/api_key.txt.example software/api_key.txt
   ```
3. Raspberry Pi の `~/photonglass` にコピーする。
   ```bash
   scp software/api_key.txt photonglass@raspberrypi.local:photonglass/
   ```

プログラムは、自分のファイルと同じフォルダにある `api_key.txt` を読みます。ファイルがない・空のときは、起動時に赤く光って通信エラーの音を鳴らし、止まります。

> [!WARNING]
> `api_key.txt` は、GitHub などで公開しないでください。他人に使われて料金が請求されることがあります（このリポジトリでは `.gitignore` で git の管理から外しています）。

## 8. 動作テストをする
`hw_test.py` で、LED → ボタン → スピーカー → カメラ の順に、1つずつ確かめます（Raspberry Pi で実行します）。
```bash
python3 ~/photonglass/test/hw_test.py
```

| テスト | やること・確かめること |
|---|---|
| LED | 赤・緑・青が2秒ずつ光るので、本当にその色に光っているかを見る。最後の3色同時で、白っぽく光れば OK |
| ボタン | 5つのボタン（カメラボタン、メイン、サブ、UP、DOWN）を1回ずつ押す。全部反応すると次へ進む（Ctrl+C で中断） |
| スピーカー | ボリューム（VR1）を少し上げ、ヘッドホンは抜いておく。起動音が鳴れば OK。ヘッドホンを挿すとスピーカーの音が止まり、ヘッドホンから聞こえれば OK |
| カメラ | カメラが見つかると、1枚撮って `~/test.jpg` に保存する |

撮った写真は、PC に持ってきて確かめられます（PC で実行）。
```bash
scp photonglass@raspberrypi.local:test.jpg .
```
1つだけ試すときは、最後に `led`・`button`・`sound`・`camera` のどれかを付けます（例：`python3 ~/photonglass/test/hw_test.py camera`）。

うまくいかないとき：
- 「音声ボード（snd_rpi_hifiberry_dac）が見つかりません」と出る → `config.txt` に `dtoverlay=hifiberry-dac` があるか確かめて、再起動する（「[3. 音声出力（DAC）を設定する](#3-音声出力dacを設定する)」）
- 「カメラが見つかりません」と出る → FFC ケーブルの向き・差し込み、HDMI ケーブル、カメラ基板を確かめる

## 9. プログラムを動かす
```bash
python3 ~/photonglass/main_async.py
```
起動音が鳴り、LED が緑になったら準備完了です。カメラボタンを押すと、写真を撮って文字を読み上げます。止めるときは Ctrl+C を押します。
効果音や `api_key.txt` は、プログラムのファイルがあるフォルダから探すので、どのフォルダから実行しても動きます。

| LED の色 | 状態 |
|---|---|
| 緑 | 待機中（ボタンを押せる） |
| 黄 | 通信中 |
| 青 | 読み上げ中 |
| 赤 | エラー（効果音で、カメラ・通信・文字が見つからない、のどれかを知らせる） |

2つのプログラム（`main_async.py` と `main_seq.py`）の違いは、[`software/README.md`](../software/README.md) を見てください。

## 10. 電源を入れたら自動で動くようにする（systemd）
1. サービスの設定ファイルを作る。
   ```bash
   sudo nano /etc/systemd/system/photonglass.service
   ```
   中身は次のとおりです。
   ```ini
   [Unit]
   Description=PHOTON GLASS (photonglass)
   Wants=network-online.target
   After=network-online.target sound.target

   [Service]
   User=photonglass
   WorkingDirectory=/home/photonglass/photonglass
   ExecStart=/usr/bin/python3 /home/photonglass/photonglass/main_async.py
   Environment=PYTHONUNBUFFERED=1
   # 止まってしまったら（エラーやカメラの抜けなど）、5秒後に自動で動かし直す
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
   この中身は、「[13. 準備をまとめて行うスクリプト](#13-準備をまとめて行うスクリプト)」の `setup_pi.sh` が入れるもの（`software/setup/photonglass.service`）と同じです。この手順は、`setup_pi.sh` でも自動で行えます。
2. サービスを有効にして、動かす。
   ```bash
   sudo systemctl daemon-reload
   ```
   ```bash
   sudo systemctl enable --now photonglass
   ```
   次からは、電源を入れると自動で `main_async.py` が動きます。

| やりたいこと | コマンド |
|---|---|
| 動いているか見る | `systemctl status photonglass` |
| 止める | `sudo systemctl stop photonglass` |
| 動かす | `sudo systemctl start photonglass` |
| 書き換えたプログラムを反映する | `sudo systemctl restart photonglass` |
| 自動で動かないようにする | `sudo systemctl disable --now photonglass` |

自動で動いている間は、そのプログラムがカメラを使っています。自分で `python3 main_async.py` を動かしたり、`hw_test.py` を使ったりするときは、先に `sudo systemctl stop photonglass` で止めてください。終わったら `sudo systemctl start photonglass` で戻します。

## 11. 困ったとき

| 症状 | 確かめること |
|---|---|
| PC から `raspberrypi.local` につながらない | Raspberry Pi の電源が入っているか、PC と同じ Wi-Fi につながっているか。起動が終わるまで少し待つ |
| SSH で `REMOTE HOST IDENTIFICATION HAS CHANGED` と出る（OS を書き込み直したときなど） | PC で `ssh-keygen -R raspberrypi.local` を実行してから、つなぎ直す |
| 起動すると赤く光り、通信エラーの音が鳴って止まる（そのあとボタンに反応しない） | `~/photonglass/api_key.txt` があるか、中身が空でないか（「[7. API キーを用意する](#7-api-キーを用意する)」） |
| ボタンを押すと、通信エラーの音が鳴る | Wi-Fi につながっているか、API キーが正しいか、Google Cloud の API と課金が有効か |
| カメラのエラーの音が鳴る | FFC ケーブルの向き・差し込み、HDMI ケーブル、カメラ基板（「[8. 動作テストをする](#8-動作テストをする)」のカメラのテスト） |
| スピーカーから音が出ない | `aplay -l` に hifiberry が出るか、ボリューム（VR1）、ヘッドホンが挿さっていないか |
| カメラのエラーの音が鳴ったあと、少しして起動音が鳴る | 使っている途中でカメラから写真が届かなくなったので、プログラムが起動し直した。FFC ケーブルのゆるみ（電源を切ってから挿し直す）か、電源の不足 |
| SSH の反応が遅い・ときどきつながらなくなる | Wi-Fi の省電力が効いている。「[13.](#13-準備をまとめて行うスクリプト)」の `setup_pi.sh` でオフになる |
| `ホスト名.local` ではつながらず、`ホスト名-2.local` などの番号付きの名前になっている | 名前がぶつかったと判断されている。「[14. 何台も用意するとき](#14-何台も用意するとき)」の avahi の設定を行う |
| 自動で動いているプログラムのメッセージを見たい | `journalctl -u photonglass -n 30` で、最近のメッセージを見られる。`sudo systemctl stop photonglass` で止めてから `python3 ~/photonglass/main_async.py` で動かすと、ターミナルに表示される |

## 12. 電源を切る
```bash
sudo poweroff
```
Raspberry Pi が止まるまで少し待ってから、バッテリーの電源ボタンを押して給電を止めます。いきなり給電を止めると、microSD カードが壊れることがあります。

## 13. 準備をまとめて行うスクリプト
「3. 音声出力（DAC）を設定する」「4. 必要なソフトを入れる」、「6.」の「[元のプログラムを保存し、元に戻すコマンドを入れる](#元のプログラムを保存し元に戻すコマンドを入れる)」、「10. 電源を入れたら自動で動くようにする」を、`setup_pi.sh` でまとめて行えます。何度実行しても大丈夫です。
「6. プログラムを Raspberry Pi にコピーする」で `setup/` もコピーしてから、Raspberry Pi で実行します。
```bash
sudo bash ~/photonglass/setup/setup_pi.sh photon01
```
`photon01` は、この Raspberry Pi の名前（ホスト名）です。省略すると名前は変えません。終わったら `sudo reboot` で再起動します。

`setup_pi.sh` がすること：
- 必要なソフトを入れる（`python3-gpiozero`・`python3-picamera2`・`python3-httpx`・`python3-requests`・`alsa-utils`）
- `config.txt` に `dtoverlay=hifiberry-dac` を足し、HDMI の音声をオフにする
- Wi-Fi の省電力をオフにする（SSH が遅くなる・つながらなくなるのを防ぐ）、登録済みの Wi-Fi に自動でつなぐ
- デスクトップ画面を起動しない（Raspberry Pi Zero 2 W はメモリが少ないため。SSH での操作には影響しない）
- 名前が番号付き（例 `photon01-2.local`）にならないようにする（「[14.](#14-何台も用意するとき)」）
- 名前を変える（引数を付けたとき）
- 電源を入れたら `main_async.py` が自動で動く設定（`photonglass.service`）
- 今のプログラムを「元の状態」として保存し、元に戻すコマンド `photonglass-reset` を入れる。書き換えて動かなくなったら `photonglass-reset` で戻せます（書き換えた方は `~/photonglass/backup_日時/` に残ります）

準備ができているかは、PC から `check_setup.sh` で確かめられます（見るだけで、何も書き換えません。API キーや Wi-Fi のパスワードは表示しません）。`[NG]` の行があれば、そこに書かれている直し方を行います。
```bash
ssh photonglass@photon01.local 'bash -s' < software/check_setup.sh
```

使う場所の Wi-Fi は、その場所にいなくても先に登録できます。パスワードは実行したあとに聞かれます（画面にもコマンドの履歴にも残りません）。数字は優先度で、大きいほど先につなぎます。
```bash
sudo bash ~/photonglass/setup/add_wifi.sh "Wi-Fiの名前" 20
```

## 14. 何台も用意するとき
1台目を完成させてから、その microSD カードを複製すると、残りを早く用意できます。
- **名前を1台ずつ変える。** 複製したカードは、どれも1台目と同じ名前で起動します。1台ずつ起動して、`sudo raspi-config nonint do_hostname photon02` のように名前を変え、再起動します（同じ名前の Raspberry Pi を同時に起動すると、どれにつながるかわからなくなります）。
- **名前が番号付きになるとき。** `photon02.local` が見つからず、`photon02-2.local` のような名前になることがあります。Raspberry Pi が自分の名前を複数の口（IPv4 と IPv6 など）で知らせて、自分どうしで「名前がぶつかった」と判断するためです。`setup_pi.sh` を実行していれば起きません。手で直すときは、次を実行してから再起動します。
  ```bash
  sudo sed -i -e "s/^#*use-ipv6=.*/use-ipv6=no/" -e "s/^#*allow-interfaces=.*/allow-interfaces=wlan0/" /etc/avahi/avahi-daemon.conf
  ```
  名前で見つからないときは、Wi-Fi ルーターの管理画面などで IP アドレスを調べ、`ssh photonglass@192.168.x.x` のように IP アドレスでつなぎます。
- **SSH の警告。** 名前を変えたり、カードを書き直したりすると、PC で `REMOTE HOST IDENTIFICATION HAS CHANGED` と出ることがあります。`ssh-keygen -R photon02.local` を実行してから、つなぎ直します。
- **API キーと Wi-Fi のパスワード。** 複製したカードには、`api_key.txt` と Wi-Fi のパスワードも入っています。カードやイメージファイルを人に渡したり、公開したりしないでください。
