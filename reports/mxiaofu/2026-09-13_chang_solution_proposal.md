# 2026-09-13 常勝軍開獎圖無回應：唯讀查證與最小候選方案

查核性質：`READ_ONLY_PROPOSAL`。本次沒有改程式、config、candidate、test 或正解，沒有寫業務 GS/DB，沒有重送、下注、deploy、restart、啟動 W 或外部發訊。唯一新增檔案是本報告。

查核範圍是常勝軍圖片從 ORDER 收件到 MISS B12 的實際邊界；ORDER 其他 dead/crash 問題不在本次範圍。以下把 9/11 歷史個案與 9/13 現行測試事件分開。

## 現行基線與保護範圍

- `D:\MISS`：branch `checkpoint/miss-pre-p0-fixes-complete-20260911`，HEAD `29adcb5aa9a4ba657798d0ee6005f29f445e5cb1`。既有 dirty 是 `config/window_layout.json`、`miss_accounting_delivery.py`、`miss_accounting_runtime.py` 及 `.worktrees/`；本次沒有覆寫。兩個 dirty Python 檔的 `CHANG_TG_CHAT_ID` 都已由舊正式群 `-1003804335513` 改為測試群 `-1004415191836`，這是現況，不是本次修改，也沒有把它當成已部署或已載入。
- `D:\MISS_ORDER`：branch `feature/miss-order-gs-publication`，HEAD `641933e`；既有 dirty 檔案保留。本次沒有重做 exact ID、ORDER bridge 或 dual poller。
- `D:\AI Agent\MISS`：branch `main`，HEAD `59d9d7e`；既有報告與 dirty 檔案保留。
- 讀到常駐 process 只能證明當時有 process，不能證明 resident runtime 已載入目前磁碟 source；本次沒有 reload 或重啟，因此 `RUNTIME_LOADED` 仍未由本查核建立。

## 歷史個案（不可倒填成現況）

9/11 常勝軍 message `99`、chat `-1003804335513`、sender `8817839914` 的 photo payload 在 `D:\MISS_ORDER\data\miss_order.sqlite3` 的 `tg_inbox`，狀態是 `processed`。既有個案文件 `D:\AI Agent\MISS\MXIAOFU_CASE_20260911_CHANG_TG99.md:19-39` 與 `reports\mxiaofu\2026-09-12_full_report.md:93-96,114-122` 都指出：當時有 ORDER 收件證據，但沒有同一 message 的 MISS event、B12 progress 或 archive；因此 ORDER `processed` 不能證明交給 MISS，也不能把缺段直接寫成收訊、Bot 或 OCR 根因。這筆歷史事件仍是 `ORDER_RECEIVED` 後段 `UNKNOWN`，不以 9/13 測試結果補填。

已由其他 Agent/既有 commit 處理的內容，現況可見但不能因此宣稱正式完成：

- `D:\MISS` ancestry 含 `4d6b54c fix(tg): prevent shared-token dual polling`，`merge-base --is-ancestor` 成立；source 註解已把 polling ownership 分開。本次不重做 dual poller。
- `D:\MISS_ORDER` HEAD `641933e fix(order): require explicit B12 handoff receipt`，其 ancestry 含 `8165716 fix(order): bridge B12 callbacks to MISS`、`a955f81 fix(tg): forward Chang photos to MISS`。`miss_order\app.py:244-282` 的 exact Chang photo bridge 使用 `occurred_at.isoformat()`；既有 `test_miss_order_chang_photo_bridge.py:151-170` 也固定檢查 `2026-09-12T20:34:00+08:00`。這條 ORDER bridge 已有 full ISO 證據，沒有必要把本次第一候選放在 ORDER。
- `D:\MISS` ancestry 含 `05e2be9 fix(tg): preserve Chang webhook event identity`、`8818deb`、`e3c2fbf`、`29adcb5`；現行 source 能建立 canonical `tg_m<chat>_<message_id>` 並寫 B12 progress。這些是 source/離線證據，不是本次查核重新部署或 runtime 載入證據。

## 9/13 現行事件實際走到哪裡

兩筆 exact 測試事件是 `tg_m1004415191836_6` 與 `tg_m1004415191836_7`，群組 `-1004415191836`、使用者 `8817839914`。兩張 archive 圖片確實存在：

