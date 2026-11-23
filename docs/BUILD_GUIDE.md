# PHOTON GLASS 組み立てガイド

PHOTON GLASS を一から作るときの、作業の順番をまとめたページです。
それぞれの作業の詳しいやり方は、リンク先のドキュメントを見てください。

## 全体の流れ

| 順番 | 作業 | 詳しいやり方 |
|---|---|---|
| 0 | 必要なものをそろえる | このページの「[0. 必要なもの](#0-必要なもの)」 |
| 1 | 基板を発注する | [`hardware/JLCPCB_ORDERING.md`](../hardware/JLCPCB_ORDERING.md) |
| 2 | 手はんだで部品を付ける | [`hardware/JLCPCB_ORDERING.md` の「実装しない（手はんだで付ける）部品」](../hardware/JLCPCB_ORDERING.md#実装しない手はんだで付ける部品) |
| 3 | 筐体を印刷する | 本体：[`enclosure/main-body/README.md` の「印刷設定」](../enclosure/main-body/README.md#印刷設定)、カメラユニット：[`enclosure/camera-unit/README.md` の「印刷設定」](../enclosure/camera-unit/README.md#印刷設定) |
| 4 | 組み立てる | このページの「[4. 組み立てる](#4-組み立てる)」 |
| 5 | Raspberry Pi をセットアップする | [`SETUP_RASPBERRY_PI.md`](SETUP_RASPBERRY_PI.md) の 1〜7 |
| 6 | 動作テスト（hw_test） | [`SETUP_RASPBERRY_PI.md` の「8. 動作テストをする」](SETUP_RASPBERRY_PI.md#8-動作テストをする) |
| 7 | プログラムを動かす | [`SETUP_RASPBERRY_PI.md` の「9. プログラムを動かす」](SETUP_RASPBERRY_PI.md#9-プログラムを動かす) |

## 0. 必要なもの

### 基板・筐体・電源ケーブルの部品
それぞれのドキュメントの部品表を見てください。
- 基板（JLCPCB で実装する部品と、手はんだで付ける部品）：[`hardware/JLCPCB_ORDERING.md`](../hardware/JLCPCB_ORDERING.md)。全部品の詳細は [`parts_list.md`](parts_list.md)
- 本体の筐体（ネジ）：[`enclosure/main-body/README.md` の「必要な部品」](../enclosure/main-body/README.md#必要な部品)
- カメラユニット（カメラ、ネジ、結束バンド）：[`enclosure/camera-unit/README.md` の「必要な部品」](../enclosure/camera-unit/README.md#必要な部品)
- 電源ケーブル（USB プラグ、電線、コネクタなど）：[`enclosure/usb-power-cable/README.md` の「部品」](../enclosure/usb-power-cable/README.md#部品)
- 3D プリンターの材料（PETG）：[`enclosure/main-body/README.md` の「印刷設定」](../enclosure/main-body/README.md#印刷設定)（本体1台で約 65〜75 g）、[`enclosure/camera-unit/README.md` の「印刷設定」](../enclosure/camera-unit/README.md#印刷設定)

### そのほかに必要なもの

| もの | 型番など | 使うところ |
|---|---|---|
| Raspberry Pi Zero 2 WH | ピンヘッダ実装済みのもの | メイン基板の40ピンソケットに挿す |
| microSD カード | SanDisk Ultra 32GB | Raspberry Pi の OS を入れる |
| FFC ケーブル | Würth Elektronik 6876 シリーズ 687622100002（100 mm、ピッチ 0.5 mm） | メイン基板と Raspberry Pi をつなぐ |
| HDMI ケーブル | CAC-HD14US07BK（0.7 m） | メイン基板とカメラユニット（カメラ基板）をつなぐ |
| スピーカー | MSI28-12R（秋月電子） | メイン基板の `SPK` コネクタにつなぐ |
| モバイルバッテリー | cheero Canvas 3200mAh IoT機器対応 CHE-061-BK-IOT2 | 電源（[`enclosure/usb-power-cable/README.md` の「使うモバイルバッテリー」](../enclosure/usb-power-cable/README.md#使うモバイルバッテリー)） |
| メガネ | — | カメラユニットを取り付ける |

Raspberry Pi の初期設定では、次のものも使います。
- モニターと、mini HDMI → HDMI の変換ケーブル（またはアダプター）。Raspberry Pi Zero 2 W の映像出力は mini HDMI 端子です。
- キーボードとマウスと、micro USB（オス）→ USB-A（メス）の変換ケーブル（OTG ケーブル）。Raspberry Pi Zero 2 W のデータ用の USB 端子は micro USB が1つだけなので、キーボードとマウスを両方つなぐときは、USB ハブを使うか、1つのレシーバーで使えるワイヤレスのキーボードとマウスを使います。開発では、microUSB L字ケーブル AFSSLCBL と、USB-A メスのコネクタ USB-4AF203AS を使っています。

## 1. 基板を発注する
メイン基板とカメラ基板を、JLCPCB に「基板製造＋部品実装」で発注します。
- 手順：[`hardware/JLCPCB_ORDERING.md`](../hardware/JLCPCB_ORDERING.md) の 1〜5
- 部品の詳細（元の部品との違い、データシート）：[`parts_list.md`](parts_list.md)

## 2. 手はんだで部品を付ける
届いたメイン基板に、実装を頼まなかった部品をはんだ付けします。
- 付ける部品：[`hardware/JLCPCB_ORDERING.md` の「実装しない（手はんだで付ける）部品」](../hardware/JLCPCB_ORDERING.md#実装しない手はんだで付ける部品)
- 40ピンソケット（`U$1`）の実装を頼まなかった場合は、これも付けます（[`hardware/JLCPCB_ORDERING.md` の「3. 部品の確認（BOM 画面）」](../hardware/JLCPCB_ORDERING.md#3-部品の確認bom-画面)）。
- スピーカー用コネクタの向き：[`hardware/main-board/images/speaker_connector_orientation.png`](../hardware/main-board/images/speaker_connector_orientation.png)

## 3. 筐体を印刷する
- 本体：[`enclosure/main-body/README.md` の「印刷設定」](../enclosure/main-body/README.md#印刷設定)
- カメラユニット：[`enclosure/camera-unit/README.md` の「印刷設定」](../enclosure/camera-unit/README.md#印刷設定)
- 電源ケーブルの USB プラグのカバー：[`enclosure/usb-power-cable/README.md` の「1. カバーを印刷する」](../enclosure/usb-power-cable/README.md#1-カバーを印刷する)

## 4. 組み立てる
- 本体：[`enclosure/main-body/README.md` の「組み立て」](../enclosure/main-body/README.md#組み立て)（ボディ背面を前面にネジ4本で留める）
- カメラユニット：[`enclosure/camera-unit/README.md` の「組み立て」](../enclosure/camera-unit/README.md#組み立て)（カメラとカメラ基板の接続、メガネへの取り付けまで）
- 電源ケーブル：[`enclosure/usb-power-cable/README.md` の「作り方」](../enclosure/usb-power-cable/README.md#作り方)（最後の「6. 確認」まで必ず行う）

### つなぐ場所

| つなぐもの | メイン基板の側 | 相手 | 注意 |
|---|---|---|---|
| Raspberry Pi Zero 2 WH | 40ピンソケット（`U$1`） | Raspberry Pi のピンヘッダ | |
| FFC ケーブル | `CN2`（カメラコネクタ） | Raspberry Pi のカメラコネクタ | 向きや差し込みが正しくないと、カメラが見つからない（[動作テスト](SETUP_RASPBERRY_PI.md#8-動作テストをする)で確かめる） |
| HDMI ケーブル | `CN3`（HDMI） | カメラ基板の `CN1`（HDMI） | カメラ基板とつなぐための端子で、モニター用ではない |
| スピーカー | `SPK`（2ピン） | スピーカー | コネクタの向き：[`speaker_connector_orientation.png`](../hardware/main-board/images/speaker_connector_orientation.png) |
| 電源ケーブル | `5V`（2ピン） | モバイルバッテリー | + と − を逆にすると Raspberry Pi が壊れる。つなぐ前に「[6. 確認](../enclosure/usb-power-cable/README.md#6-確認基板につなぐ前に必ず)」を必ず行う |

## 5. Raspberry Pi をセットアップする
OS の書き込みから、音声出力（DAC）の設定、プログラムのコピー、API キーの用意までを行います。
- 手順：[`SETUP_RASPBERRY_PI.md`](SETUP_RASPBERRY_PI.md) の 1〜7

## 6. 動作テスト（hw_test）
LED → ボタン → スピーカー → カメラ の順に、組み立てたものが動くかを確かめます。
- 手順：[`SETUP_RASPBERRY_PI.md` の「8. 動作テストをする」](SETUP_RASPBERRY_PI.md#8-動作テストをする)

## 7. プログラムを動かす
- 手順：[`SETUP_RASPBERRY_PI.md` の「9. プログラムを動かす」](SETUP_RASPBERRY_PI.md#9-プログラムを動かす)
- 電源を入れたら自動で動くようにする：[`SETUP_RASPBERRY_PI.md` の「10. 電源を入れたら自動で動くようにする（systemd）」](SETUP_RASPBERRY_PI.md#10-電源を入れたら自動で動くようにするsystemd)
- 2つのプログラム（`main_async.py` と `main_seq.py`）の違い：[`software/README.md`](../software/README.md)

## 設計を変えるとき
- 基板：[`hardware/README.md` の「ファイルの開き方」](../hardware/README.md#ファイルの開き方)、KiCad 版の説明（[メイン基板](../hardware/main-board/kicad/README.md)・[カメラ基板](../hardware/camera-board/kicad/README.md)）
- 本体の筐体：[`enclosure/main-body/README.md` の「設計を変える」](../enclosure/main-body/README.md#設計を変える)
- カメラユニットの筐体：[`enclosure/camera-unit/README.md` の「設計を変える」](../enclosure/camera-unit/README.md#設計を変える)
- 電源ケーブルのカバー：[`enclosure/usb-power-cable/README.md` の「ファイル」](../enclosure/usb-power-cable/README.md#ファイル)
- プログラム：[`software/README.md`](../software/README.md)
