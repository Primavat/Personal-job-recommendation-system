"""
notifier.py — optional Telegram notifications after each pipeline run.
"""

import logging
import httpx

from config import Config

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, cfg: Config):
        self.cfg    = cfg
        self.active = bool(cfg.TELEGRAM_BOT_TOKEN and cfg.TELEGRAM_CHAT_ID)
        if not self.active:
            logger.info("Telegram notifier disabled (no token/chat_id).")

    def send(self, top_jobs: list[dict], total_added: int):
        if not self.active:
            return
        try:
            lines = [
                f"🤖 *Tech Jobs Pipeline*",
                f"✅ *{total_added} new listings added*\n",
                "🔥 *Top picks:*",
            ]
            for j in top_jobs[:5]:
                link = j.get("apply_link", "")
                title  = _esc(j.get("title", "N/A"))
                co     = _esc(j.get("company", "N/A"))
                cat    = _esc(j.get("category", ""))
                jtype  = _esc(j.get("job_type", ""))
                loc    = _esc(j.get("location", ""))
                line   = (
                    f"• *{title}* @ {co}\n"
                    f"  _{cat}_ · {jtype} · {loc}"
                )
                if link:
                    line += f"\n  [Apply →]({link})"
                lines.append(line)

            text = "\n".join(lines)
            url  = (f"https://api.telegram.org/bot{self.cfg.TELEGRAM_BOT_TOKEN}"
                    f"/sendMessage")
            httpx.post(url, json={
                "chat_id":    self.cfg.TELEGRAM_CHAT_ID,
                "text":       text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }, timeout=10)
            logger.info("Telegram notification sent.")
        except Exception as e:
            logger.warning(f"Telegram notification failed: {e}")


def _esc(text: str) -> str:
    """Escape Markdown special characters."""
    for ch in r"_*[]()~`>#+-=|{}.!":
        text = text.replace(ch, f"\\{ch}")
    return text
