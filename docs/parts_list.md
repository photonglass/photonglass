PHOTON GLASS · OG19 · JLCPCB 発注用

# PHOTON GLASS 部品リスト

メイン基板（OG19AWv2）とカメラ基板（OG19_PC-3）で使う全部品の一覧です。部品ごとに次の内容をまとめています。

- 元の部品と同じものか
- データシート
- 回路図記号のピン（ピン名 → パッド）が、データシートのピン配置と一致しているか

部品番号はすべて JLCPCB の部品ライブラリで在庫を確認済みです（2026-10-15 時点）。

- JLCPCB 実装 **13** 行（メイン） / **6** 行（カメラ）
- 手はんだ **7** 個（メイン基板）
- 回路記号の不一致 **0**

## メイン基板 OG19AWv2

「実装」列が「手はんだ」の行は、BOM / CPL には含めていません

| Ref | 元の部品 | 今回の部品 | 実装 | 回路記号の照合 | 資料 |
|---|---|---|---|---|---|
| PCM5102A<br>オーディオDAC | TI PCM5102A（TSSOP-20）<br>同一 | `PCM5102APWR`<br>Texas Instruments · `C107671` · 在庫 5,831 | JLCPCB 実装 | 一致<br>1 CPVDD〜20 DVDD の全20ピンが TI データシート・JLCPCB の記号と一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2409291903_Texas-Instruments-PCM5102APWR_C107671.pdf) [LCSC](https://www.lcsc.com/product-detail/adcs-dacs-special-purpose_texas-instruments-pcm5102apwr_C107671.html) [TI](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf) |
| PAM8304<br>スピーカーアンプ | Diodes PAM8304（MSOP-8）<br>同一 | `PAM8304ASR`<br>Diodes Incorporated · `C581342` · 在庫 2,684 | JLCPCB 実装 | 一致<br>1 OUT+ / 2 PVDD / 3 VDD / 4 IN− / 5 IN+ / 6 SD / 7 GND / 8 OUT− が一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2006092117_Diodes-Incorporated-PAM8304ASR_C581342.pdf) [LCSC](https://www.lcsc.com/product-detail/audio-amplifiers_diodes-incorporated-pam8304asr_C581342.html) [Diodes](https://www.diodes.com/assets/Datasheets/PAM8304.pdf) |
| CN1<br>3.5mm ヘッドホンジャック | Switchcraft 35RASMT4BHNTRX（在庫0）<br>代替 | `SJ-43516-SMT-TR`<br>CUI · `C4992780` · 在庫 136 | JLCPCB 実装 | 一致・注意あり<br>4極（TRRS）品。Ring2 をスリーブ（AGND）に接続し、ステレオプラグで元と同じ動作。注意点 1 | [データシート](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2401261118_CUI-SJ-43516-SMT-TR_C4992780.pdf) [LCSC](https://www.lcsc.com/product-detail/audio-connectors-headphones_cui-sj-43516-smt-tr_C4992780.html) [元: Switchcraft](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2401261118_Switchcraft-35RASMT4BHNTRX_C4992744.pdf) |
| CN2<br>カメラ用 FFC 22P | Hirose FH12-22S-0.5SH<br>同一 | `FH12-22S-0.5SH(55)`<br>HRS(Hirose) · `C597981` · 在庫 684 | JLCPCB 実装 | 一致<br>部品・記号とも元設計のまま。パッド1〜22の並びが JLCPCB の部品データと一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_HRS-Hirose-FH12-22S-0-5SH-55_C597981.pdf) [LCSC](https://www.lcsc.com/product-detail/ffc-fpc-flat-flexible-connector-assemblies_hrs-hirose-fh12-22s-0-5sh-55_C597981.html) |
| CN3<br>HDMI Type-A | Amphenol 10029449 系<br>同シリーズ | `10029449-111RLF`<br>Amphenol ICC · `C427307` · 在庫 1,556 | JLCPCB 実装 | 一致<br>1〜19番が HDMI 規格の割当と一致（18 +5V、19 HPD）。シェル脚4本は GND | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Amphenol-ICC-10029449-111RLF_C427307.pdf) [LCSC](https://www.lcsc.com/product-detail/hdmi-connectors_amphenol-icc-10029449-111rlf_C427307.html) |
| U\$1<br>Raspberry Pi 40ピン接続（表面に実装） | Samtec SSW-120-02-G-D（在庫5・約\$10）<br>代替 | `2.54-2*20P`<br>BOOMELE(Boom Precision Elec) · `C5124634` · 在庫 8,734 | JLCPCB 実装 | 一致<br>同形状の汎用ソケット（高さ8.5mm）。1 3.3V / 2 5V … 40 GPIO21 が標準ピン配置と一致。Eagle では Pi を裏返して重ねるためのピン配置の鏡像として反転配置、実物は表面に実装（CPL も Top） | [データシート](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2401111126_BOOMELE-Boom-Precision-Elec-2-54-2-20P_C5124634.pdf) [LCSC](https://www.lcsc.com/product-detail/female-headers_boomele-boom-precision-elec-2-54-2-20p_C5124634.html) [元: Samtec](https://www.samtec.com/products/ssw) |
| U\$3<br>状態表示 RGB LED | Kingbright KPF-3236SURKMGKPBC（JLC未登録）<br>代替 | `S6-3528RGBTA`<br>TUOZHAN · `C2843672` · 在庫 7,379 | JLCPCB 実装 | 一致・注意あり<br>ピン配置はデータシートどおり。色の並びが変わり、ソフト側の変更が必要。注意点 3 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2109061230_TUOZHAN-S6-3528RGBTA_C2843672.pdf) [LCSC](https://www.lcsc.com/product-detail/rgb-leds_tuozhan-s6-3528rgbta_C2843672.html) |
| VR1<br>音量ボリューム（2連） | ALPS RK10J（型番指定なし）<br>同シリーズ | `RK10J12E002L`<br>ALPSALPINE · `C231765` · 在庫 1,278 | 手はんだ | 一致・注意あり<br>端子の並び（共通・ワイパー・端）が一致。抵抗カーブは B（直線型）。注意点 2 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_1810170234_ALPSALPINE-RK10J12E002L_C231765.pdf) [LCSC](https://www.lcsc.com/product-detail/potentiometers-variable-resistors_alpsalpine-rk10j12e002l_C231765.html) |
| SW_SUB, SW_UP, SW_DOWN<br>サイドプッシュスイッチ | ALPS SKHH サイドプッシュ（型番指定なし）<br>同シリーズ | `SKHHLQA010`<br>ALPSALPINE · `C125034` · 在庫 2,449 | 手はんだ | 一致・注意あり<br>端子2本＋取付脚2本が一致。ボタン長さ 8.35mm は今回の選定。注意点 4 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2410121957_ALPSALPINE-SKHHLQA010_C125034.pdf) [LCSC](https://www.lcsc.com/product-detail/tactile-switches_alpsalpine-skhhlqa010_C125034.html) |
| SW_MAIN<br>メインスイッチ（裏面） | 秋月 P-03647 = Cosland DTS-63-N-V（6.2mm角・高さ7mm）<br>同シリーズ | `DTS-63K-V`<br>Diptronics · `C141874` · 在庫 794 | 手はんだ | 一致<br>同シリーズ・同寸法。4端子の導通ペア（P2-P3 = GND、P1-P4 = SW_BODY）が一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Diptronics-DTS-63K-V_C141874.pdf) [LCSC](https://www.lcsc.com/product-detail/tactile-switches_diptronics-dts-63k-v_C141874.html) [元: 秋月](https://akizukidenshi.com/goodsaffix/ts-0606_20200714.pdf) |
| SPK, 5V<br>2ピンコネクタ（縦型） | JST S2B-XH-A（横型）<br>代替 | `B2B-XH-A(LF)(SN)`<br>JST · `C158012` · 在庫 241,489 | 手はんだ | 一致<br>縦型（上から挿す）に変更。パッドは同じ。ピン1 = 四角パッド（5V / SPK+）。本体が基板内に収まるよう 0.5mm 下げて配置 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_JST-B2B-XH-A-LF-SN_C158012.pdf) [LCSC](https://lcsc.com/product-detail/wire-to-board-connector_jst-b2b-xh-a-lf-sn_C158012.html) |
| C2〜C4, C7〜C11<br>パスコン 0.1µF | 0603 0.1µF<br>同一 | `CC0603KRX7R9BB104`<br>YAGEO · `C14663` · 在庫 51,101,481 | JLCPCB 実装 | 一致<br>値・サイズ同じ（50V X7R） | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2211101700_YAGEO-CC0603KRX7R9BB104_C14663.pdf) [LCSC](https://www.lcsc.com/product-detail/multilayer-ceramic-capacitors-mlcc-smd-smt_yageo-cc0603krx7r9bb104_C14663.html) |
| C1<br>2.2µF | 0603 2.2µF<br>同一 | `CL10A225KO8NNNC`<br>Samsung Electro-Mechanics · `C23630` · 在庫 3,546,419 | JLCPCB 実装 | 一致<br>値・サイズ同じ（16V X5R） | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL10A225KO8NNNC_C23630.pdf) [LCSC](https://www.lcsc.com/product-detail/multilayer-ceramic-capacitors-mlcc-smd-smt_samsung-electro-mechanics-cl10a225ko8nnnc_C23630.html) |
| C5, C6<br>DAC 出力フィルタ 2200pF | 0603 2200pF<br>同一 | `0603B222K500NT`<br>FH (Guangdong Fenghua Advanced Tech) · `C1604` · 在庫 991,140 | JLCPCB 実装 | 一致<br>値・サイズ同じ（X7R）。音質優先なら C0G の C33353 も可 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_FH--Guangdong-Fenghua-Advanced-Tech-0603B222K500NT_C1604.pdf) [LCSC](https://www.lcsc.com/product-detail/multilayer-ceramic-capacitors-mlcc-smd-smt_fh-guangdong-fenghua-advanced-tech-0603b222k500nt_C1604.html) |
| R1〜R4<br>470Ω | 0603 470Ω<br>同一 | `0603WAF4700T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C23179` · 在庫 5,713,240 | JLCPCB 実装 | 一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF4700T5E_C23179.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf4700t5e_C23179.html) |
| R5, R6<br>470kΩ | 0603 470kΩ<br>同一 | `0603WAF4703T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C23178` · 在庫 1,321,083 | JLCPCB 実装 | 一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF4703T5E_C23178.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf4703t5e_C23178.html) |
| R7〜R9<br>LED 電流制限 | 0603 40Ω<br>代替 | `0603WAF402JT5E`<br>UNI-ROYAL(Uniroyal Elec) · `C23047` · 在庫 24,004 | JLCPCB 実装 | 一致<br>40Ω ちょうどの在庫品が JLCPCB にないため 40.2Ω ±1%（差 0.5% で部品の許容差内） | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF402JT5E_C23047.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf402jt5e_C23047.html) |

