# 2026-09-13 剩餘三筆事件：唯讀解析／寫入分層與處理提案

本文件只整理以下三個 exact event，沒有修改 `D:\MISS` 的 production、candidate、test、SQLite、GS 或其他業務資料，也沒有重跑外部 OCR、網站或 GS：

- `631464422124028109`
- `631354634019537033`
- `631458503575732582`

結論分成「目前可驗證的錯層」、「尚缺的證據」與「需核准的最小方案」。舊附件的 `PY`／目前分頁內容不是這三筆的 immutable first snapshot；不能把附件所見的後續值冒稱成第一次解析或最後正確值。

## 調查邊界與 current base

- Formal root：`D:\MISS`，本次檢查時 `HEAD=d983b90`；相關 `miss_event_service.py`、`miss_middle_parser.py`、`miss_sheet_writer.py`、`ypm_ocr_server.py`、`miss_settlement_buffer.py` 沒有本次重疊 dirty。
- SQLite 僅以 `mode=ro`、`PRAGMA query_only=ON`、`PRAGMA quick_check` 讀取 `D:\MISS\miss_state.sqlite3` 的 `events` schema 與三個 exact `event_id`；`quick_check=ok`。沒有 dump 全庫。
- 原圖僅以 `view_image` 讀取 `D:\MISS\image_archive\631464422124028109.jpg`；沒有重跑外部 OCR。
- 既有 focused offline tests（未新增或修改）結果：

  ```text
  python -B -m unittest test_miss_parser_ocr_customer_cases_20260908.py test_miss_middle_parser_vertical.py test_p0_xiaoxin_write_recovery.py
  Ran 14 tests in 0.091s
  OK
  ```

  這只代表 current source 的 `OFFLINE_PASS`，不代表三筆歷史事件已恢復，也不代表正式環境或歷史 GS 已驗收。

## 總結表

| event | current 第一個可驗證層 | current 是否仍成立 | 最小處理方向 |
|---|---|---|---|
| `631464422124028109` | 原圖與保存解析的第二筆金額不一致；第一個可驗證差異在原圖→保存解析，該區間內仍缺 OCR 原文／中間輸入 | 原圖→保存解析差異成立；保存解析→最後分頁的 GS／人工狀態另屬 UNKNOWN，不能回推為保存解析原因 | 先找 OCR 原輸出與現有保存失敗點；不做 `80→50` 全域替換。完整同圖 transcription 確認後，exact-SHA 只可作單圖訂正選項 |
| `631354634019537033` | 文字非注單判別／注單候選 admission；日期中的 `8/24-8/29` 通過 generic number gate 後進入中球 parser | current 純函式可重現 | 在 `_process_text` 注單候選門檻前加窄的「查帳日期範圍」排除；不改號碼 parser |
| `631458503575732582` | current parser 的 actionable row 正確；「找不到同 ID」的第一錯層仍是 GS append／readback／後續清理的歷史證據缺口 | current source 已有小新 K 欄 event identity contract；歷史實際 cell 仍未知 | 保留 parser 與 K identity contract；只取得 exact historical append/readback 證據後再決定是否需要 writer/清理層修正 |

## `631464422124028109`：YPM 圖片第二筆二星 50/20 與保存 80/20 不一致

### 原始證據與保存解析

舊附件 `D:\AI Agent\MISS\reports\mxiaofu\2026-09-12_plain_language.md:33-40,705-710` 保存的原始事件只有 `[圖片事件]`，並記錄四個保存解析列：

1. `selection=07,08,09+-2+-4`，二星 `70`，三星 `10`。
2. `selection=07+32+11,13+26,36`，二星 `80`，三星 `20`。
3. 二／三／四星皆 `10`。
4. 二／三／四星皆 `10`。

本地 exact event row（`miss_state.sqlite3.events`）也保存：

- `event_type=image`、`target_sheet=YPM`、`target_row_start=29`、`target_row_end=32`。
- `parse_status=人工檢查`、`manual_status=待人工確認`。
- `parse_result_json.imageArchivePath=D:\\MISS\\image_archive\\631464422124028109.jpg`。
- `imageSha256=40ee5ca2fc5d2c44845cc5b43f8d61ba2b7791bc7675e0ce5ae5b7827c49e361`。
- 本地 JSON 有 `gsWrittenRange=YPM!29:32` 與幾個 verification flag，但沒有 actual cell values 或 actual readback body。

