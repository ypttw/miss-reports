# 2026-09-13 兩筆中球解析錯例：最小修正提案

本文件是唯讀調查結果與候選方案。這一輪沒有修改 `D:\MISS` 的 production、candidate、test 或 runtime，也沒有寫 GS／業務 DB、重送、下注、restart、deploy、commit 或 push。只有本文件寫入 `D:\AI Agent\MISS\reports\mxiaofu\`。

## 結論先行

- `631393184504873511` 的第一個可驗證錯層是 `D:\MISS\miss_middle_parser.py` 的日期／彩種標題辨識。現有 `_is_lottery_header()` 只接受整行日期標題的空白分隔；`9/12。天天` 正規化成 `9/12.天天` 後沒有被當成標題，日期遂進入選號掃描。這已足以解釋保存解析多出 `09,12` 及 35 對 34 的列數差異。
- `631465498483359907` 的第一個可驗證錯層也是 `D:\MISS\miss_middle_parser.py`，但屬於另一個 grammar gap：現有全車 suffix grammar 沒有宣告 `539、選號、車、各N元` 這個 YPM 形狀。專用 car parser 因而沒有取得 `10,33` 與 `5元` 的欄位所有權；後續 legacy fallback 仍可能把殘留金額當選號。現有 code 有一般全車修正，沒有覆蓋這個 exact raw shape。
- 保存解析是歷史結果，不是 first-parse snapshot。因而可以確認原文與保存解析的語意不一致，也可以確認 current code 的具體 grammar 缺口。主管另以 `python -B` 對 current `parse_middle_text()` 做純 parser reproduction，已重現兩個 exact shape 的 current 錯誤；這證明目前 source 仍有問題，不等同於證明 9/12 當時第一次解析一定使用目前這個 commit。要作歷史版本歸因，仍要有 event 綁定的 first parser input／result 與當時 loaded revision。

## 唯讀 preflight 與 current version

- 協調根 `D:\AI Agent\MISS`：`main`、HEAD `59d9d7e0c96564f4f0ea3df025fc593ee31c6228`；已有 dirty files，與本案 parser 檔案無 overlap。
- Formal 根 `D:\MISS`：`checkpoint/miss-pre-p0-fixes-complete-20260911`、HEAD `29adcb5aa9a4ba657798d0ee6005f29f445e5cb1`；已有 `config/window_layout.json`、`miss_accounting_delivery.py`、`miss_accounting_runtime.py` 與 `.worktrees/` dirty/untracked，`miss_middle_parser.py`、`miss_pipeline.py`、`miss_event_service.py`、`miss_nonhit_parser.py`、`miss_ticket_semantics.py` clean。
- 本次讀到的 `D:\MISS\miss_middle_parser.py` SHA-256 是 `C45199EDCF3B79AB0BD208E5B093522C7CF5C834D04C1BEE09EB5FB61EFCF1A0`。現有 header 修正來自 `69580fef`；現有 token-ownership／suffix-car 修正來自 `303ef3e`。兩者都早於本次 exact event，卻沒有涵蓋下面兩個形狀。
- 沒有在兩個 root 找到本次適用的 `AGENTS.md`、`PROJECT_CONTROL.md` 或 `OPEN_ISSUES.md`；已依 `D:\AI Agent\MISS\MISS_NIGHT_OPS_AGENT_PLAN_20260912.md` 的唯讀與 approval gate 執行。

## 事件證據與流程邊界

舊附件 `D:\AI Agent\MISS\reports\mxiaofu\2026-09-12_plain_language.md` 的第 224–263 行記載 `631393184504873511`：原文第一行是 `9/12。天天`，後續有 `27,38孤碰8碰`、`27,39孤碰8碰`、`27,09孤碰8碰` 等；保存解析第 1 列是 `9,12`，後續列是二星 `8`，共 35 列，而小新分頁列 6–39 是 34 個真正下注列。父本次覆核也確認第一行邊界及 `09/12` 合法選號必須受到保護。

同一檔案第 741–749 行記載 `631465498483359907`：原文為 `539、10、33、車、各5元`，保存解析是選號 `10,33,5`，目標 YPM 分頁是選號 `10,33`、全車 `5`。`2026-09-12_full_report.md` 第 61–69 行把兩者列為原文／保存解析的解析錯例，並明確說沒有 first-parse snapshot 時不能把保存值稱為第一次解析。

主管以目前 Formal source 做了無副作用的 `python -B` 純 parser 驗證，沒有改檔、test、DB 或 runtime：

- 第一案使用已提供的最小片段 `9/12。天天\n\n27,38孤碰8碰\n27,39孤碰8碰\n27,09孤碰8碰`；current `_is_lottery_header()` 回傳 `False`，`allow_selection_only=True` 產生額外一列 `selection=09.12`，其餘三列仍是 `27.38`、`27.39`、`27.09` 且 `star2=8`。
- 第二案使用完整原文 `539、10、33、車、各5元`，以 YPM／539／`allow_selection_only=False` 呼叫；current parser 產生 `selection=10.33.05`、`car=""`、`manual_check=True`。

這是 current code 已重現；第一案只使用主管提供的最小片段，不能拿它宣稱完整原文的 34 列已全部重播。歷史保存值與 current reproduction 仍是兩個時間層，不能互相代替。

目前正常文字路由在 `D:\MISS\miss_pipeline.py:214-240,979-983`：小新文字依明確 `天天` 決定天天樂，YPM 固定 `539`。實際中球解析在 `D:\MISS\miss_event_service.py:4647-4722` 呼叫同一個 `parse_middle_text()`：小新傳 `allow_selection_only=True` 且不傳 `source`；YPM 傳 `lottery="539", allow_selection_only=False, source="YPM"`。因此這兩筆目前可驗證的第一個錯層都在中球 parser 邊界，不是 GS writer 或 downstream 分頁比對。

## 事件一：`631393184504873511` 日期被當成選號

### 已證實的原因

1. `D:\MISS\miss_middle_parser.py:142-200` 的 `_normalize_symbols()` 把 `。` 轉成 `.`，所以標題變成 `9/12.天天`。
2. `D:\MISS\miss_middle_parser.py:2875-2888` 的 `_is_lottery_header()` 以 `re.fullmatch()` 判斷日期標題；既有 pattern 接受 `9/12 天天`，但不接受日期與彩種之間的 `.`。同一行若含後續票面內容，也不能靠現有 full-line match 略過。
3. `_is_lottery_header()` 的 fallback 只會呼叫 `_strip_context()`；`D:\MISS\miss_middle_parser.py:203-222` 的 `_strip_context()` 移除 `天天`，沒有移除前面的日期。
4. `D:\MISS\miss_middle_parser.py:661-758` 的 `_selection_from_text()` 對留下的 `9/12` 以數字 token 掃描並 zfill，得到 `09`、`12`。這是在選號欄位形成錯誤列的第一個可驗證位置。
5. `D:\MISS\miss_middle_parser.py:74-86` 的 `_normalize_middle_pong_notation()` 已明確把 `孤碰`／`8碰` 轉為一般星數／金額表示；現有 evidence 沒有顯示孤碰語意是第一錯層。修正應在標題辨識邊界完成，不能刪掉 `27,38`、`27,09` 或二星 `8`。

### current code 是否已修好

未修好這個 exact shape，而且已由 current pure parser reproduction 重現：`_is_lottery_header("9/12.天天")` 是 `False`，最小片段會多出 `09.12`。`69580fef` 的既有修正只涵蓋完整行的日期／彩種 caption；目前 source 沒有 `9/12.天天` 的 punctuation-aware full-line branch，也沒有以 event timestamp 任意刪除 slash。這個 current reproduction 不會把歷史保存結果升格為 first parser revision。

### 最小候選修正（須使用者核准後才可製作 candidate）

檔案：`D:\MISS\miss_middle_parser.py`。函式：`_is_lottery_header()`。

- 修改前：日期與彩種只容許空白相接，例如 `8/13 539:`；`9/12.天天` 不匹配，後續日期進入 `_selection_from_text()`。
- 修改後：只在**整行**是「日期 + 明確彩種」時，讓現有 full-line header pattern 接受正規化後日期與彩種之間的一個 `.`（原始 `。`／`、` 會先被 `_normalize_symbols()` 正規化）。例如 `9/12.天天` 會被略過；含真正票面動作的行不因有 slash 就整行丟掉。
- 這個候選不把 `_selection_from_text()` 改成全域刪除日期，也不把任意 `09/12` 當 header。回歸案例要明確包含合法 `09/12` 選號加上玩法，確認它不會被這個 full-line-only 修正刪掉。
- 如果之後取得的 event 綁定 parser input 證明 `/ /` 是同一物理行而不是報告用的換行顯示，才另行設計「有明確 header 分隔邊界才拆」的窄規則；在該 evidence 出現前不做 inline 全域 stripping。

候選後對本事件的預期是：第一個可寫候選從 `27,38` 開始；`27,38孤碰8碰`、`27,39孤碰8碰`、`27,09孤碰8碰` 的二星 `8` 與選號保持；不再產生日期 `09,12` 額外列。完整 34 列仍須以 event 綁定的完整 parse input／目標分頁內容驗證，報告目前的原文以省略號結尾，不能自行補猜省略部分。

## 事件二：`631465498483359907` 全車金額被掃成選號

### 已證實的 current grammar gap

`D:\MISS\miss_middle_parser.py:2600-2707` 的 `_parse_middle_line()` 先走 `_parse_known_suffix_car_expression()`、`_parse_aliasless_x_each_car_expression()`，再走 `_parse_suffix_car_expression()` 與 `_parse_prefix_car_expression()`。

- `_KNOWN_SUFFIX_CAR_RE`（檔案前段約 37–45 行）要求選號從 1–2 位 token 開始，後接 car alias；exact raw 卻從 `539` 開始，且 `539` 是彩種前綴，不是選號。
- `_parse_suffix_car_expression()` 的 `named_delimited`（約 1111–1131 行）可讀 `選號、車各5元`，但要求 `車` 後直接接 `各`／金額；exact raw 是 `車、各5元`，多了一個分隔號。
- 同函式的 numeric guard（約 1132–1155 行）只有在 car 前的數字前綴可證明只是 `539` 時才放行；exact raw 在 `車` 前還有 `10、33`，因此 guard 不能把它當成一個完整 car expression。
- `_find_car_action()`（約 382–405 行）只宣告 car alias 後直接金額，或金額 token 直接接 car alias；`車、各5元` 不符合。專用 parser 沒取得欄位所有權後，`_parse_middle_line()` 約 2847–2868 行的 legacy `parse_ticket()` 相容入口仍可能把殘留 `5` 留在 selection。這個 source-level fallback path 與保存的 `10,33,5` 語意一致，但在缺少 first snapshot 時，不能聲稱歷史當下必定走了這條 path。

因此目前不是「YPM 的 `1車` 單位 contract 沒有修好」：`D:\MISS\miss_ticket_semantics.py:198-224` 已將 YPM bare `1` 與 explicit `元` 分開，既有 tests 也涵蓋 `23*2車`。本事件先要修的是 `車、各5元` 的 action ownership；一旦 car branch 取得 `5`，現有 explicit `元` contract 會保留 `5`，不應再另改 amount semantics。

### current code 是否已修好

只有一般 suffix／prefix car 形狀已修正；exact `539、10、33、車、各5元` 沒有 current pattern，而且已由 current pure parser reproduction 重現為 `selection=10.33.05`、`car=""`、`manual_check=True`。這是可直接由 regex、parser 呼叫順序與 current output 共同驗證的剩餘 gap。歷史保存結果仍不能綁定到 current HEAD，也不能把 current reproduction 當成當時 first parse receipt。

### 最小候選修正（須使用者核准後才可製作 candidate）

檔案：`D:\MISS\miss_middle_parser.py`。函式：`_parse_suffix_car_expression()`。

- 修改前：沒有一個 anchored branch 同時擁有 `539` 前綴、`10、33` selection、`車`、`各`、explicit `元`。
- 修改後：在既有 named suffix branch 前加入一個窄的 anchored branch，只接受本事件的語意形狀：leading explicit `539`、至少兩個 1–2 位選號、`車` alias、可選的一個分隔號、`各`、amount、`元／塊`。它以既有 `_selection_from_text()` 解析選號，並以 `_canonical_car_amount()` 填入 car；未知單位、缺少號碼、沒有 leading `539` 的文字仍走原本分支／人工 gate。
- 這個 branch 的預期 canonical row 是 `selection="10.33"`、`numbers=("10","33")`、`car="5"`、沒有 `05` 選號；原始 raw 保留完整 `539、10、33、車、各5元`。不改 `_find_car_action()` 的一般規則，也不放寬成任意「各」都代表全車。

選擇新增窄 anchored branch，而不是放寬既有 `named_delimited`，是因為該 regex 使用 `re.search()` 且選號群組左側沒有 `(?<!\d)` 邊界。若只放寬 `車` 後的分隔號，`539、10、33、車、各5元` 可能從 `539` 的尾巴 `39` 開始匹配，形成錯誤選號 `39,10,33`；anchored branch 先宣告完整 leading `539` 是彩種前綴，才能阻止 `539` 尾巴進入 selection。

## 不改事項與保護界線

- 不改 `route_event()`、YPM／小新分頁選擇、`EventService`、GS writer、SQLite schema、callback、OCR provider、W、scheduler 或任何下注／傳送流程。
- 不在本輪修改 production、candidate、test、truth fixture 或 expected rows；不回寫兩筆歷史資料，不重播、不重送、不啟動／重啟 W。
- 日期候選只處理明確 header 行，不以 slash、時間、最新列或 screenshot 猜配；合法 `09/12` 選號、`27,09`、`孤碰8碰` 都要保留。
- YPM 候選只處理明確 `車、各N元` 所有權；`23*1車`（YPM implicit 100）、`23*2車`（explicit 2）、`車34？17？15？10？各50元`、各種 car alias、缺單位的未知格式仍受既有 gate 控制。

## 現有離線證據

先檢查了既有測試的 header／car grammar，沒有新增或改寫 test。已在 Formal 唯讀執行兩組明確 `unittest`：

```text
python -m unittest -v test_human_truth_parser_rc_20260825.py test_source_amount_lexical_unification_20260825.py test_rc_car_selection_boundary_20260825.py test_miss_middle_parser_vertical.py
Ran 32 tests in 0.484s
OK