## カメラ基板 OG19_PC-3

全部品 JLCPCB 実装

| Ref | 元の部品 | 今回の部品 | 実装 | 回路記号の照合 | 資料 |
|---|---|---|---|---|---|
| CN1<br>HDMI Type-A | Amphenol 10029449 系<br>同シリーズ | `10029449-111RLF`<br>Amphenol ICC · `C427307` · 在庫 1,556 | JLCPCB 実装 | 一致<br>メイン基板と同じ | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Amphenol-ICC-10029449-111RLF_C427307.pdf) [LCSC](https://www.lcsc.com/product-detail/hdmi-connectors_amphenol-icc-10029449-111rlf_C427307.html) |
| CN2<br>カメラ用 FFC 22P | Hirose FH12-22S-0.5SH<br>同一 | `FH12-22S-0.5SH(55)`<br>HRS(Hirose) · `C597981` · 在庫 684 | JLCPCB 実装 | 一致・注意あり<br>パッド番号が実部品と逆順（元設計どおり）。注意点 5 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_HRS-Hirose-FH12-22S-0-5SH-55_C597981.pdf) [LCSC](https://www.lcsc.com/product-detail/ffc-fpc-flat-flexible-connector-assemblies_hrs-hirose-fh12-22s-0-5sh-55_C597981.html) |
| SW1<br>タクトスイッチ | ALPS SKRTLBE010<br>同一 | `SKRTLBE010`<br>ALPSALPINE · `C127481` · 在庫 2,106 | JLCPCB 実装 | 一致<br>端子①③（共通）= GND、②（スイッチ側）= SW1 信号 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_1809041613_ALPSALPINE-SKRTLBE010_C127481.pdf) [LCSC](https://www.lcsc.com/product-detail/tactile-switches_alpsalpine-skrtlbe010_C127481.html) |
| GND（部品名）<br>表示 LED | 0603 チップ LED（色指定なし）<br>代替 | `KT-0603R`<br>Hubei KENTO Elec · `C2286` · 在庫 7,890,022 | JLCPCB 実装 | 一致<br>赤を選定。記号 A → JLC 1番（アノード）、C → 2番（カソード） | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_1810231112_Hubei-KENTO-Elec-KT-0603R_C2286.pdf) [LCSC](https://www.lcsc.com/product-detail/led-indication-discrete_hubei-kento-elec-kt-0603r_C2286.html) |
| R1, R2<br>10kΩ | 0603 10kΩ<br>同一 | `0603WAF1002T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C25804` · 在庫 32,676,170 | JLCPCB 実装 | 一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0603WAF1002T5E_C25804.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf1002t5e_C25804.html) |
| R3<br>1kΩ | 0603 1kΩ<br>同一 | `0603WAF1001T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C21190` · 在庫 24,612,269 | JLCPCB 実装 | 一致 | [データシート](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010130_UNI-ROYAL-Uniroyal-Elec-0603WAF1001T5E_C21190.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf1001t5e_C21190.html) |