- `D:\MISS\image_archive\tg_m1004415191836_6.jpg`，88,384 bytes。
- `D:\MISS\image_archive\tg_m1004415191836_7.jpg`，89,115 bytes。

ORDER SQLite（URI `mode=ro`、`PRAGMA query_only=ON`、`quick_check=ok`）查到：

| message | `tg_inbox.id` | update | status | attempts | received / processed | photo |
|---|---:|---:|---|---:|---|---:|
| `6` | `1115` | `349907651` | `processed` | `2` | `2026-09-12T21:14:08.597801+00:00` / `2026-09-12T21:14:38.258481+00:00` | 4 張，最大 88,384 bytes |
| `7` | `1116` | `349907652` | `processed` | `0` | `2026-09-12T22:47:53.329587+00:00` / `2026-09-12T22:47:53.337015+00:00` | 4 張，最大 89,115 bytes |

MISS `miss_state.sqlite3` 也以 read-only/query-only 查詢，`quick_check=ok`。兩筆 row 都已保存 exact identity，但 `event_time` 是缺年份的 `09/13 05:14`、`09/13 06:47`，`parse_status`、`lottery_source` 為空，`gs_write_status=pending`：

| event | source / identity | event_time | updated_at | GS state |
|---|---|---|---|---|
| `tg_m1004415191836_6` | `Telegram`; `TGCHAT:-1004415191836`; `TGUSER:8817839914` | `09/13 05:14` | `2026-09-12T21:14:10+00:00` | `pending` |
| `tg_m1004415191836_7` | `Telegram`; `TGCHAT:-1004415191836`; `TGUSER:8817839914` | `09/13 06:47` | `2026-09-12T22:47:54+00:00` | `pending` |

`D:\MISS\logs\b12_draw_progress.log:105-113` 與 `D:\MISS\logs\ypm_ocr_server.log:21076-21088` 對兩筆事件都有同樣邊界：

1. `MISS_RECEIVED` 已出現。
2. `route=chang_draw`, `lottery=539` 的 archive `START`、`OK` 已出現。
3. 隨後立即是 `terminal status=BLOCKED reason_code=REPORT_DATE_REQUIRED`。
4. 沒有同一 event 的 OCR、GS write、GS readback、render 或 Telegram send phase。

因此現在能確認的層次是：

`ORDER tg_inbox received/processed` → `MISS_RECEIVED` → `exact Chang route` → `image archive START/OK` → **日期 authority gate BLOCKED**。

OCR、GS write/readback、產圖與送達不是「失敗已證明」，而是尚未到達，或在本次證據中沒有出現，應保留 `NOT_REACHED/UNKNOWN`。`processed`、archive `OK`、health 或 READY 都不代表整條鏈成功。

## 第一個錯誤層與可重現證據

現行 source 的因果順序是可核對的：

- `D:\MISS\miss_tg_intake.py:245-255` 的 `_message_timestamp()` 對 Telegram `datetime` 先轉台北時間，卻在 `:252` 用 `strftime("%m/%d %H:%M")` 丟掉年份與 timezone；`intake_probe_handler()` 在 `:564-572` 把同一值放進 text/photo 共用 payload 的 `timestamp`。
- `D:\MISS\ypm_ocr_server.py:4157-4164` 讀入這個 timestamp，`:4221-4243` 直接把它放成 event 的 `source_event_timestamp`。
- `D:\MISS\miss_accounting_runtime.py:631-647` 的 `derive_event_report_date()` 對 `source_event_timestamp` 只接受可解析的 ISO datetime；沒有 explicit `report_date/accounting_date/date` 或 ISO timestamp 就 `REPORT_DATE_REQUIRED`。
- `D:\MISS\miss_accounting_runtime.py:4022-4035` 的 `_process_chang_image()` 在任何 `download`/OCR observe 前呼叫這個 resolver，因此此 gate 是當前第一個錯誤層。

本次未改檔的離線探針直接重現：

```text
_message_timestamp(datetime(2026-09-13 05:14:06+08:00))
    -> '09/13 05:14'
derive_event_report_date({'source_event_timestamp': '09/13 05:14'}, lottery='539')
    -> RuntimeBlocked: REPORT_DATE_REQUIRED
derive_event_report_date({'source_event_timestamp': '2026-09-13T05:14:06+08:00'}, lottery='539')
    -> 2026-09-13
```

