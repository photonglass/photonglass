# 基板 / Boards

| 基板 | 役割 | 大きさ |
|---|---|---|
| [`main-board/`](main-board) OG19AWv2 | Raspberry Pi Zero 2 W の40ピンに挿す。音声出力（PCM5102A + PAM8304）、スピーカー用コネクタ、ボタン4個、RGB LED、ヘッドホンジャック、電源用コネクタ（5V）、カメラ基板へのHDMI | 79 × 42 mm、2層 |
| [`camera-board/`](camera-board) OG19 PC-3 | カメラユニットの中の基板。カメラ（Zero Spy Camera）をつなぎ、カメラボタン（シャッター）とLEDを載せる。HDMIケーブルでメイン基板へ | 39.3 × 17.2 mm、2層 |

## ファイルの開き方
| ソフト | 開くファイル | 方法 |
|---|---|---|
| **KiCad 9 以降** | `kicad/*.kicad_pro` | ダブルクリックで開く。KiCad 10 で開いて保存すると、ファイルが新しい形式になり KiCad 9 では開けなくなる |
| **Fusion**（旧 Eagle） | `eagle/*.sch` / `*.brd` | Fusion の「ファイル → 開く」で `.sch` を選ぶと、回路図と基板がセットで電子設計として開く |
| Eagle 9.x | `eagle/*.sch` / `*.brd` | そのまま開く（Eagle は 2026年6月に販売とサポートが終了しているので、これから使うなら KiCad か Fusion） |

Eagle・KiCad の部品ライブラリのうち、jst-xh（メイン基板の `5V`・`SPK` のコネクタ）は、yuhki50 氏の [eagle-pcb-library](https://github.com/yuhki50/eagle-pcb-library)（MIT ライセンス）に由来します。

## JLCPCB で作る
各基板のフォルダに、発注に必要なファイル（ガーバー・BOM・CPL）がそろっています。
発注の手順は **[`JLCPCB_ORDERING.md`](JLCPCB_ORDERING.md)** を見てください（基板製造の設定、部品実装の設定、部品の向きの確認、手はんだで付ける部品）。

スピーカー用コネクタの向きは [`main-board/images/speaker_connector_orientation.png`](main-board/images/speaker_connector_orientation.png) を見てください。

## 元設計（OTON GLASS ver5）からの変更
- 在庫のない部品を JLCPCB で買える部品に置き換え（ヘッドホンジャック、RGB LED、ピンソケット、抵抗値の近似など）。詳しくは [`docs/parts_list.md`](../docs/parts_list.md)。
- メイン基板：上辺の段差をなくした、左右の角を対称な面取りにした、HDMI とヘッドホンジャックの前面をそろえた、ボタンを基板の端まで出した、不足していたビアを追加した、など。
- **RGB LED の色と GPIO の対応が変わっています**：GPIO9 = 赤、GPIO11 = 緑、GPIO10 = 青。

## 版の履歴
| 版（シルクの表記） | 変更 |
|---|---|
| メイン基板 `2026 / PB-4`、カメラ基板 `2026 / PC-4` | シルクの名前を「PHOTON GLASS」に変更（前の版はメイン基板「OTONGLASS」、カメラ基板「OTON GLASS」）。メイン基板の表面に、リポジトリの URL（`github.com/photonglass/photonglass`）とライセンス（`CERN-OHL-S v2`）を追加（2026-11-25 に、この文字と「PHOTON GLASS / 2026 / PB-4」を高さ 1.0 mm・線の太さ 0.16 mm に拡大。JLCPCB の最小値は高さ 1.0 mm・線の太さ 0.153 mm）。**銅箔・穴・レジスト・メタルマスク・外形は前の版と同じ**で、変わったのは表面のシルク（`.GTO`）だけ。設計データに残っていた、手はんだ部品（VR1・SW_MAIN・SW_SUB／UP／DOWN）の旧部品の LCSC 番号を外し、実際に使う部品の型番（`MPN`）と購入先（`SUPPLIER`）に置き換え |
| メイン基板 `2019 / PB-3`、カメラ基板 `2019 / PC-3` | 元設計を JLCPCB 向けに直した最初の版（上の「元設計からの変更」） |

カメラ基板は小さく、裏面にも GND のビアが並んでいて URL を入れる場所がないため、URL とライセンスはメイン基板にだけ入れています。

## 組み立て後のテスト
[`software/test/hw_test.py`](../software/test/hw_test.py) を Raspberry Pi で実行すると、LED → ボタン → スピーカー → カメラの順に確認できます。
Raspberry Pi の準備とテストの実行方法は [`docs/SETUP_RASPBERRY_PI.md`](../docs/SETUP_RASPBERRY_PI.md) にあります。