我用 `view_image` 看保存原圖。可辨認的右側金額如下：

- 第一筆：`2-70元`、`3-10元`。這與保存解析 `70/10` 相符；附件所說的第一筆 `20` 不能覆蓋原圖可見的 `70`，也不能把它當成第一筆 OCR 錯。
- 第二筆：`2-50元`、`3-20元`。這與保存解析的 `star2=80`、`star3=20` 只有二星金額不同，形成可重現的原圖／保存解析差異。

`D:\MISS\logs\ypm_ocr_server.log:20964-20965` 只證明當時有一個 Gemini `ReadTimeout` 警告，之後記錄「圖片 OCR 完成、筆數=4」；沒有保存四列 OCR 原文。`editor_revisions` 對此 exact ID 也沒有列。

舊附件提到 YPM 分頁的 `20/50` 是報告當時觀察，不是不可變的 historical cell snapshot。這次沒有讀新的外部 GS，因此不能拿它反推第一筆應該是 `20`，也不能以它排除後續人工修改。

### 第一個可驗證錯層與剩餘缺口

目前能說到的最窄結論是：

> 第二筆原圖可見 `2-50元、3-20元`，保存解析為 `star2=80、star3=20`；第一個可驗證差異位於「原圖到保存解析」之間。因為 OCR 原始回傳與送入 parser 的中間資料未保存，目前只能把 OCR／後段 parser 留作 UNKNOWN，不能再細分其中哪一層先錯。保存解析到最後分頁之間的 GS 實際 cell 與後續人工修改也沒有不可變證據；沒有證據顯示它們會回灌 `parse_result`，所以另列為保存解析→最後分頁的獨立歷史缺口，不混入本段根因。

目前不能用 `gsContentVerified=true`、`gsRangeVerified=true`、`gsWriteVerified=true`、`YPM!29:32` 其中任何一項排除保存解析→最後分頁之間的 GS 實際內容錯誤或後續人工修改；這些只是本地保存的回執旗標／範圍宣告，不包含被比較的金額。它們也不能補回原圖到保存解析之間遺失的 OCR 輸出。

已檢查 current code：

- `D:\MISS\ypm_ocr_server.py:_miss_image_ocr_handler`（約 3175）會先查 exact-image accepted truth，否則進 `image_ocr_with_routing`。
- `D:\MISS\ypm_ocr_server.py:_load_corrected_ocr_examples`／`_corrected_ocr_example_result`（約 3084／3167）有精確 SHA 對照機制；上述 target SHA 不在目前 `D:\MISS\ypm_examples\accepted_ocr_truth.json`。
- `D:\MISS\miss_event_service.py:_process_image`（約 5156）會把 OCR 組成 `ocrText` 後交給 `parse_ocr_strings`，但這筆歷史 SQLite payload 沒有 `ocrText`。
- `D:\MISS\miss_middle_parser.py:parse_ocr_strings`（約 3422）及 `parse_middle_text`（約 2922）沒有針對此 event 或 `80→50` 的特例。沒有查到 current 已針對本圖加過修正；也沒有重跑 OCR 來冒充 current replay。

因此本案不是「可直接 patch parser」；目前先要補的是原圖到保存解析之間的 exact 保存證據，另有保存解析到最後分頁的歷史證據缺口：

1. 優先：該 event 當時交給 parser 的 OCR line array／prewrite transcript，以及確認現有保存機制為何沒有留下它。
2. 分開處理：該 event 在 `YPM!29:32` 的 immutable append response／actual readback cells，以及可辨識後續人工修改的 revision；這只能定位保存解析→最後分頁，不能代替第 1 項。

`miss_event_service.py` 的 receipt projection 目前只保留 `eventId`、range、row count、verification flags 與 redacted diagnostics，故本地 SQLite 找不到上述實際 cell body。這是保存欄位缺口，不是可以猜根因的理由。