這把「缺年份的來源 timestamp」與現行 resolver 的 fail-closed 行為直接接起來。它沒有證明圖片內容的開獎日就是 9/13，也沒有證明此前 9/11 message 99 的原因相同。

證據強度要分開：第一個錯誤層 `REPORT_DATE_REQUIRED` 已由兩筆 current event 的 terminal log 和函式探針確認；`miss_tg_intake._message_timestamp()` 是能產生同樣短值、且與 current `miss_state.event_time` 完全相符的現行入口機制。可是 current log 沒有保存 ingress process/原始 HTTP payload，因此不能把 `_6/_7` 的實際送入者硬寫成 direct intake；也可能是另一入口或中間轉換把 timestamp 截短。ORDER bridge source 本身已有 ISO 證據，故 direct intake 是最小候選目標，但 `exact_ingress_owner` 在下一次自然事件取得 raw payload 前仍標 `UNPROVEN`。

## 為什麼不能直接改共用 helper

`_message_timestamp()` 的輸出不是只給 Chang B12：

- `miss_settlement_buffer.submit_telegram()` 以傳入 timestamp 保存 Telegram `event_time`（`D:\MISS\miss_settlement_buffer.py:1062-1109`）。
- `miss_event_service._append_raw_event()` 同時把它寫成 `line_timestamp`、`gas_timestamp` 及 event ledger `event_time`（`D:\MISS\miss_event_service.py:2921-2960`）。
- recovery deadline 明確只接受 `MM/DD HH:MM`（`D:\MISS\miss_settlement_buffer.py:118-132`），文字／非命中時間 parser 也只抓 `M/d HH:mm`（`D:\MISS\miss_event_service.py:1318-1342`）。
- 成功通知的人話顯示會直接插入傳入值（`D:\MISS\ypm_ocr_server.py:713-735,897-901`）。

所以「把 `_message_timestamp` 全域改成 ISO」會同時改變 text/photo legacy event_time、recovery 入窗與人話顯示；這些影響尚未被允許或驗證。這也是本報告不提全域 helper 替換的理由。

## 需使用者核准的最小候選

候選名稱：`CHANG_PHOTO_MACHINE_DATE_FIELD`。目前只提出，不建立 candidate、不改 Formal、不 reload。

### 修改前

直接 MISS intake 的 photo payload 只有：

```text
timestamp = "09/13 05:14"
```

ypm 會將該值直接複製成 `source_event_timestamp`，B12 在 resolver 卡住。文字與圖片共用同一格式，legacy event_time/recovery 仍依賴短格式。

### 修改後（兩個 exact file/function）

1. `D:\MISS\miss_tg_intake.py` 的 `_photo_payload()`：保留原有 `timestamp` 不變，另加 `source_event_timestamp`；值取同一 `message.date` 的完整 ISO-8601（aware datetime 先轉台北、保留 offset；缺值不猜日期）。只在圖片 payload 增加此機器欄位，文字 payload contract 不變。
2. `D:\MISS\ypm_ocr_server.py` 的 `handle_tg_event()`：沿用既有 timestamp 驗證與保存；只有 `message_type=image` 且 chat/user 精確符合 Chang 時，若 payload 有 `source_event_timestamp`，將其作為 event 的 `source_event_timestamp`。既有 `timestamp`、`_miss_tg_timestamp`、archive event_time、傳給 legacy consumers 的 short timestamp 保留。欄位缺少時沿用原本的 `timestamp`（ORDER 既有 full ISO 仍可正常解析；direct intake 的短值仍會被日期 gate 擋下）；欄位若存在但不是可解析完整時間，則拒絕且不猜年份。

ORDER 的既有 full ISO `timestamp` 不需變更；它會走現有 fallback，避免再做一套 ID 或 poller 設定。`derive_event_report_date()`、`_process_chang_image()`、OCR、GS、render、send、回調及日期業務規則均不修改。

### 正常不變項與影響

