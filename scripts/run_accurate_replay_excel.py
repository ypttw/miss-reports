# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import sys
import time
import shutil
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\MISS')

from miss_middle_parser import parse_middle_text
from miss_nonhit_parser import parse_nonhit_text

db_path = r'D:\MISS\miss_state.sqlite3'
output_excel_path = r'D:\MISS\reports\sqlite_all_events_reconciliation.xlsx'
portal_excel_path = r'D:\AI Agent\miss-reports\reports\sqlite_all_events_reconciliation.xlsx'

print(f"Connecting to SQLite {db_path}...")
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
cur = conn.cursor()

cur.execute('''
    SELECT event_id, source, event_time, target_sheet, raw_text, 
           parse_result_json, gs_write_status, manual_status
    FROM events
    ORDER BY rowid ASC
''')
all_events = cur.fetchall()
print(f"Total events fetched from SQLite: {len(all_events)}")

# Create workbook
wb = openpyxl.Workbook()
ws_summary = wb.active
ws_summary.title = "審計摘要 (Summary)"
ws_events = wb.create_sheet(title="事件全量總表 (All Events)")
ws_written = wb.create_sheet(title="已成交實戰單 (Written Only)")
ws_bets = wb.create_sheet(title="逐筆下注對照 (Bet Details)")

font_title = Font(name="Microsoft JhengHei", size=13, bold=True, color="1B365D")
font_section = Font(name="Microsoft JhengHei", size=10, bold=True, color="FFFFFF")
font_data = Font(name="Microsoft JhengHei", size=9)
font_bold = Font(name="Microsoft JhengHei", size=10, bold=True)
font_alert = Font(name="Microsoft JhengHei", size=10, bold=True, color="9C0006")

fill_meta = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
fill_raw = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")
fill_saved = PatternFill(start_color="2980B9", end_color="2980B9", fill_type="solid")
fill_actual = PatternFill(start_color="4A708B", end_color="4A708B", fill_type="solid")
fill_current = PatternFill(start_color="8E44AD", end_color="8E44AD", fill_type="solid")

fill_exact = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
fill_diff = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
fill_improved = PatternFill(start_color="D1ECF1", end_color="D1ECF1", fill_type="solid")
fill_regression = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
fill_empty = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

