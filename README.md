# MISS & MISS ORDER 每日對帳與稽核報告庫

此倉庫為 **M小福 (M-XiaoFu)** 每日對帳稽核報告與產出物的專屬私有發布庫，方便主管及團隊在手機（GitHub Mobile App 或手機瀏覽器）隨時隨地安全查閱。

---

## 📱 手機快速查看目錄

### 📅 2026-09-12 每日稽核專案
- **完整日報 (白話+技術)**: [`reports/mxiaofu/2026-09-12.md`](reports/mxiaofu/2026-09-12.md)
  - 核心結論：54 筆注單全覆蓋核對完成，5 筆異常注單定性定責，ORDER 21 停擺徹底查明，已完成五大修復提案。
- **全量 54 筆注單逐筆對帳佐證表**: [`reports/mxiaofu/2026-09-12_evidence.md`](reports/mxiaofu/2026-09-12_evidence.md)
  - 完整事件級 109 列對帳資料，包含下注金額、解析金額、差異比對與責任歸屬。
- **行動版 PDF 稽核報告**: [`pdf/2026-09-12_mxiaofu_full_report.pdf`](pdf/2026-09-12_mxiaofu_full_report.pdf)
  - 包含精美封面、章節樣式、對帳表格、防偽校驗章。可在手機端點擊直接預覽或下載。
- **工作日誌**: [`reports/mxiaofu/journal/2026-09-13.md`](reports/mxiaofu/journal/2026-09-13.md)

---

## 🛠️ 修復提案與技術文檔
- **提案 A & B (解析器核心修復)**: [`reports/mxiaofu/2026-09-13_parser_solution_proposal.md`](reports/mxiaofu/2026-09-13_parser_solution_proposal.md)
- **提案 E (Chang TG 照片時戳分析)**: [`reports/mxiaofu/2026-09-13_chang_solution_proposal.md`](reports/mxiaofu/2026-09-13_chang_solution_proposal.md)
- **提案 C & D (ORDER 21 與非注單處理)**: [`reports/mxiaofu/2026-09-13_remaining_ticket_solutions.md`](reports/mxiaofu/2026-09-13_remaining_ticket_solutions.md)

---

## 🔒 安全與隱私保護原則
1. 本倉庫為**私有倉庫 (Private Repository)**，僅授權帳號可見。
2. 嚴格禁止提交任何運行時 Token、API 金鑰、資料庫檔案 (`.db`, `.sqlite`) 或客戶敏感原始個資。
3. 所有對帳資料均經過標準遮罩與脫敏處理。