## 手はんだで付ける部品（別途購入）

この7個は JLCPCB の BOM・CPL から外してあり、基板にはパッドと穴だけが用意されます。同じ型番を LCSC などで購入してください。

- `RK10J12E002L` × 1<br>VR1 — 音量ボリューム（2連） · [C231765](https://www.lcsc.com/product-detail/potentiometers-variable-resistors_alpsalpine-rk10j12e002l_C231765.html)
- `SKHHLQA010` × 3<br>SW_SUB, SW_UP, SW_DOWN — サイドプッシュスイッチ · [C125034](https://www.lcsc.com/product-detail/tactile-switches_alpsalpine-skhhlqa010_C125034.html)
- `DTS-63K-V` × 1<br>SW_MAIN — メインスイッチ（裏面） · [C141874](https://www.lcsc.com/product-detail/tactile-switches_diptronics-dts-63k-v_C141874.html)
- `B2B-XH-A(LF)(SN)` × 2<br>SPK, 5V — 2ピンコネクタ（縦型） · [C158012](https://lcsc.com/product-detail/wire-to-board-connector_jst-b2b-xh-a-lf-sn_C158012.html)

## 注意点

1. **CN1 ヘッドホンジャック**：回路図の記号（5ピン）は元のまま変えておらず、実部品の端子への割当だけを変えています。

   | 回路図のピン | つながる回路 | 元 Switchcraft | 今回 CUI SJ-43516 | 動作 |
   |---|---|---|---|---|
   | `P$3` | 左ch（VR1-A 経由） | 3 Tip | #2 Tip | プラグ先端に接触 |
   | `P$2` | 右ch（VR1-B 経由） | 2 Ring | #3 Ring1 | プラグのリングに接触 |
   | `P$1` | AGND | 1 Sleeve | #1 Sleeve ＋ #4 Ring2 | ステレオプラグのスリーブが両方に触れる |
   | `P$5` | スピーカーアンプへ（R4） | 5 Tip SW（常時閉） | #5 Tip SW（常時閉） | 未挿入で Tip とつながり、挿すと開く |
   | `P$4` | スピーカーアンプへ（R3） | 4 Ring SW（常時閉） | #6 Ring SW（常時閉） | 未挿入で Ring とつながり、挿すと開く |

   元は3極（TRS）用、代替品は4極（TRRS）用です。

   - 対応付け：元のピン（P\$1 スリーブ / P\$2 リング / P\$3 チップ / P\$4 リングSW / P\$5 チップSW）を、代替品の `#1 / #3 / #2 / #6 / #5` にそれぞれ割り当てています。
   - Ring2（#4）はスリーブと同じ AGND につないでいるので、普通のステレオプラグが元と同じように使えます。
   - チップSW・リングSWは、どちらもプラグを挿すと開く「常時閉」タイプで、元と同じ動作です。

2. **VR1 ボリューム**：

   - 端子の並びは一致しています。データシートの並びは左から「1 共通 / ② R1ワイパー / 2 R2ワイパー / 3 R2端 / ③ R1端」で、Eagle の `1AB / 2B / 2A / 3A / 3B` にあたります。
   - 抵抗カーブは「3B」（B = 直線型）です。音量調整には一般に A カーブ（対数型）を使います。元の部品が A カーブだった場合は、音量の変わり方が変わります。

3. **U\$3 RGB LED**：色の並びが元と違うため、回路図の色の割当を入れ替えました。40ピンヘッダの割当は次のとおりで、ソフト側の変更が必要です。

   - 19番（GPIO10）→ **青**
   - 21番（GPIO9）→ **赤**
   - 23番（GPIO11）→ **緑**

4. **SW_SUB / UP / DOWN**：元の型番が分からないため、ボタン長さ 8.35mm の SKHHLQA010 を選びました。フットプリントは共通なので、手はんだの際に SKHHLMA010（3.85mm）や SKHHLUA010（5.85mm）に変えても構いません。

5. **カメラ基板 CN2**：Eagle のパッド番号は、実部品のピン番号と逆順になっています（パッド「1」の位置に実部品の22番ピンが来る）。これは元の設計（ファイル名の「reverse」）からのもので、今回は変更していません。部品はパッドの形どおりに載るので、元の基板と同じ実装になります。

6. **元の Kingbright 製 RGB LED** のデータシートは、公式サイトの URL が見つからなかったため掲載していません。

出典：各メーカーのデータシート、LCSC / JLCPCB の部品データ（EasyEDA のフットプリント・記号）。照合した Eagle データ：`2019-06-27_OG19AWv2_JLC`、`2019-05-28_OG19_PC-3_reverse_JLC`。
