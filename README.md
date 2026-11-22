# PHOTON GLASS

一人称のカメラで捉えるイメージから，音などのフィードバックでユーザーにインタラクションする，メガネ型のデバイス〈PHOTON GLASS〉のハードウェアデータです。
PHOTON GLASS は、OTON GLASS ver5 を元にしながら、自作の容易さや改変性を高め、ツールキットとして新しく開発したものです。
基板2枚（メイン基板・カメラ基板）の設計データ、3Dプリンターで造形できるカメラユニットの筐体と電源ケーブルのカバー、本体のプログラム、組み立てとセットアップの手順を公開しています。

*[English summary](#english-summary) below.*

![カメラユニット](enclosure/camera-unit/images/overview.png)

## 中身

| フォルダ | 内容 | 開けるソフト |
|---|---|---|
| [`hardware/`](hardware/README.md) | 基板2枚の概要、ファイルの開き方、元設計からの変更 | — |
| [`hardware/main-board/`](hardware/main-board) | メイン基板（Raspberry Pi Zero 2 W に載る音声・ボタン基板） | KiCad 9 以降 / Fusion（Eagle形式） |
| [`hardware/camera-board/`](hardware/camera-board) | カメラ基板（HDMIケーブルでメイン基板とつながる） | KiCad 9 以降 / Fusion（Eagle形式） |
| [`enclosure/camera-unit/`](enclosure/camera-unit) | カメラユニットの筐体・メガネ用アタッチメント | STEP（Fusion・FreeCAD など）/ STL・3MF（スライサー）/ Python（CadQuery） |
| [`enclosure/usb-power-cable/`](enclosure/usb-power-cable) | モバイルバッテリーからメイン基板へ給電するケーブルの作り方（配線・部品）と、USB プラグのカバー | STEP / STL / Python（CadQuery） |
| [`software/`](software) | 本体プログラムと効果音。普段使うのは `main_async.py`、仕組みを学ぶなら流れの読みやすい `main_seq.py`（違いは [`software/README.md`](software/README.md)） | Python 3（Raspberry Pi） |
| [`software/test/`](software/test) | 組み立て後の動作テスト用スクリプト（Raspberry Pi で実行） | Python 3 |
| [`docs/`](docs) | 組み立てガイド（[`BUILD_GUIDE.md`](docs/BUILD_GUIDE.md)）、Raspberry Pi のセットアップ（[`SETUP_RASPBERRY_PI.md`](docs/SETUP_RASPBERRY_PI.md)）、部品リスト（[`parts_list.md`](docs/parts_list.md)：データシート・回路記号の照合結果） | — |

## はじめての人へ
- **まず読む**：[`docs/BUILD_GUIDE.md`](docs/BUILD_GUIDE.md) に、発注から動かすまでの作業の順番と、それぞれで読むドキュメントをまとめています。
- **基板を作る**：[`hardware/JLCPCB_ORDERING.md`](hardware/JLCPCB_ORDERING.md) の手順で、JLCPCB に部品実装まで発注できます（ガーバー・部品表・部品配置ファイル付き）。
- **筐体を印刷する**：[`enclosure/camera-unit/README.md`](enclosure/camera-unit/README.md) に、印刷設定（Bambu Lab A1 / PETG）と組み立て手順があります。
- **Raspberry Pi を準備する**：[`docs/SETUP_RASPBERRY_PI.md`](docs/SETUP_RASPBERRY_PI.md) に、OS の書き込みから動作テスト、自動起動までの手順があります。
- **設計を変える**：基板は KiCad か Fusion で、筐体は `src/` の Python スクリプトの数値を変えるか、STEP を CAD に読み込んで編集します。

## 質問・不具合の報告

質問や不具合の報告は、GitHub の Issues で受け付けています。
https://github.com/photonglass/photonglass/issues

## 憲法
PHOTON GLASS の理念と利用、名称、特許については、[憲法（`CHARTER.md`）](CHARTER.md)に定めています。

## ライセンス
Copyright (C) 株式会社オトングラス

対象ごとに、次のライセンスで公開しています。

| 対象 | 含まれるもの | ライセンス | 全文 |
|---|---|---|---|
| ソフトウェア | `software/` のプログラム（`main_async.py`・`main_seq.py`・`test/` など） | GNU General Public License v3.0（GPL-3.0-only） | [`LICENSE`](LICENSE) |
| ハードウェア | `hardware/`（基板の KiCad・Eagle データ、BOM・CPL）、`enclosure/`（筐体の CadQuery スクリプト）と、それらの生成物（ガーバー、STL・STEP・3MF）。**例外**：README・写真・画像と `hardware/JLCPCB_ORDERING.md` は除く（ドキュメント・写真・画像として CC BY-SA 4.0） | CERN Open Hardware Licence Version 2 - Strongly Reciprocal（CERN-OHL-S v2） | [`LICENSE-HARDWARE`](LICENSE-HARDWARE) |
| ドキュメント・写真・画像 | `docs/`、`CHARTER.md`、各フォルダの `README.md`、`hardware/JLCPCB_ORDERING.md`、写真・画像（各フォルダの `images/` など） | クリエイティブ・コモンズ 表示-継承 4.0 国際（CC BY-SA 4.0） | 公式テキスト：[日本語](https://creativecommons.org/licenses/by-sa/4.0/legalcode.ja)・[English](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en) |
| サウンド | `software/sound/` の効果音 | CC BY-SA 4.0 | 同上 |

- 各 README、写真・画像、`hardware/JLCPCB_ORDERING.md` は、`hardware/`・`enclosure/`・`software/` の中にあっても CC BY-SA 4.0 です。`software/sound/` も、`software/` の中にありますが CC BY-SA 4.0 です。

### CC BY-SA 4.0 のクレジット表記
ドキュメント・写真・画像・サウンドは、株式会社オトングラスが CC BY-SA 4.0 で提供しています。全文のファイルはこのリポジトリに入れていないので、公式テキスト（[日本語](https://creativecommons.org/licenses/by-sa/4.0/legalcode.ja)・[English](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en)）を見てください。

使うときは、次のようにクレジットを表記してください。改変したときは、改変したことも書いてください。
```
PHOTON GLASS（Copyright (C) 株式会社オトングラス）
https://github.com/photonglass/photonglass
CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/
```

### かんたんな説明
正確な条件は、各ライセンスの全文を見てください。

**できること**
- 誰でも無料で、このデータで基板や筐体を作り、使い、売ることができます。
- 自由に改変できます。

**守ること**
- 作ったもの・改変したものを人に配ったり売ったりするときは、元と同じライセンスで公開する。
  - ソフトウェアとハードウェアは、受け取った人がソース（プログラム・設計データ）を手に入れられるようにする。ハードウェアの場合は、ソースを渡すか、ソースの置き場所を知らせる。
- 著作権表示とライセンスの表示を消さない。改変した場合は、いつ・どこを変えたかを書く。
- ドキュメント・写真・画像・サウンドを使うときは、上のクレジットを表記する。

**その他**
- 無保証です（作ったものが動かなくても、作者は責任を負いません）。
- 自分で使うだけなら、改変したデータを公開する義務はありません。
- 特許の扱いは、憲法の[「3. 特許について」](CHARTER.md#3-特許について)を見てください。

### 商用ライセンス
クローズドな製品への組み込みなど、各ライセンスの条件と異なる利用を希望する場合は、商用ライセンスを個別に契約できます。問い合わせはこちら：https://note.com/keisukeshimakage/n/nef3c9957ae25

### 含まれていないもの
- 部品メーカーや EasyEDA/LCSC が配布している部品の3Dモデル（再配布の条件がはっきりしないため）。基板の3D形状は KiCad や Fusion の3Dビューで確認してください。
- Google Cloud の API キー（各自で用意して、プログラムと同じフォルダの `api_key.txt` に書く。書き方は [`software/README.md`](software/README.md#動かし方)）。
- 本体の筐体（カメラユニットとは別の筐体）の3Dモデルデータ。追加を準備中です。

### クレジット
**PHOTON GLASS（2026年）**
- 回路・基板設計、ドキュメンテーション：山中将治（Masaharu Yamanaka）
- プロダクトデザイン：小松靖知（Yasutomo Komatsu）
- プログラミング：石塚日向（Hinata Ishizuka）
- アドバイジング：須田拓也（Hiroya Suda）、高橋卓久真（Takuma Takahashi）、陳冠宇（Chen Kuan-Yu）

**OTON GLASS ver5（2019年）― PHOTON GLASSの元となったモデル**
- エンジニアリング：宮下恵太（Keita Miyashita）
- サーバーサイドエンジニアリング：鶴岡秀樹（Hideki Tsuruoka）
- プロダクトデザイン：佐野友優（Tomomasa Sano）
- サウンドデザイン：田中堅大（Kenta Tanaka）

---

## English summary
Hardware for **PHOTON GLASS**, a glasses-type device that interacts with users via feedback such as sound, based on images captured by a first-person camera.
PHOTON GLASS was newly developed as a toolkit based on OTON GLASS ver5, with improved ease of self-building and modifiability.
The documentation is written in Japanese.
- `hardware/` – main board and camera board (KiCad 9 and Eagle/Fusion formats, Gerbers, JLCPCB BOM/CPL)
- `enclosure/camera-unit/` – FDM-printable camera enclosure: STEP, print-ready STL/3MF, parametric CadQuery source, print settings
- `enclosure/usb-power-cable/` – power cable from a mobile battery to the main board: wiring, parts and a 3D-printable cover for the USB plug
- `software/` – Python programs for the Raspberry Pi Zero 2 W (press the camera button to take a photo, recognise its text with Google Cloud Vision and read it aloud with Google Cloud Text-to-Speech), sound effects and a hardware test script
- `docs/` – build guide, Raspberry Pi setup guide and parts list
- Licences (Copyright (C) OTON GLASS Inc.):
  - Software (`software/`): **GPL-3.0-only** (see `LICENSE`)
  - Hardware (`hardware/`, `enclosure/`: board data, CadQuery scripts and their outputs such as Gerbers and STL/STEP/3MF; except READMEs, images and `hardware/JLCPCB_ORDERING.md`): **CERN-OHL-S-2.0** (see `LICENSE-HARDWARE`)
  - Documentation (`docs/`, `CHARTER.md`, READMEs, `hardware/JLCPCB_ORDERING.md`), photos and images, and sounds (`software/sound/`): **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/legalcode.en)
  - For uses outside these licences, such as embedding in a closed product, a commercial licence is available: https://note.com/keisukeshimakage/n/nef3c9957ae25
- Charter (in Japanese): `CHARTER.md` – principles and use, the PHOTON GLASS name, and patents
- Questions and bug reports: GitHub Issues (https://github.com/photonglass/photonglass/issues)