python -m unittest -v test_parser_b_gap_repair_20260826.py test_parser_common_gap_repair.py
Ran 43 tests in 0.161s
OK
```

這 75 個 PASS 只能證明既有離線案例通過；它們沒有覆蓋主管本次重現的兩個 exact shape，也不能證明當時 runtime 已載入 current code。現有 PASS 特別保護了：

- B：`B_539_same_line_and_pillars` 的 539 同行／柱位語意。
- C：`C_pong_pong_blank_boundary_and_car_state` 的碰碰 blank boundary、全車 state；另有 `孤碰` normalization source code。
- D：`D_tian_tian_two_rows` 的天天樂兩列。
- E：`E_539_car_amount_is_not_scaled` 的 539 explicit car amount。
- car token ownership matrix、known car aliases、缺少 unit 應人工、前後日期 token 的 source coverage，以及 YPM `1車`／`2車` contract。

## 核准後的驗收設計

### Offline RED → minimal fix → GREEN

先建立兩個 exact regression（只使用 event 綁定的完整原文，不把省略號當資料）：

1. 小新：第一行 `9/12。天天`，後續至少包含 `27,38孤碰8碰`、`27,39孤碰8碰`、`27,09孤碰8碰`。RED 應能指出 header 形成 `09,12` 額外列；GREEN 要確認不再有日期列，第一筆為 `27,38`、二星 `8`，`27,09` 保持有效選號。
2. YPM：`539、10、33、車、各5元`。RED 應能指出 car action 沒有取得 selection／amount ownership；GREEN 要只有一列 `10.33`、全車 `5`，不含 `05`。

同一輪回歸必須重跑 B/C/D/E、既有 car boundary、known alias、missing-unit manual、date-before/after-action coverage 與 vertical／pong tests；對候選檔跑 `python -m unittest`、`py_compile`、`git diff --check`，並確認 dirty overlap 仍為零。任何正常案例列數、`09/12` 選號、孤碰金額或 `1車` 單位改變，都停止，不進下一層。

### Isolated actual-path simulation

以無外部連線的 event double 驗證：

- 小新 route 取得 `天天樂`，YPM route 取得 `539`；兩筆都只進 `parse_middle_text()`，raw event text 完整保留。
- 對小新確認 parser rows 與目標列數／順序，對 YPM 確認 selection／car 欄位；不呼叫 worksheet、SQLite write、callback、OCR 或 browser。
- 對 exact raw 若 physical line boundary 與附件顯示的 `/` 不一致，將該差異標為阻擋，不自行把 slash 拆成行。

### 實戰／live acceptance

本輪沒有 `DEPLOYED`、`RUNTIME_LOADED`、`LIVE_ACCEPTANCE_PASS` 或 `PRODUCTION_STABLE`。只有在使用者核准 candidate、完成離線與 isolated pass 後，才可另行安排 bounded deployment。實戰驗收需以同一 `event_id` 對照 raw、parser result、GS readback 與後續業務 receipt；本提案不會觸發任何 live side effect。

## 仍需的證據與使用者回答

- 兩筆的業務語意本身沒有待猜的問題：第一筆是移除 `9/12。天天` 標題並保留後續孤碰二星 `8`，第二筆是 `10、33` 全車 `5元`。
- 需要使用者回答的是是否核准以上兩個**最小 parser logic candidate**；未收到核准前不改 code/test。
- 若要把「保存解析錯」進一步升級為「當時 first parser 的確切 root cause」，下一個唯讀取證動作是以 exact `event_id` 取出當時保存的 parser input／`parse_result_json`、first parse／revision metadata（若存在），並確認 `_miss_parse_text` 的 physical line boundary。找不到這些 immutable evidence 時，歷史版本歸因仍是 `UNKNOWN`；兩個 current grammar gap 與候選修正不受此阻擋。

## 07:38 主管補查：兩筆完整原文已由 SQLite 取得

前段「只取得第一筆最小片段、完整原文仍待查」是提案初稿時的狀態，本次已補足，不再向使用者索取已存在的資料。

- 來源：`D:\MISS\miss_state.sqlite3`，以 `mode=ro`、`PRAGMA query_only=ON` 開啟，`quick_check=ok`；只按兩個 exact event ID 讀取 `events.raw_text`、保存解析及修訂數量。沒有業務寫入或 live 呼叫。
- current Formal HEAD 仍為 `d983b90bfff88197a758f886429d5b6ecb1abb21`；`miss_middle_parser.py` 無 dirty，沿用前段相同 hash。這一版 Chang 日期修改不涉及 parser。
- `631393184504873511` 的完整 raw_text 是一行 `9/12。天天` 日期標題及 34 行孤碰注單，實際保存的是換行而非報告分隔符。全文 SHA256：`9c711ea63d29c179918b12fc4888158087f49baf37c1be26e7c503943bd9222c`。
- 主管以完整 raw_text 及實際小新呼叫參數（`lottery="天天樂"`、`allow_selection_only=True`、`source=""`）執行既有純 parser：共 35 列，第一列錯為 `09.12`，其後 34 行仍是原注單。保存 `middleParse` 也是 35 列。逐列核對選號／全車／二星／三星／四星，僅統一選號分隔符後，兩者沒有欄位差異。這確認 current code 可重現完整保存結果，並未證明歷史當時載入的版本。
- `631465498483359907` 的完整 raw_text 為 `539、10、33、車、各5元`；全文 SHA256：`0d32c8a5fe49668f23b9805a04aa1f0e61a311d498dff9561b564def72a74f36`。以實際 YPM 參數執行純 parser，保存與 current 都只有一列 `10.33.05`、全車空；同樣逐欄相符。
- 兩個 event 的 `editor_revisions` 均為 0。這只能說此表沒有對應修訂，不證明其他入口從未修改，也不把保存解析稱為第一次解析。

核准後驗證改用第一筆完整 34 行原文，不能只驗證三行例子：修正只移除多出的日期列，其餘 34 行的選號、玩法與金額逐欄保持。第二筆只應得到 `10.33`、全車 `5`。兩項邏輯候選仍等待使用者核准；本次沒有新增測試、改 parser、回填或重播舊注單。