- 不變：`event_id=tg_m<chat>_<message_id>`、exact chat/user、photo bytes/hash、archive 路徑、Chang route、legacy `timestamp`／event_time、文字入窗、recovery parser、TTL `handle_ttl_image_event(event, timestamp)` 舊路徑、ORDER bridge、dual poller、Sheets identity、金額/下注/通知 gate。
- 預期改善：直接 MISS intake 的 exact Chang photo 能提供一個可解析的來源事件日期，通過目前 `REPORT_DATE_REQUIRED` gate。
- 仍需驗證：`source_event_timestamp` 這個新欄位只應被 exact Chang B12 使用；其他 photo/文字 route 不得因欄位存在而改用新日期。若實作時無法把使用限制在 exact Chang，應停在 candidate review，不擴大成全站 timestamp migration。

選這個候選而不讓 resolver 自動從 `09/13` 猜年份，是因為 resolver 現在的 fail-closed 約束是正確的；日期權威應在 ingress 傳完整來源時間，不應由本機現在日期補猜。選新增 machine field 而不改 shared `timestamp`，是因為上節列出的文字顯示、入窗與 recovery contract 尚未允許變更。

## 核准後的離線驗證與停止條件

邏輯修改必須先核准；核准後仍只先做 candidate。驗收順序如下：

1. **RED 對照**：用 aware UTC `datetime` 及 Taipei `datetime` 探測現行 helper；確認 legacy photo `timestamp` 仍為 `MM/DD HH:MM`，現行沒有 machine field 時仍會 `REPORT_DATE_REQUIRED`。
2. **候選 GREEN**：用現有 intake/photo fixture 檢查 photo payload 同時有短 `timestamp` 與完整 ISO `source_event_timestamp`；text payload 沒有新欄位且原 timestamp/display/入窗輸入不變。
3. **窄路由**：用既有 webhook tests 檢查 exact Chang image 的 event source date 取 machine field；wrong chat/user、普通文字、非 Chang photo、TTL `handle_ttl_image_event` 與 ORDER 已有 ISO payload 保持舊路徑。缺欄位、非字串、控制字元、非 ISO 都不得猜年份或繞過 gate。
4. **既有 focused suites**（不以此宣稱正式完成）：`python -m unittest -v test_miss_tg_webhook.py`（目前 baseline 29 OK）、`python -m unittest -v test_b12_539_image_route.py test_b12_chang_telegram_image_route.py`（目前 baseline 24 OK）、`D:\MISS_ORDER` 的 `python -m unittest -v test_miss_order_chang_photo_bridge.py`（目前 baseline 10 OK）。候選若新增 regression，應放入既有相關 test file，不能藉 bypass 讓 baseline 綠。
5. 做 `py_compile`、`git diff --check`、窄範圍 secret scan，並重新確認 dirty overlap；不 stage 其他檔案、不覆寫目前 dirty。

任何 text payload 變成 ISO、recovery deadline 無法解析、wrong route 取 machine field、缺日期時變成猜年份，均停止，不進 Formal。

## 若獲得新的 live 授權，實測必須逐層留證

不能重送 `_6/_7`，也不能用舊 archive 回放冒充 live。若目前授權仍只有查證/提案，需由使用者提供一張新自然測試圖或給對應的 live 授權；若既有授權已明確涵蓋該 exact scope，不重複詢問。候選核准本身不連帶授權 deploy、reload、重送、GS/DB 寫入或外部發訊。取得對應授權後，該次要以同一 immutable event id 串起：

1. ORDER `tg_inbox` 的 raw identity、Telegram message date、photo bytes/size 與 bridge receipt。
2. MISS `MISS_RECEIVED`、exact route、archive path/sha256。
3. `report_date` 來源的完整 ISO，以及它與新圖明確可核對的開獎日期／caption／測試 fixture 一致；full ISO 成功只代表事件日期可解析，不代表圖片所屬開獎日已證明。
4. OCR `START`、輸入 image sha、同 event `ACCEPTED`、numbers/accepted proof。
5. GS write `START`、exact target sheet/range、`WRITTEN` 或 `IDEMPOTENT` receipt；再取得同 event 的 readback numbers/range proof。
6. render output path/sha 與送往 exact Chang destination 的 send receipt；若有 callback/button，另要有同 event callback receipt。

