# MISS & MISS ORDER 每日對帳與稽核門戶

此倉庫為 **M小福 (M-XiaoFu)** 每日對帳稽核報告與產出物的專屬發布庫，提供完整**單頁網頁門戶 (Web Portal)**、行動版 PDF、每日專案修改記錄 (Changelog) 與工作日誌，方便主管及團隊在手機或電腦隨時隨地安全查閱。

---

## 🌐 網頁直接瀏覽門戶 (Web Portal)

- **線上直接瀏覽**: [`index.html`](index.html)
  > 💡 包含 8 大功能分頁、即時表格關鍵字搜尋（支援事件 ID、金額、玩法篩選）、深淺主題切換與行動端響應式介面，不必手動翻閱目錄或閱讀原始 Markdown 檔案！
- **行動版 PDF 總報告**: [`pdf/2026-09-12_mxiaofu_full_report.pdf`](pdf/2026-09-12_mxiaofu_full_report.pdf)（支援手機直接預覽與下載）

---

## 📅 每日對帳與專案變更目錄

### 1. 2026-09-13（週日）
- **專案每日修改記錄 (Changelog)**: [`reports/mxiaofu/changelog/2026-09-13.md`](reports/mxiaofu/changelog/2026-09-13.md)
  - 記錄提案 A/B 解析器修復提交 `15b73f1`、外部 Agent B12 常勝軍時戳邊界 11 筆提交、MISS ORDER 5 筆提交，以及 Port 5005 生產熱部署 PID 38176。
- **M小福每日工作日誌**: [`reports/mxiaofu/journal/2026-09-13.md`](reports/mxiaofu/journal/2026-09-13.md)
  - 記錄 0912 報告交付、TDD 驗證 GREEN、全量 164 測試回歸對照、1,874 筆凍結注單實戰回放與 13:20 生產環境熱部署歷程。

### 2. 2026-09-12（週六）
- **完整日報 (白話整體摘要 + 10 大核心章節)**: [`reports/mxiaofu/2026-09-12.md`](reports/mxiaofu/2026-09-12.md)
  - 54 筆注單全覆蓋審計、5 筆異常注單定性定責、ORDER 21 停擺根因剖析與五大最小修復提案。
- **全量 54 筆注單逐筆對帳佐證表**: [`reports/mxiaofu/2026-09-12_evidence.md`](reports/mxiaofu/2026-09-12_evidence.md)
  - 完整 109 列逐筆四層比對（原單 -> 保存解析 -> 人工修改 -> 分頁/PY）。
- **專案每日修改記錄 (Changelog)**: [`reports/mxiaofu/changelog/2026-09-12.md`](reports/mxiaofu/changelog/2026-09-12.md)
  - 完整記錄 2026-09-12 全天 MISS 專案 30 筆提交（B12 常勝軍、LINE 發送、GS 429 配額重試等）。

---

## 🛠️ 技術修復提案專區

- **提案 A & B (解析器核心修復，已部署)**: [`reports/mxiaofu/2026-09-13_parser_solution_proposal.md`](reports/mxiaofu/2026-09-13_parser_solution_proposal.md)
- **提案 E (Chang TG 照片時戳分析)**: [`reports/mxiaofu/2026-09-13_chang_solution_proposal.md`](reports/mxiaofu/2026-09-13_chang_solution_proposal.md)
- **提案 C & D (ORDER 21 筆與非注單處理)**: [`reports/mxiaofu/2026-09-13_remaining_ticket_solutions.md`](reports/mxiaofu/2026-09-13_remaining_ticket_solutions.md)

---

## 🔒 安全與隱私保護原則

1. 本倉庫嚴格禁止提交任何運行時 Token、API 金鑰、資料庫檔案 (`.db`, `.sqlite`) 或客戶敏感原始個資。
2. 所有對帳資料與注單均經過標準遮罩與脫敏處理。