### 最小可審處理方案（尚未套用）

1. **不做全域金額替換。** 不把 `80` 一律改成 `50`，也不照舊附件的 `20/50` 反推第一筆；這會把原圖第一筆已看清的 `70/10` 改壞。
2. 若完整 canonical transcription（不只金額，也確認選號格式）已被確認，可在候選中用現有 exact-SHA truth 入口新增此圖片 digest 的完整 `answer_lines`，由 `_corrected_ocr_example_result` 只命中同一張、同一組 bytes 的圖片。這只是可選的單圖訂正，不是本案主要根因修復；不會改善未來相似的手寫 `50/80`，也不是通用 parser 訓練或規則修正。不改 `parse_middle_text` 的一般金額規則，不影響其他 50、70、80 的正常下注。
3. 若目前只確認「第二筆二星是 50、三星是 20」而未有四筆完整 OCR 行，先保持人工檢查，不新增不完整 truth row；下一個取證動作是先找回完整 OCR line array／prewrite artifact，再決定是否建立 exact-SHA truth。
4. 若要改善未來可鑑識性，先另行評估最小保存變更：只在 parser 邊界保存 event-scoped `ocrText`／OCR line array，並確認現有保存失敗機制。不要把 GS actual readback/value digest 一併擴大成同一個未核准修改；GS／人工證據仍是另一個歷史分層缺口。

### 正常功能不變項與驗收設計

- 第一筆 `70/10` 應維持；合法的 `50`、`70`、`80` 及其他金額不可被全域轉換。
- 選號、尾數／柱位、二／三／四星欄位及人工 gate 不因本案臨時修正而改變。
- 離線驗收（僅適用於日後核准的單圖訂正）：以同一組 target image bytes 的 exact SHA 命中候選 truth，解析四筆完整 canonical lines，確認第二筆為 `50/20`、第一筆仍為 `70/10`，其餘已確認列不被重排；不同 SHA、包括未來相似手寫圖片，不受影響。這不代表通用解析已修復。
- 實戰／正式驗收（本輪未做）：只能用該 event 的 immutable OCR／append/readback evidence 對照，不能用現行 GS 的單次畫面取代歷史證據；若要重新處理或改寫歷史列，需另得明確授權。

## `631354634019537033`：查 8/24–8/29 總帳被保留成選號候選

### 原文、保存解析與 current 重現

舊附件 `D:\AI Agent\MISS\reports\mxiaofu\2026-09-12_plain_language.md:51-58,194-199` 的原文是：

```text
@阿福 抱歉如果還沒睡可以幫我調閱一下子 8/24-8/29的帳目(總帳)嗎?
```

這是查帳請求，不是下注。exact SQLite row 保存：

- `event_type=text`、`target_sheet=記錄`、`target_row_start=5`、`target_row_end=5`。
- `mode=中球文字`、`manual=true`。
- `middleParse`／`recordParse` 都是 `08,24,29`，玩法、星數、全車、支數均空白。
- route 為非正式／資料不足，但本地事件仍記錄 `gs_write_status=written` 與 `記錄!5` 的寫入旗標。

我以 current source 的純函式確認：

- `_is_non_bet_report_text(raw)` 為 `False`；它只辨認既有固定報帳／開獎損益格式。
- `_is_selection_price_comment(raw)` 為 `False`；現有 account settlement 只涵蓋「前帳」等其他句型，沒有這個查總帳請求。
- `has_at_least_two_valid_ticket_numbers(raw)` 為 `True`，所以日期中的 8、24、29 通過文字事件的候選門檻。
- `parse_middle_text(raw, allow_selection_only=False)` current 輸出 `selection=08.24.29`、`manual=True`、原因為只有號碼缺少星數／全車。這正是此事件保存的候選形態。

因此本案第一個可驗證錯層是 **文字非注單 gate／候選 admission**，不是 `08` 的補零或 `parse_middle_text` 的號碼格式本身。舊附件目前 GS 找不到同 ID 不能被用來證明當時沒有寫入；它只與本地保存的「曾嘗試／宣告寫入」形成另一個需分開處理的歷史 readback 問題。這筆即使有記錄列，也不能算成漏下注。