缺任一段、日期與圖片內容不一致、write/readback 只有 `READY` 沒 receipt、render/send 沒 exact receipt，就停在 `BLOCKED` 或 `UNKNOWN`。即使一筆自然新圖完整通過，也只能依序標 `OFFLINE_PASS`（若只是測試）、`DEPLOYED`、`RUNTIME_LOADED`、`LIVE_ACCEPTANCE_PASS`；沒有穩定觀察窗不能標 `PRODUCTION_STABLE`。

## 目前結論與下一個有界動作

目前可下的最小結論是：9/13 `_6/_7` 已到 MISS archive，第一個實際阻斷是 `REPORT_DATE_REQUIRED`；現行 direct MISS Telegram intake 的 datetime formatter 與 resolver contract 有可重現的不相容，但 `_6/_7` 是否確由這個 ingress 送入仍是 `UNPROVEN`，不能越過 raw payload 證據。已知 ORDER bridge、exact ID、dual poller 與 callback receipt 修正不需重做，也沒有證據支持先改 OCR、群 ID、GS writer 或 send。

本輪狀態仍是 `READ_ONLY_PROPOSAL`，不是 `CANDIDATE_READY`、`DEPLOYED`、`RUNTIME_LOADED` 或 `LIVE_ACCEPTANCE_PASS`。下一個具體決策只有兩種：

- 核准上面的兩檔窄候選，才製作 candidate 並按 RED→GREEN 驗證；或
- 暫不改邏輯時，取得一筆新自然測試圖的已遮罩 ingress payload（保留 chat/message/date/type，不含 token/secret），只核對 `source_event_timestamp` 是否由正確 ingress 產生；不以重送舊事件代替。

在上述決策前，本報告沒有任何正式修復或 live 成功宣稱。

## 07:25 版本更新（追加，不覆寫原提案）

### 來源與本輪 execution 事實

主管指出的 `d983b90bfff88197a758f886429d5b6ecb1abb21` 已在本輪查核前存在於 `D:\MISS` HEAD。唯讀 Git 證據如下：

- commit：`2026-09-13 07:25:21 +08:00`，author `ypttw`，message `fix(b12): derive 539 date from source message time`。
- parent：`29adcb5aa9a4ba657798d0ee6005f29f445e5cb1`；reflog 也有同一時間的 `commit` entry。
- files：`miss_accounting_runtime.py`、`miss_tg_intake.py`、`ypm_ocr_server.py`，新增 `test_b12_539_message_date.py`，更新 `test_miss_tg_intake_bot.py`。
- 本輪本 Agent 只執行 `git show/status/log/reflog`、source/log/DB read-only 查詢與 process snapshot；沒有寫上述程式、沒有執行測試、沒有 restart/reload/resend。唯一寫入仍是本報告檔。
- current source status 仍只見原有 `config/window_layout.json`、`miss_accounting_delivery.py`、`miss_accounting_runtime.py` dirty；`miss_tg_intake.py`、`ypm_ocr_server.py` 與新增 test 在 HEAD clean。`miss_accounting_runtime.py` 的 dirty 差異仍只有測試群 ID，與本 commit 的 resolver fallback 行不重疊。

### d983b90 已處理的內容

原提案中的 `CHANG_PHOTO_MACHINE_DATE_FIELD` 不應再重複改碼；以下部分已由此 commit 實作，狀態由「待修改」移到「待驗收」：

1. `D:\MISS\miss_tg_intake.py:259-272` 新增 `_message_source_event_timestamp()`，aware Telegram datetime 轉成台北時間的完整 ISO；`payload_common` 在 `:580-589` 同時保留原 `timestamp` 並加入 `source_event_timestamp`。
2. `D:\MISS\ypm_ocr_server.py:4165-4187` 重用既有 `is_exact_chang_tg_image` 判斷：exact Chang image 優先取 machine field，缺少時沿用原 `timestamp`；有來源時間時以 `route_timestamp` 傳入 B12，event 的 `source_event_timestamp` 在 `:4260` 保存。
3. `D:\MISS\miss_accounting_runtime.py:4031-4037` 對沒有 `source_event_timestamp` 的直接 runtime 呼叫，以傳入 `timestamp` 建立 dated event，再交給既有 `derive_event_report_date()`。這沒有把 resolver 改成猜年份。
4. 既有 ORDER bridge 的 full ISO `timestamp` 不需改；缺少新欄位時可沿用該 full ISO。若 direct intake 只有短 `timestamp`，仍會被既有日期 gate 擋下；若欄位存在但 malformed，仍不會猜年份。

