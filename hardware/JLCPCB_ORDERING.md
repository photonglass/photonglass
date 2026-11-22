# JLCPCB での発注方法

基板2枚を、[JLCPCB](https://jlcpcb.com/) で「基板製造＋部品実装（PCBA）」まで発注する手順です。
画面の項目名は 2026年時点のものです。変わっていることがあるので、そのときは近い項目を選んでください。

## 使うファイル
| 基板 | ガーバー（基板製造） | BOM（部品表） | CPL（部品配置） |
|---|---|---|---|
| メイン基板 | [`main-board/gerber/OG19AWv2_main_gerber.zip`](main-board/gerber/OG19AWv2_main_gerber.zip) | [`main-board/jlcpcb-assembly/BOM.csv`](main-board/jlcpcb-assembly/BOM.csv) | [`main-board/jlcpcb-assembly/CPL.csv`](main-board/jlcpcb-assembly/CPL.csv) |
| カメラ基板 | [`camera-board/gerber/OG19_PC-3_camera_gerber.zip`](camera-board/gerber/OG19_PC-3_camera_gerber.zip) | [`camera-board/jlcpcb-assembly/BOM.csv`](camera-board/jlcpcb-assembly/BOM.csv) | [`camera-board/jlcpcb-assembly/CPL.csv`](camera-board/jlcpcb-assembly/CPL.csv) |

- ガーバーの zip は**解凍せずにそのまま**アップロードします。中身は銅箔・レジスト・シルク・メタルマスク（表裏）、外形、穴データ（メッキ／非メッキ）の11ファイルです。
- BOM の「Stock」列は作成時（2026-10-14）の在庫数です。発注時の在庫は画面で確認してください。

基板は1枚ずつ別の注文として（同じカートに）入れます。

## 1. 基板製造の設定
1. jlcpcb.com にログインし、トップの「Order now」（または「Instant Quote」）を開く。
2. 「Add gerber file」でガーバーの zip をアップロードする。外形サイズと層数は自動で読み取られる。
   - メイン基板：79 × 42 mm、カメラ基板：39.3 × 17.2 mm と表示されれば OK。
3. 設定は次の通り。書いていない項目は初期値のままでよい。

| 項目 | 設定 |
|---|---|
| Base Material | FR-4 |
| Layers | 2 |
| PCB Qty | 5（最小数） |
| PCB Thickness | 1.6 mm |
| PCB Color | 好きな色（緑以外は納期が少し延びることがある） |
| Surface Finish | HASL (with lead) または LeadFree HASL。ENIG にすると HDMI やカメラコネクタのはんだ付けが安定するが高くなる |
| Remove Order Number | 「Specify a location」にしない限り、シルクのどこかに注文番号が印刷される。消したい場合は有料オプションを選ぶ |

配線幅・間隔は最小 0.1524 mm（6 mil）、穴は最小 0.305 mm なので、標準仕様の範囲に収まっています。

## 2. 部品実装（PCB Assembly）の設定
1. 同じ画面の下の「PCB Assembly」をオンにする。
2. 設定は次の通り。

| 項目 | メイン基板 | カメラ基板 |
|---|---|---|
| PCBA Type | Economic（Standard でもよい） | Economic |
| Assembly Side | **Top Side** | **Top Side** |
| PCBA Qty | 2〜5（必要な数） | 2〜5 |
| Tooling holes | Added by JLCPCB | Added by JLCPCB |

3. 「NEXT」で基板の画像を確認し、もう一度「NEXT」。
4. **BOM** と **CPL** をアップロードし、「Process BOM & CPL」を押す。

## 3. 部品の確認（BOM 画面）
すべての部品に JLCPCB の部品番号（LCSC番号）が入っているので、自動で割り当てられます。各行に「✓」が付いていることを確認してください。

| 確認すること | 内容 |
|---|---|
| 在庫切れ（赤字）の部品 | 同じ値・同じフットプリントの別の部品を検索して置き換える。抵抗・コンデンサは値と大きさ（0603）が同じなら何でもよい |
| メイン基板の U$1（40ピンソケット） | スルーホール部品。**実装を頼むと THT（手実装）料金が追加される**。安くしたい場合は行のチェックを外し、届いてから自分ではんだ付けする |
| 「Extended」の部品 | 種類ごとに追加料金（部品の段取り費）がかかる。どの部品も代わりがないので、そのままでよい |

### 実装しない（手はんだで付ける）部品
メイン基板の次の部品は、操作感や外形に関わるので BOM から外してあります。別途買って、届いた基板に自分ではんだ付けしてください。

| 部品 | 型番 | 購入先 |
|---|---|---|
| VR1 ボリューム | R1001G16T2B-B10K | aitendo |
| SW_SUB / SW_UP / SW_DOWN | SKHHLPA010 | 秋月電子（107193） |
| SW_MAIN | P-03646（タクトスイッチ 赤） | 秋月電子 |
| SPK / 5V コネクタ（縦型） | JST B2B-XH-A(LF)(SN) | LCSC（C158012） |

型番と購入先は、発注リスト（2026-10-20 版）に合わせています。LCSC の部品は、同じ注文の中で「部品だけ」買うこともできます（JLCPCB の Parts → Order Parts、または LCSC.com）。

## 4. 部品の向きの確認（プレビュー画面）
「NEXT」で部品が基板に載ったプレビューが出ます。**ここがいちばん大事です**。部品の向きや位置がずれていたら、部品をクリックして回転・移動で直します。

ICは1番ピンの印（○や切り欠き）が、基板のシルクの1番ピンの印と合っているかを見ます。

| 基板 | 部品 | 確認すること |
|---|---|---|
| メイン | PCM5102A（TSSOP-20） | 1番ピンの位置 |
| メイン | PAM8304（MSOP-8） | 1番ピンの位置 |
| メイン | U$3 RGB LED | 1番ピン（角の切り欠き）の位置。6本の足がパッドに乗っているか |
| メイン | CN1 イヤホンジャック | 穴が基板の外側（右端）を向いているか |
| メイン | CN3 HDMI | 差し込み口が基板の外側を向いているか |
| メイン | CN2 カメラコネクタ | 部品の外形がシルクの枠と重なっているか |
| メイン | U$1 40ピンソケット | 実装を頼んだ場合のみ。表面（Top）に載っているか |
| カメラ | CN1 HDMI | 差し込み口が基板の端を向いているか |
| カメラ | CN2 カメラコネクタ | 差し込み口がカメラ側の端を向いているか |
| カメラ | SW1 タクトスイッチ | 押す部分が基板の端（シャッター側）を向いているか |

不安な部品があれば、この画面で「注文後に JLCPCB のエンジニアに確認してもらう」こともできます。注文後に向きの問題を見つけると、JLCPCB からメールで確認の連絡が来ます。

## 5. 注文
1. 「NEXT」で見積もりを確認し、「SAVE TO CART」。
2. もう1枚の基板も同じ手順でカートに入れる。
3. カートで配送方法を選んで支払う。届くまでは、通常 1〜3 週間程度。

## 届いたら
1. 手はんだの部品（上の表）を付ける。
2. Raspberry Pi Zero 2 W に載せ、[`software/test/hw_test.py`](../software/test/hw_test.py) で動作を確認する（Raspberry Pi の準備は [`docs/SETUP_RASPBERRY_PI.md`](../docs/SETUP_RASPBERRY_PI.md)、全体の流れは [`docs/BUILD_GUIDE.md`](../docs/BUILD_GUIDE.md)）。
3. スピーカーのコネクタの向きは [`main-board/images/speaker_connector_orientation.png`](main-board/images/speaker_connector_orientation.png) を見る。

## ガーバーについて
ガーバーは、Eagle のデータ（`eagle/*.brd`）からスクリプトで作ったものです。ベタGNDは Eagle の設定どおりに計算し、ネット間の間隔違反 0件・未接続 0件を確認しています。
基板データを直した場合は、KiCad（`kicad/`）または Fusion / Eagle の CAM 出力でガーバーを作り直してください。KiCad では「ファイル → 製造用ファイル出力 → ガーバー」と「ドリルファイル」で出力し、1つの zip にまとめます。