thin_border_side = Side(border_style="thin", color="D3D3D3")
thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
align_center = Alignment(horizontal="center", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

columns_def = [
    # Meta (0-5)
    ("序號", fill_meta, 8, align_center),
    ("Event ID", fill_meta, 22, align_center),
    ("時間", fill_meta, 12, align_center),
    ("來源", fill_meta, 10, align_center),
    ("解析路由類型\n(中球 / 不中記錄)", fill_meta, 16, align_center),
    ("目標工作表", fill_meta, 12, align_center),
    # Raw (6)
    ("【原始訊息】\nraw_text", fill_raw, 32, align_left),
    # 當時解析結果 (7-13)
    ("【當時保存解析】\n選號", fill_saved, 20, align_left),
    ("【當時保存解析】\n支數/組數", fill_saved, 10, align_center),
    ("【當時保存解析】\n玩法/說明", fill_saved, 14, align_left),
    ("【當時保存解析】\n全車", fill_saved, 10, align_center),
    ("【當時保存解析】\n二星", fill_saved, 10, align_center),
    ("【當時保存解析】\n三星", fill_saved, 10, align_center),
    ("【當時保存解析】\n四星", fill_saved, 10, align_center),
    # 實戰執行狀態查核 (14-16)
    ("【GS 寫入狀態】\ngs_write_status", fill_actual, 14, align_center),
    ("【終端回執鏈路】\n(bet_attempts 外鍵)", fill_actual, 24, align_center),
    ("【實戰回執備註】\n(嚴禁以保存解析充數)", fill_actual, 32, align_left),
    # 最新重跑解析 (17-23)
    ("【最新重跑】\n選號", fill_current, 20, align_left),
    ("【最新重跑】\n支數/組數", fill_current, 10, align_center),
    ("【最新重跑】\n玩法/說明", fill_current, 14, align_left),
    ("【最新重跑】\n全車", fill_current, 10, align_center),
    ("【最新重跑】\n二星", fill_current, 10, align_center),
    ("【最新重跑】\n三星", fill_current, 10, align_center),
    ("【最新重跑】\n四星", fill_current, 10, align_center),
    ("【審計比對結果】\n(回放判定)", fill_current, 20, align_center)
]

for ws in [ws_events, ws_written, ws_bets]:
    ws.row_dimensions[1].height = 28
    headers = [col[0] for col in columns_def]
    ws.append(headers)
    for col_idx, col_info in enumerate(columns_def, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = font_section
        cell.fill = col_info[1]
        cell.alignment = align_center
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = col_info[2]

stats = {
    'total_events': len(all_events),
    'route_record': 0,
    'route_middle': 0,
    'written_events': 0,
    'EXACT_MATCH': 0,
    'DIFF_CONTENT': 0,
    'IMPROVED': 0,
    'BOTH_EMPTY': 0,
    'REGRESSION': 0,
    'regression_image': 0,
    'regression_text': 0
}

t0 = time.time()
event_row_idx = 2
written_row_idx = 2
bet_row_idx = 2

for ev_idx, row in enumerate(all_events, 1):
    ev_id, source, ev_time, target_sheet, raw_text, pj_str, gs_stat, man_stat = row
    target_sheet_str = str(target_sheet or '').strip()
    raw_text_str = str(raw_text or '').strip()
    gs_stat_str = str(gs_stat or '').strip()

    if gs_stat_str == 'written':
        stats['written_events'] += 1

    # Parse saved parse result
    pj = {}
    if pj_str:
        try:
            pj = json.loads(pj_str)
        except Exception:
            pj = {}

    mode = pj.get('mode', '')
    has_middle_parse = bool(pj.get('middleParse'))
    has_record_parse = bool(pj.get('recordParse'))

    # Determine True Route (Exact task-280 logic)
    if mode == '中球文字' or has_middle_parse:
        route = 'middle'
    elif mode == '不中文字':
        route = 'record'
    elif target_sheet_str in ('YPM', '小新', '539', '天天樂'):
        route = 'middle'
    elif '記錄' in target_sheet_str:
        if any(kw in raw_text_str for kw in ('不中', '800*', '800x', '800X', '800 *', '800 x')):
            route = 'record'
        elif any(kw in raw_text_str for kw in ('碰碰', '專車', '全車', '車', '星', '連碰')):
            route = 'middle'
        else:
            route = 'record' if has_record_parse else 'middle'
    else:
        route = 'middle'

    route_name = "中球解析 (middle)" if route == 'middle' else "不中/記錄解析 (record)"
    if route == 'middle': stats['route_middle'] += 1
    else: stats['route_record'] += 1

    # Extract Saved Bets
    saved_bets = []
    if route == 'middle' and has_middle_parse:
        for m in pj.get('middleParse', []):
            if isinstance(m, dict):
                saved_bets.append({
                    'selection': str(m.get('selection') or '').strip(),
                    'count': '',
                    'play': '',
                    'car': str(m.get('car') or '').strip(),
                    'star2': str(m.get('star2') or '').strip(),
                    'star3': str(m.get('star3') or '').strip(),
                    'star4': str(m.get('star4') or '').strip(),
                })
    elif route == 'record' and has_record_parse:
        for r in pj.get('recordParse', []):
            if isinstance(r, dict):
                saved_bets.append({
                    'selection': str(r.get('numbers') or r.get('selection') or '').strip(),
                    'count': str(r.get('count') or '').strip(),
                    'play': str(r.get('play') or '').strip(),
                    'car': str(r.get('car') or '').strip(),
                    'star2': str(r.get('star2') or '').strip(),
                    'star3': str(r.get('star3') or '').strip(),
                    'star4': str(r.get('star4') or '').strip(),
                })
    elif has_middle_parse:
        for m in pj.get('middleParse', []):
            if isinstance(m, dict):
                saved_bets.append({
                    'selection': str(m.get('selection') or '').strip(),
                    'count': '',
                    'play': '',
                    'car': str(m.get('car') or '').strip(),
                    'star2': str(m.get('star2') or '').strip(),
                    'star3': str(m.get('star3') or '').strip(),
                    'star4': str(m.get('star4') or '').strip(),
                })
    elif has_record_parse:
        for r in pj.get('recordParse', []):
            if isinstance(r, dict):
                saved_bets.append({
                    'selection': str(r.get('numbers') or r.get('selection') or '').strip(),
                    'count': str(r.get('count') or '').strip(),
                    'play': str(r.get('play') or '').strip(),
                    'car': str(r.get('car') or '').strip(),
                    'star2': str(r.get('star2') or '').strip(),
                    'star3': str(r.get('star3') or '').strip(),
                    'star4': str(r.get('star4') or '').strip(),
                })

    # Terminal Betting Receipt status - HONEST AUDIT (DO NOT FAKE WITH SAVED_BETS!)
    if gs_stat_str == 'written':
        receipt_link_status = "BLOCKED_AT_IDENTITY"
        receipt_note = "GS已寫入；但SQLite缺終端單號外鍵，無法逐筆證明回執"
    elif gs_stat_str in ('ignored', 'duplicate_suppressed', 'manual_required', 'write_error', 'cancelled'):
        receipt_link_status = "NOT_WRITTEN"
        receipt_note = f"狀態為 {gs_stat_str}，未寫入GS帳冊"
    else:
        receipt_link_status = "UNKNOWN"
        receipt_note = f"狀態為 '{gs_stat_str}'，無終端關聯"

    # Run Current Worktree Parser (Exact task-280 logic)
    curr_bets = []
    if raw_text_str and not raw_text_str.startswith('[圖片'):
        try:
            if route == 'middle':
                lottery = '539'
                if '天天' in raw_text_str or '天天' in target_sheet_str:
                    lottery = '天天樂'
                res = parse_middle_text(raw_text_str, source=source or 'LINE', lottery=lottery)
                for b in res.bets:
                    curr_bets.append({
                        'selection': str(b.selection or '').strip(),
                        'count': '',
                        'play': '',
                        'car': str(b.car or '').strip(),
                        'star2': str(b.star2 or '').strip(),
                        'star3': str(b.star3 or '').strip(),
                        'star4': str(b.star4 or '').strip(),
                    })
            else:
                nonhit_rows = parse_nonhit_text(raw_text_str)
                for nr in nonhit_rows:
                    curr_bets.append({
                        'selection': ','.join(str(n) for n in nr.numbers),
                        'count': str(nr.count or '').strip(),
                        'play': str(nr.smart_play or '').strip(),
                        'car': '',
                        'star2': '',
                        'star3': '',
                        'star4': '',
                    })
        except Exception:
            curr_bets = []

    # Comparison Verdict
    if not saved_bets and not curr_bets:
        verdict = "BOTH_EMPTY"
        stats['BOTH_EMPTY'] += 1
    elif not saved_bets and curr_bets:
        verdict = "IMPROVED (原無現有)"
        stats['IMPROVED'] += 1
    elif saved_bets and not curr_bets:
        verdict = "REGRESSION (現為空)"
        stats['REGRESSION'] += 1
        if raw_text_str.startswith('[圖片'):
            stats['regression_image'] += 1
        else:
            stats['regression_text'] += 1
    else:
        # Compare canonical representation
        def bet_key(b):
            sel = b.get('selection','').replace(' ', '').replace('.', ',').strip()
            nums = ",".join(sorted(str(int(n)) for n in sel.split(',') if n.isdigit()))
            return (nums or sel, b.get('count',''), b.get('play',''), b.get('car',''), b.get('star2',''), b.get('star3',''), b.get('star4',''))
        
        saved_keys = [bet_key(b) for b in saved_bets]
        curr_keys = [bet_key(b) for b in curr_bets]
        
        if saved_keys == curr_keys:
            verdict = "EXACT_MATCH (完全一致)"
            stats['EXACT_MATCH'] += 1
        else:
            verdict = "DIFF_CONTENT (有差異/優化)"
            stats['DIFF_CONTENT'] += 1

    # Helpers
    def agg(b_list, f_name):
        vals = [str(b.get(f_name, '')).strip() for b in b_list if str(b.get(f_name, '')).strip()]
        return "\n".join(vals) if vals else ""

    # Row data for All Events summary sheet
    event_row_data = [
        ev_idx,
        ev_id,
        ev_time,
        source,
        route_name,
        target_sheet_str,
        raw_text_str,
        agg(saved_bets, 'selection'),
        agg(saved_bets, 'count'),
        agg(saved_bets, 'play'),
        agg(saved_bets, 'car'),
        agg(saved_bets, 'star2'),
        agg(saved_bets, 'star3'),
        agg(saved_bets, 'star4'),
        gs_stat_str,
        receipt_link_status,
        receipt_note,
        agg(curr_bets, 'selection'),
        agg(curr_bets, 'count'),
        agg(curr_bets, 'play'),
        agg(curr_bets, 'car'),
        agg(curr_bets, 'star2'),
        agg(curr_bets, 'star3'),
        agg(curr_bets, 'star4'),
        verdict
    ]
    ws_events.append(event_row_data)
    for c_idx, col_info in enumerate(columns_def, 1):
        cell = ws_events.cell(row=event_row_idx, column=c_idx)
        cell.font = font_data
        cell.border = thin_border
        cell.alignment = col_info[3]
    st_cell = ws_events.cell(row=event_row_idx, column=25)
    if "EXACT_MATCH" in verdict: st_cell.fill = fill_exact
    elif "DIFF_CONTENT" in verdict: st_cell.fill = fill_diff
    elif "IMPROVED" in verdict: st_cell.fill = fill_improved
    elif "REGRESSION" in verdict: 
        st_cell.fill = fill_regression
        st_cell.font = font_alert
    else: st_cell.fill = fill_empty
    event_row_idx += 1

    # Detail Rows for Bet Details and Written Only
    max_rows = max(len(saved_bets), len(curr_bets), 1)
    for r_idx in range(max_rows):
        s_b = saved_bets[r_idx] if r_idx < len(saved_bets) else {}
        c_b = curr_bets[r_idx] if r_idx < len(curr_bets) else {}

        detail_row_data = [
            ev_idx if r_idx == 0 else f"{ev_idx}-{r_idx+1}",
            ev_id,
            ev_time,
            source,
            route_name,
            target_sheet_str,
            raw_text_str if r_idx == 0 else "",
            s_b.get('selection', ''),
            s_b.get('count', ''),
            s_b.get('play', ''),
            s_b.get('car', ''),
            s_b.get('star2', ''),
            s_b.get('star3', ''),
            s_b.get('star4', ''),
            gs_stat_str if r_idx == 0 else "",
            receipt_link_status if r_idx == 0 else "",
            receipt_note if r_idx == 0 else "",
            c_b.get('selection', ''),
            c_b.get('count', ''),
            c_b.get('play', ''),
            c_b.get('car', ''),
            c_b.get('star2', ''),
            c_b.get('star3', ''),
            c_b.get('star4', ''),
            verdict if r_idx == 0 else ""
        ]
        ws_bets.append(detail_row_data)
        for c_idx, col_info in enumerate(columns_def, 1):
            cell = ws_bets.cell(row=bet_row_idx, column=c_idx)
            cell.font = font_data
            cell.border = thin_border
            cell.alignment = col_info[3]
        if r_idx == 0:
            st_cell = ws_bets.cell(row=bet_row_idx, column=25)
            if "EXACT_MATCH" in verdict: st_cell.fill = fill_exact
            elif "DIFF_CONTENT" in verdict: st_cell.fill = fill_diff
            elif "IMPROVED" in verdict: st_cell.fill = fill_improved
            elif "REGRESSION" in verdict: 
                st_cell.fill = fill_regression
                st_cell.font = font_alert
            else: st_cell.fill = fill_empty
        bet_row_idx += 1

        if gs_stat_str == 'written':
            ws_written.append(detail_row_data)
            for c_idx, col_info in enumerate(columns_def, 1):
                cell = ws_written.cell(row=written_row_idx, column=c_idx)
                cell.font = font_data
                cell.border = thin_border
                cell.alignment = col_info[3]
            if r_idx == 0:
                st_cell = ws_written.cell(row=written_row_idx, column=25)
                if "EXACT_MATCH" in verdict: st_cell.fill = fill_exact
                elif "DIFF_CONTENT" in verdict: st_cell.fill = fill_diff
                elif "IMPROVED" in verdict: st_cell.fill = fill_improved
                elif "REGRESSION" in verdict: 
                    st_cell.fill = fill_regression
                    st_cell.font = font_alert
                else: st_cell.fill = fill_empty
            written_row_idx += 1

# Populate Summary Sheet
ws_summary.column_dimensions['A'].width = 38
ws_summary.column_dimensions['B'].width = 24
ws_summary.column_dimensions['C'].width = 65

summary_data = [
    ("MISS SQLite 歷史全庫回放比對與終端鏈路審計報告", "", ""),
    (f"報告產出時間: {time.strftime('%Y-%m-%d %H:%M:%S')} (Asia/Taipei)", "", ""),
    ("", "", ""),
    ("【最高審計裁決與部署閘門】", "", ""),
    ("部署核准狀態 (Deployment Gate)", "DEPLOYMENT_VETOED", "使用者依審計直接證據行使否決權：嚴禁 AGY 部署！"),
    ("全庫防回退判定 (Regression Rule)", "FAILED (不合格)", f"存在 {stats['REGRESSION']} 筆回退（REGRESSION > 0），違反全庫防回退準則"),
    ("終端實戰回執鏈路 (Receipt Bridge)", "BLOCKED_AT_IDENTITY", "SQLite written 2,299 筆 vs bet_attempts 120 筆，無外鍵連接，嚴禁造假"),
    ("", "", ""),
    ("【資料庫母體指標】", "", ""),
    ("總 Event ID 筆數", str(stats['total_events']), f"SQLite events 表中全部事件總數 ({stats['total_events']} 筆)"),
    ("中球單路由筆數 (middle)", str(stats['route_middle']), f"分發至中球解析器之筆數 ({stats['route_middle']} 筆)"),
    ("不中／記錄單路由筆數 (record)", str(stats['route_record']), f"分發至不中解析器之筆數 ({stats['route_record']} 筆)"),
    ("已成交實戰 Event 筆數 (written)", str(stats['written_events']), f"GS 寫入狀態標記為 written 之事件 ({stats['written_events']} 筆)"),
    ("SQLite 終端嘗試表記錄數 (bet_attempts)", "120", "bet_attempts 僅 120 筆，且無 event_id 欄位，與 written 筆數嚴重脫節"),
    ("", "", ""),
    ("【最新通用大腦重跑比對成果 (task-280 真實數據)】", "", ""),
    ("完全一致 (EXACT_MATCH)", str(stats['EXACT_MATCH']), "歷史保存注單與最新大腦解析 100% 相同"),
    ("內容差異 / 優化 (DIFF_CONTENT)", str(stats['DIFF_CONTENT']), "包含星數金額修復、缺號補全、自適應多柱優化"),
    ("歷史空白但最新解析成功 (IMPROVED)", str(stats['IMPROVED']), "歷史轉人工或漏認，最新大腦成功識別"),
    ("回退筆數 (REGRESSION)", str(stats['REGRESSION']), f"歷史有解析但最新為空：{stats['REGRESSION']} 筆（直接證偽『零回退』說法！）"),
    ("  └ 圖片注單無 OCR 重跑為空", str(stats['regression_image']), f"原始訊息為 [圖片事件]，重跑無 OCR 導致為空 ({stats['regression_image']} 筆)"),
    ("  └ 文字注單格式差異回退", str(stats['regression_text']), f"文字注單因格式、多柱括號邊界或分流未命中導致為空 ({stats['regression_text']} 筆)"),
    ("兩者皆為空 (BOTH_EMPTY)", str(stats['BOTH_EMPTY']), "非注單閒聊、貼圖或開獎回報"),
    ("", "", ""),
    ("【審計欄位結構與斷鏈說明】", "", ""),
    ("1. 原始訊息 (raw_text)", "raw_text", "通訊軟體接收之原始未加工文字"),
    ("2. 當時保存解析", "選號/支數/玩法/全車/二三四星", "當時 SQLite parse_result_json 保存之解析輸出"),
    ("3. GS 寫入狀態", "gs_write_status", "SQLite 中記錄之 Google Sheets 寫入狀態 (如 written, ignored)"),
    ("4. 終端回執鏈路", "BLOCKED_AT_IDENTITY", "因架構缺乏 event_id 外鍵，嚴禁以保存解析複製充數，誠實標註斷鏈"),
    ("5. 最新重跑解析", "選號/支數/玩法/全車/二三四星", "依中球/不中分流以最新 parser 重跑之真實結果")
]

for r_idx, row in enumerate(summary_data, 1):
    ws_summary.append(row)
    if r_idx == 1:
        ws_summary.cell(row=1, column=1).font = font_title
    elif "【" in str(row[0]):
        ws_summary.cell(row=r_idx, column=1).font = font_bold
    elif "DEPLOYMENT_VETOED" in str(row[1]) or "FAILED" in str(row[1]):
        ws_summary.cell(row=r_idx, column=1).font = font_alert
        ws_summary.cell(row=r_idx, column=2).font = font_alert
        ws_summary.cell(row=r_idx, column=3).font = font_alert
    else:
        for c in range(1, 4):
            ws_summary.cell(row=r_idx, column=c).font = font_data

print(f"Saving updated Excel to {output_excel_path}...")
wb.save(output_excel_path)
print("Saved to MISS reports.")

print(f"Copying updated Excel to {portal_excel_path}...")
os.makedirs(os.path.dirname(portal_excel_path), exist_ok=True)
shutil.copy2(output_excel_path, portal_excel_path)
print("Copied to Portal.")

print(f"Done! Replayed and generated Excel in {time.time() - t0:.1f}s")
print(f"Stats: {stats}")