此實作與原提案有兩個需要 review 的差異，不能默認「完全零影響」：

- 新欄位目前放在 text/photo 共用 `payload_common`，因此文字 payload 的 wire shape 也多了一欄；ypm 只在 exact Chang image 使用它，文字、非 Chang image 與 TTL 仍以原 `timestamp` 路徑處理。這是 source 行為已改變，需由既有 intake contract test 驗收。
- exact Chang image 會把 full ISO `route_timestamp` 傳給 `_b12_accounting_line_image_route()`，所以該 exact route 保存的 event ledger `event_time` 可能由短格式變為 ISO；這與原提案「legacy event_time 保持短格式」不同，不能在沒有實測 recovery/顯示消費者前宣稱不變。文字、TTL 與 ORDER 的既有路由沒有因本 commit 直接改用這個 route timestamp。

### 測試證據與其限制

`test_b12_539_message_date.py` 現在有 8 個日期/路由測試，包含：

- Telegram datetime → `source_event_timestamp` full ISO，並檢查 Chang runtime 能走到 OCR mock 前。
- LINE/full ISO fallback、539 same-day、缺少/錯誤日期 fail-closed、wrong Telegram chat 拒絕。
- TTL 20:29:59 與 20:30:00 的跨日規則仍維持。

`test_miss_tg_intake_bot.py` 也更新了 text payload 的新欄位期望。這些是 commit 內容與 test source 證據；本次沒有找到 d983b90 的實際 unittest execution output，因此 `OFFLINE_PASS` 不能由 commit 本身宣稱。前一版查核的 29/24/10 focused outputs 發生在此 commit 之前，不能倒填成 d983b90 版本測試結果。

`b12_draw_progress.log:136-138,169-171` 的 `tg_m1004415191836_9 ... status=SENT` 也不能當 live acceptance：該 event 沒有 `miss_state` row、ORDER `tg_inbox` row 或 archive image，且同一 ID 直接硬編在既有 offline `test_b12_chang_telegram_image_route.py:260,284`。同理，新增 test 的 exact webhook `message_id='7'` 使用真實測試群 ID 並可能 emit `MISS_RECEIVED`；任何同 ID log 觀察行都要先排除 offline mock/test 來源，不能當成新收到的 `_7`。

### Runtime loaded / live 狀態

目前有一點時間相容證據：`ypm_ocr_server.py` process start `07:26:18`、`miss_tg_intake.py` process start `07:26:30`，晚於 commit `07:25:21`；兩個 source mtime 也為 `07:24:17`。但 startup log 沒有 source hash、commit ID 或版本 marker，`miss_tg_intake.log` 也沒有對應的 post-commit startup entry；process start 只能說時間上可能載入過新檔，不能證明 resident code hash。因此目前仍是：

- `DEPLOYED`：本輪未作部署動作，不能以 commit 在 current HEAD 代替 Formal deploy receipt。
- `RUNTIME_LOADED`：`UNKNOWN/未證明`；不以 process start 時間代替。
- `LIVE_ACCEPTANCE_PASS`：未達成；`_6/_7` 是 commit 前的 `REPORT_DATE_REQUIRED`，`_9` 是 test-like progress，沒有新的自然事件完整鏈。

### 更新後的下一個有界驗收動作

不重送 `_6/_7`、不重放 `_9`、不因測試 log 啟動新流程。下一步只在既有 exact scope 已涵蓋，或使用者另給相應 live 授權/自然新測試圖時進行：以一個全新的 message ID 查 ORDER raw `tg_inbox`、MISS `MISS_RECEIVED`、`source_event_timestamp`/`route_timestamp`、archive，再按同一 event 逐層核對 OCR、GS write/readback、render 與 send receipt。若沒有這筆新的自然事件，就只能把 d983b90 標成 `SOURCE_CANDIDATE_PRESENT/待離線執行與 runtime 證明`，不能標 `RUNTIME_LOADED` 或 `LIVE_ACCEPTANCE_PASS`。

本追加段落只更新版本事實與驗收邊界；原提案的歷史證據、9/11 message 99 的 `UNKNOWN`、圖片日期需獨立核對及不改業務日期規則仍然有效。
