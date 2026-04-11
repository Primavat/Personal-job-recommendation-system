"""
sheets_manager.py — Google Sheets integration via gspread.

Tabs created:
  🇮🇳 India Jobs   — roles located in India
  🌍 Global Jobs   — all non-India roles
  📋 All Jobs      — every job combined
  📊 Summary       — stats dashboard
  🕐 Run History   — log of every pipeline run

Auth methods:
  service_account — credentials.json
  oauth           — browser login (oauth_client.json)
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from config import Config

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

COLUMNS = [
    "Job Title", "Company", "Location", "Type", "Category",
    "Tags / Skills", "Date Posted", "Source", "Apply Link", "AI Summary", "Row Added",
]

# India-related keywords for location matching
INDIA_KEYWORDS = [
    "india", "bengaluru", "bangalore", "mumbai", "delhi", "hyderabad",
    "chennai", "pune", "kolkata", "ahmedabad", "noida", "gurgaon",
    "gurugram", "jaipur", "surat", "kochi", "indore", "remote (india)",
    "remote, india", "in, india",
]

CATEGORY_COLOURS = {
    "AI / ML":               {"red": 0.84, "green": 0.94, "blue": 0.84},
    "Frontend / Web":        {"red": 0.84, "green": 0.90, "blue": 1.00},
    "Software Engineering":  {"red": 1.00, "green": 0.96, "blue": 0.80},
    "Backend / Full Stack":  {"red": 1.00, "green": 0.88, "blue": 0.80},
    "Data Engineering":      {"red": 0.90, "green": 0.84, "blue": 1.00},
    "DevOps / Cloud":        {"red": 0.80, "green": 0.96, "blue": 0.96},
    "Quantum Computing":     {"red": 1.00, "green": 0.84, "blue": 0.96},
    "Cybersecurity":         {"red": 1.00, "green": 0.84, "blue": 0.84},
}

# Tab definitions: (tab_name, emoji, header_colour_rgb)
TABS = {
    "india":   ("🇮🇳 India Jobs",  {"red": 0.88, "green": 0.95, "blue": 0.88}),
    "global":  ("🌍 Global Jobs",  {"red": 0.85, "green": 0.90, "blue": 1.00}),
    "all":     ("📋 All Jobs",     {"red": 0.12, "green": 0.23, "blue": 0.37}),
}

DARK_HEADER  = {"red": 0.12, "green": 0.23, "blue": 0.37}
INDIA_HEADER = {"red": 0.13, "green": 0.55, "blue": 0.13}
GLOBAL_HEADER= {"red": 0.10, "green": 0.30, "blue": 0.60}


def _is_india(job: dict) -> bool:
    loc = (job.get("location") or "").lower()
    return any(kw in loc for kw in INDIA_KEYWORDS)


class SheetsManager:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._gc = None

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _connect(self):
        if self._gc:
            return
        method = os.getenv("GOOGLE_AUTH_METHOD", "service_account").lower()
        self._gc = self._connect_oauth() if method == "oauth" else self._connect_sa()

    def _connect_sa(self):
        f = self.cfg.GOOGLE_CREDENTIALS_FILE
        if not Path(f).exists():
            raise FileNotFoundError(f"credentials.json not found at '{f}'.")
        creds = Credentials.from_service_account_file(f, scopes=SCOPES)
        logger.info("  Google auth: service account")
        return gspread.authorize(creds)

    def _connect_oauth(self):
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials as OC
        from google.auth.transport.requests import Request

        token_file  = Path("oauth_token.json")
        client_file = Path(os.getenv("GOOGLE_OAUTH_CLIENT_FILE", "oauth_client.json"))
        creds = None

        if token_file.exists():
            try:
                creds = OC.from_authorized_user_file(str(token_file), SCOPES)
            except Exception:
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("  Google auth: token refreshed")
                except Exception:
                    creds = None
            if not creds:
                if not client_file.exists():
                    raise FileNotFoundError(f"oauth_client.json not found.")
                flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
                logger.info("  Opening browser for Google login …")
                creds = flow.run_local_server(port=0)
                logger.info("  OAuth login successful")
            token_file.write_text(creds.to_json())

        return gspread.authorize(creds)

    # ── Sheet access ──────────────────────────────────────────────────────────

    def _get_or_create_sheet(self):
        self._connect()
        try:
            sh = self._gc.open(self.cfg.GOOGLE_SHEET_NAME)
            logger.info(f"  Opened existing sheet: '{self.cfg.GOOGLE_SHEET_NAME}'")
        except gspread.SpreadsheetNotFound:
            sh = self._gc.create(self.cfg.GOOGLE_SHEET_NAME)
            logger.info(f"  Created new sheet: '{self.cfg.GOOGLE_SHEET_NAME}'")
            if self.cfg.GOOGLE_SHEET_EMAIL:
                try:
                    sh.share(self.cfg.GOOGLE_SHEET_EMAIL, perm_type="user", role="writer")
                except Exception as e:
                    logger.warning(f"  Could not share: {e}")
        # Remove default blank sheet
        try:
            sh.del_worksheet(sh.worksheet("Sheet1"))
        except Exception:
            pass
        return sh

    def _ensure_tab(self, sh, name: str, header_color: dict) -> gspread.Worksheet:
        try:
            return sh.worksheet(name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(name, rows=5000, cols=len(COLUMNS))
            ws.update("A1", [COLUMNS])
            self._format_header(ws, sh, header_color)
            return ws

    def _ensure_history_tab(self, sh):
        name = "🕐 Run History"
        try:
            return sh.worksheet(name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(name, rows=500, cols=6)
            ws.update("A1:F1", [["Run Timestamp", "India Jobs",
                                  "Global Jobs", "Total Added",
                                  "Total in Sheet", "Sources"]])
            ws.format("A1:F1", {"textFormat": {"bold": True},
                                 "backgroundColor": DARK_HEADER,
                                 "textFormat": {"bold": True,
                                                "foregroundColor": {"red":1,"green":1,"blue":1}}})
            return ws

    def _ensure_summary_tab(self, sh):
        name = "📊 Summary"
        try:
            return sh.worksheet(name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(name, rows=50, cols=5)
            return ws

    # ── Header formatting ─────────────────────────────────────────────────────

    def _format_header(self, ws, sh, bg_color: dict):
        sid  = ws._properties["sheetId"]
        reqs = [
            {"repeatCell": {
                "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {
                    "backgroundColor": bg_color,
                    "textFormat": {"bold": True,
                                   "foregroundColor": {"red":1,"green":1,"blue":1}},
                    "horizontalAlignment": "CENTER",
                }},
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }},
            {"updateSheetProperties": {
                "properties": {"sheetId": sid,
                               "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }},
        ]
        for i, w in enumerate([280,180,150,110,160,200,110,110,80,300,110]):
            reqs.append({"updateDimensionProperties": {
                "range": {"sheetId": sid, "dimension": "COLUMNS",
                          "startIndex": i, "endIndex": i+1},
                "properties": {"pixelSize": w},
                "fields": "pixelSize",
            }})
        sh.batch_update({"requests": reqs})

    # ── Upload ────────────────────────────────────────────────────────────────

    def upload(self, jobs: list[dict]) -> int:
        sh = self._get_or_create_sheet()

        # Ensure all tabs exist
        india_ws  = self._ensure_tab(sh, "🇮🇳 India Jobs",  INDIA_HEADER)
        global_ws = self._ensure_tab(sh, "🌍 Global Jobs", GLOBAL_HEADER)
        all_ws    = self._ensure_tab(sh, "📋 All Jobs",    DARK_HEADER)
        hist_ws   = self._ensure_history_tab(sh)
        summ_ws   = self._ensure_summary_tab(sh)

        # Load existing links per tab to prevent duplicates
        existing = {
            "india":  self._get_links(india_ws),
            "global": self._get_links(global_ws),
            "all":    self._get_links(all_ws),
        }

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        india_rows, global_rows, all_rows = [], [], []
        sources_seen = set()

        for j in jobs:
            link = j.get("apply_link", "").strip()
            row  = [
                j.get("title", ""),
                j.get("company", ""),
                j.get("location", ""),
                j.get("job_type", ""),
                j.get("category", ""),
                j.get("tags", ""),
                j.get("date_posted", ""),
                j.get("source", ""),
                link,
                j.get("summary", ""),
                now_str,
            ]
            sources_seen.add(j.get("source", ""))

            # Add to All Jobs tab
            if link not in existing["all"]:
                all_rows.append(row)
                existing["all"].add(link)

            # Add to India or Global tab
            if _is_india(j):
                if link not in existing["india"]:
                    india_rows.append(row)
                    existing["india"].add(link)
            else:
                if link not in existing["global"]:
                    global_rows.append(row)
                    existing["global"].add(link)

        # Append rows to each tab
        if india_rows:
            india_ws.append_rows(india_rows, value_input_option="USER_ENTERED")
            self._colour_rows(india_ws, sh, len(india_rows))
            logger.info(f"  🇮🇳 India: {len(india_rows)} new jobs")

        if global_rows:
            global_ws.append_rows(global_rows, value_input_option="USER_ENTERED")
            self._colour_rows(global_ws, sh, len(global_rows))
            logger.info(f"  🌍 Global: {len(global_rows)} new jobs")

        if all_rows:
            all_ws.append_rows(all_rows, value_input_option="USER_ENTERED")
            self._colour_rows(all_ws, sh, len(all_rows))

        total_added = len(all_rows)
        total_in_sheet = len(all_ws.get_all_values()) - 1

        # Update summary tab
        self._update_summary(summ_ws, sh, india_ws, global_ws, all_ws, now_str)

        # Log to history
        hist_ws.append_row([
            now_str,
            len(india_rows),
            len(global_rows),
            total_added,
            total_in_sheet,
            ", ".join(sorted(s for s in sources_seen if s)),
        ])

        return total_added

    # ── Summary dashboard ─────────────────────────────────────────────────────

    def _update_summary(self, ws, sh, india_ws, global_ws, all_ws, now_str):
        try:
            india_total  = max(0, len(india_ws.get_all_values()) - 1)
            global_total = max(0, len(global_ws.get_all_values()) - 1)
            all_total    = max(0, len(all_ws.get_all_values()) - 1)

            data = [
                ["📊 Global Tech Jobs — Summary Dashboard", "", ""],
                ["", "", ""],
                ["Section", "Total Jobs", "Last Updated"],
                ["🇮🇳 India Jobs",  india_total,  now_str],
                ["🌍 Global Jobs", global_total, now_str],
                ["📋 All Jobs",    all_total,    now_str],
                ["", "", ""],
                ["Pipeline Info", "", ""],
                ["Last run", now_str, ""],
                ["Dedup method", "Apply link matching", ""],
                ["AI backend", "Groq (Llama 3.3 70B)", ""],
            ]
            ws.clear()
            ws.update("A1", data)

            sid  = ws._properties["sheetId"]
            reqs = [
                # Title row
                {"repeatCell": {
                    "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {"userEnteredFormat": {
                        "backgroundColor": DARK_HEADER,
                        "textFormat": {"bold": True, "fontSize": 13,
                                       "foregroundColor": {"red":1,"green":1,"blue":1}},
                    }},
                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                }},
                # India row
                {"repeatCell": {
                    "range": {"sheetId": sid, "startRowIndex": 3, "endRowIndex": 4},
                    "cell": {"userEnteredFormat": {
                        "backgroundColor": {"red": 0.88, "green": 0.96, "blue": 0.88},
                    }},
                    "fields": "userEnteredFormat.backgroundColor",
                }},
                # Global row
                {"repeatCell": {
                    "range": {"sheetId": sid, "startRowIndex": 4, "endRowIndex": 5},
                    "cell": {"userEnteredFormat": {
                        "backgroundColor": {"red": 0.85, "green": 0.90, "blue": 1.00},
                    }},
                    "fields": "userEnteredFormat.backgroundColor",
                }},
                # Col widths
                {"updateDimensionProperties": {
                    "range": {"sheetId": sid, "dimension": "COLUMNS",
                              "startIndex": 0, "endIndex": 1},
                    "properties": {"pixelSize": 220}, "fields": "pixelSize",
                }},
                {"updateDimensionProperties": {
                    "range": {"sheetId": sid, "dimension": "COLUMNS",
                              "startIndex": 1, "endIndex": 2},
                    "properties": {"pixelSize": 120}, "fields": "pixelSize",
                }},
                {"updateDimensionProperties": {
                    "range": {"sheetId": sid, "dimension": "COLUMNS",
                              "startIndex": 2, "endIndex": 3},
                    "properties": {"pixelSize": 200}, "fields": "pixelSize",
                }},
            ]
            sh.batch_update({"requests": reqs})
        except Exception as e:
            logger.debug(f"Summary update skipped: {e}")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_links(self, ws: gspread.Worksheet) -> set:
        try:
            col_idx = COLUMNS.index("Apply Link") + 1
            return set(v.strip() for v in ws.col_values(col_idx)[1:] if v.strip())
        except Exception:
            return set()

    def _colour_rows(self, ws, sh, n_new: int):
        try:
            all_rows = ws.get_all_values()
            sid      = ws._properties["sheetId"]
            cat_col  = COLUMNS.index("Category")
            start    = len(all_rows) - n_new
            reqs = []
            for i, row in enumerate(all_rows[start:], start=start):
                cat   = row[cat_col] if len(row) > cat_col else ""
                color = CATEGORY_COLOURS.get(cat)
                if color:
                    reqs.append({"repeatCell": {
                        "range": {"sheetId": sid,
                                  "startRowIndex": i, "endRowIndex": i+1},
                        "cell": {"userEnteredFormat": {"backgroundColor": color}},
                        "fields": "userEnteredFormat.backgroundColor",
                    }})
            if reqs:
                sh.batch_update({"requests": reqs})
        except Exception as e:
            logger.debug(f"Colour rows skipped: {e}")