### current 是否已有修正

current `D:\MISS\miss_event_service.py` 仍是：

1. `_process_text`（約 4397）先走固定 non-bet／聊天評論 gate。
2. 通過後以 `has_at_least_two_valid_ticket_numbers`（約 4436）作注單候選門檻。
3. 其他群組／記錄的中球文字再落到約 4789 的 `parse_middle_text(... allow_selection_only=False)`。

目前沒有「查閱／調閱 + 帳目／總帳 + 日期範圍」的窄分支；current 純函式重現代表本案尚未修好。這是新邏輯提案，尚未改 source 或 test。

### 最小可審處理方案（需使用者先同意）

在 `D:\MISS\miss_event_service.py` 的 `_process_text` 候選門檻前新增一個窄 helper，例如 `_is_non_bet_account_lookup`，條件同時要求：

- 有 `調閱`／`查閱`／`查一下`／`查帳` 等查閱動詞；
- 有 `帳目` 或 `總帳`；
- 有日期範圍 `\d{1,2}/\d{1,2}-\d{1,2}/\d{1,2}`（允許空白與全形連字號）；
- 沒有 `二／三／四星`、`車／全車／專車`、`尾`、`不中`、`X/*× 支數／金額`、`各 N 元` 等下注玩法標記。

在現有 `_is_selection_price_comment` 之後、`has_at_least_two_valid_ticket_numbers` 之前，對符合者直接回傳：

```text
status=ignored
rows=0
manual=False
acceptance_status=不需下注
reason=查帳／總帳請求，不是下注訊息
```

這個位置只改非注單分類，不改 parser；也不把所有含日期或所有「帳」字的文字一律忽略。不要把現行函式的聊天評論 reason 直接套在查帳，避免日後 audit 誤解。

### 正常功能不變項與驗收設計

- `539、10、33、車、各5元` 等含玩法／金額的真下注不符合「無玩法標記」條件，仍進正常 parser；這個候選 branch 不會修正或吞掉第二案。
- `08,24,29 二星5`、`8/24-8/29 各5元` 等含下注動作或金額的訊息不應被查帳 branch 忽略。
- 既有五行以上帳目清單、固定報帳／開獎損益格式及正常日期型注單保持原行為。
- 離線驗收：exact raw 產生 `ignored/rows=0` 且 fake worksheet 沒有 append；上述真下注與含玩法負例仍產生原本的候選／解析結果。應以既有 `python -m unittest` 方式在候選中新增 focused case；本輪未新增測試。
- 實戰驗收（本輪未做）：只能在使用者核准後用新事件觀察「查帳不新增下注列、真下注仍新增」，不回寫或補送本歷史 event。

## `631458503575732582`：小新文字解析存在，但舊報告找不到同 ID

### 原文、保存解析與 current 純解析

舊附件 `D:\AI Agent\MISS\reports\mxiaofu\2026-09-12_plain_language.md:60-65,449-454` 的原文是：

```text
今彩
06.11.25.31二三四星0.5
```

exact SQLite row 保存：

- `event_type=text`、`target_sheet=小新`、`target_row_start=46`、`target_row_end=46`。
- `middleParse` 為 `06,11,25,31`、二星 `0.5`、三星 `0.5`、四星 `0.5`。
- `gsWrittenRange=小新!46:46`、`gsActualUpdatedRange=A46:K46`，並保存 `gsIdentityContract=xiaoxin_event_id_k_v1`；這些是本地 event result 的宣告欄位，不能代替 actual K cell readback。
- `editor_revisions` 對此 exact ID 無列。

current 純函式結果如下：

- `infer_xiaoxin_lottery` 判定 `lottery=539`、source=`文字`。
- `parse_middle_text(... allow_selection_only=True)` 會先把單獨的 `今彩` 留成一個人工 placeholder，再產生 actionable row `06.11.25.31` + 二／三／四星皆 `0.5`。
- EventService 使用 `_usable_middle_bets` 後只保留 actionable row；因此這個 header placeholder 不會造成第二列空下注。

這代表 current parser 對實際下注內容沒有再現缺號或星額錯位。`今彩` 導致整體人工旗標是保守的人工檢查訊號，不是本案的缺列根因。

