#!/usr/bin/env python3
"""
Global Tech Jobs & Internships Pipeline
========================================
Fetches jobs from public APIs → Claude AI filters/classifies → Google Sheets

Usage:
    python main.py                  # Run once
    python main.py --schedule       # Run on cron schedule
    python main.py --filter remote  # Remote-only roles
    python main.py --filter intern  # Internships only
    python main.py --notify         # Enable Telegram notifications
"""

import argparse
import logging
import sys
import time

import schedule

from config import Config
from collectors import JobCollector
from claude_processor import ClaudeProcessor
from sheets_manager import SheetsManager
from notifier import Notifier
from utils import setup_logging, load_seen_ids, save_seen_ids

logger = logging.getLogger(__name__)


def run_pipeline(cfg: Config, job_filter: str | None = None, notify: bool = False):
    """Full pipeline: collect → process → upload."""

    logger.info("=" * 60)
    logger.info("Pipeline run started")

    seen_ids = load_seen_ids(cfg.SEEN_IDS_FILE)
    notifier  = Notifier(cfg) if notify else None

    # ── 1. Collect ────────────────────────────────────────────────────────
    logger.info("Phase 1: Collecting jobs from APIs …")
    collector = JobCollector(cfg)
    raw_jobs  = collector.collect_all()
    logger.info(f"  Collected {len(raw_jobs)} raw listings")

    if not raw_jobs:
        logger.warning("No jobs collected. Check API keys / network.")
        return

    # ── 2. Deduplicate against history ───────────────────────────────────
    new_jobs = [j for j in raw_jobs if j["id"] not in seen_ids]
    logger.info(f"  {len(new_jobs)} new (after dedup against {len(seen_ids)} seen)")

    if not new_jobs:
        logger.info("No new jobs to process. All done.")
        return

    # ── 3. Claude: filter, classify, clean ───────────────────────────────
    logger.info("Phase 2: Claude AI processing …")
    processor = ClaudeProcessor(cfg)
    processed = processor.process_batch(new_jobs)
    logger.info(f"  {len(processed)} passed domain filter")

    # ── 4. Optional user-side filter ────────────────────────────────────
    if job_filter == "remote":
        processed = [j for j in processed
                     if "remote" in (j.get("location") or "").lower()]
        logger.info(f"  → {len(processed)} after remote filter")
    elif job_filter == "intern":
        processed = [j for j in processed
                     if j.get("job_type", "").lower() == "internship"]
        logger.info(f"  → {len(processed)} after internship filter")

    if not processed:
        logger.info("No qualifying jobs after filtering.")
        return

    # ── 5. Google Sheets upload ───────────────────────────────────────────
    logger.info("Phase 3: Uploading to Google Sheets …")
    sheets = SheetsManager(cfg)
    added  = sheets.upload(processed)
    logger.info(f"  Uploaded {added} new rows")

    # ── 6. Persist seen IDs ───────────────────────────────────────────────
    for j in processed:
        seen_ids.add(j["id"])
    save_seen_ids(cfg.SEEN_IDS_FILE, seen_ids)

    # ── 7. Notify ────────────────────────────────────────────────────────
    if notifier and added > 0:
        notifier.send(processed[:5], added)   # preview of top 5

    logger.info(f"Pipeline complete — {added} jobs added to sheet.")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Global Tech Jobs Pipeline")
    parser.add_argument("--schedule", action="store_true",
                        help="Run on a recurring schedule (default: every 6 hours)")
    parser.add_argument("--filter", choices=["remote", "intern"],
                        help="Optional post-filter: remote or internship only")
    parser.add_argument("--notify", action="store_true",
                        help="Send Telegram notification after each run")
    parser.add_argument("--interval", type=int, default=6,
                        help="Schedule interval in hours (default: 6)")
    args = parser.parse_args()

    setup_logging()
    cfg = Config()

    if args.schedule:
        logger.info(f"Scheduler mode: every {args.interval} hour(s)")
        run_pipeline(cfg, args.filter, args.notify)          # immediate first run
        schedule.every(args.interval).hours.do(
            run_pipeline, cfg, args.filter, args.notify
        )
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_pipeline(cfg, args.filter, args.notify)


if __name__ == "__main__":
    main()