### current writer／identity 狀態與 first wrong layer

current source 已有小新 event identity contract：

- `D:\MISS\miss_sheet_writer.py:XIAOXIN_HEADERS`（約 45）含第 11 欄 `event_id`。
- `build_xiaoxin_updates`（約 261）把 `event_id` 放入每一列，並以 `verify_event_id_column=11`（約 318）要求 append receipt 驗證 K 欄。
- `D:\MISS\miss_settlement_buffer.py` 有 `XIAOXIN_GS_IDENTITY_CONTRACT = "xiaoxin_event_id_k_v1"`（約 42）及對應 prewrite／recovery contract。
- current focused p0 recovery tests 包含小新 K 欄 identity、缺 receipt fail-closed、舊 contract 不自動 replay，均已在上面的 14 tests 通過。

所以目前可排除「current parser 沒有 event identity 設計」；但不能從 source 或 SQLite 的 boolean receipt 推回 9/12 `小新!K46` 實際值。舊報告所說的「目前找不到同一 event_id」第一個未定位層仍可能是 append 實際內容、讀回／快取、後續清理或查看時間點；現有資料不能在這些層之間選一個。

### 最小可審處理方案與驗收

1. 不修改 `parse_middle_text`、`_usable_middle_bets`、小新欄位或 K identity contract；目前沒有 parser candidate 可合理提出。
2. 下一個必要取證動作是只找 event `631458503575732582` 的 immutable append/readback artifact：`小新!A46:K46` 的 actual row body、K 欄 exact event ID、response/readback range、或 event-owned receipt。不得用現在 GS 的「找得到／找不到」取代 9/12 時點證據。
3. 若該 artifact 證明 K 欄當時就是 exact ID，這案屬附件查看／後續清理／歷史 readback gap，不需 parser 修正。
4. 若 artifact 證明 append body 缺 K 或 K 不一致，才另提 writer／settlement candidate；不能在沒有 body evidence 時重送或補寫。

離線驗收已完成：parser actionable row、`build_xiaoxin_updates` 第 11 欄 exact event ID、recovery fail-closed tests 通過。正式／實戰驗收仍需 historical or fresh controlled append receipt + actual K readback，且本輪未做外部 GS、重送、部署或 runtime action。

## 不改事項、外部證據與使用者決定

本輪沒有：

- 修改 `D:\MISS` production／candidate／test／正解或任何業務資料；
- 修改既有 `D:\AI Agent\MISS\reports\mxiaofu\2026-09-13_parser_solution_proposal.md`；
- 寫 GS／SQLite、清理或補寫歷史列；
- 重跑外部 OCR、重新送出、下注、restart、deploy、commit 或 push。

需要主管整合的具體下一步證據：

1. `631464422124028109`：先找本地保存的原始 OCR line array／prewrite transcript，並查明現有 OCR 保存失敗機制；另分開找 event-owned `YPM!29:32` actual append/readback values 及後續 editor/revision receipt。
2. `631458503575732582`：本地保存的 `小新!A46:K46` actual row／K identity readback 或 immutable append receipt。
3. `631354634019537033` 不需要外部 GS 才能提出 gate；本輪已足以證明 current candidate admission 仍重現，但新增 branch 必須先取得使用者對行為改變的同意。

仍需使用者決定的業務事項：

- 是否正式把「含日期範圍、查閱／帳目語意且沒有下注玩法」列為不需下注；這是本輪唯一提出的 parser-adjacent 邏輯變更，尚未套用。
- 在完整四列 OCR canonical lines 找回並核對後，是否採用同一組 bytes 的 exact-image truth 作單圖訂正；目前不能自行補寫不完整答案列，也不把它當成通用 parser 修復。
- 若歷史 append/readback artifact 證實保存解析→最後分頁確有缺失，是否另開 writer／清理層提案；本輪不以 current GS 狀態作恢復依據。

本文件的可用狀態是 `OFFLINE_PASS + PROPOSAL_ONLY`；三筆均未 `DEPLOYED`、`RUNTIME_LOADED` 或 `LIVE_ACCEPTANCE_PASS`。
