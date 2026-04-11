"""
claude_processor.py — AI filtering with 90% internship priority.

Supported backends (set AI_BACKEND in .env):
  groq       — console.groq.com       (free)
  gemini     — aistudio.google.com    (free)
  openrouter — openrouter.ai          (free tier)
  claude     — console.anthropic.com  (paid)
"""

import json
import logging
import re
import time

import httpx

from config import Config

logger = logging.getLogger(__name__)


class ClaudeProcessor:
    def __init__(self, cfg: Config):
        self.cfg     = cfg
        self.client  = httpx.Client(timeout=90)
        self.backend = cfg.AI_BACKEND.lower()

    def process_batch(self, jobs: list[dict]) -> list[dict]:
        key = self.cfg.AI_API_KEY
        if not key or "your-key-here" in key:
            logger.error(
                f"AI_API_KEY is missing in .env. Backend: {self.backend}\n"
                f"  Groq (free)   → https://console.groq.com\n"
                f"  Gemini (free) → https://aistudio.google.com"
            )
            return []

        all_processed: list[dict] = []
        chunk_size = self.cfg.CLAUDE_BATCH_SIZE

        for i in range(0, len(jobs), chunk_size):
            chunk = jobs[i: i + chunk_size]
            logger.info(f"  AI ({self.backend}): chunk {i//chunk_size+1} ({len(chunk)} jobs) …")
            try:
                result = self._call_ai(chunk)
                all_processed.extend(result)
            except Exception as e:
                logger.warning(f"  AI chunk error: {e}")
            time.sleep(self.cfg.CHUNK_SLEEP)

        return all_processed

    def _build_prompt(self, jobs: list[dict]) -> tuple[str, str]:
        system = f"""You are a job data quality engineer specialising in INTERNSHIPS and entry-level tech roles.

PRIORITY RULE: You must accept and keep internships (90% of output should be internships).
Only reject a job if it is completely unrelated to tech (e.g. sales, HR, marketing, cooking).

Your tasks:
1. FILTER — keep jobs in these tech domains:
   {json.dumps(self.cfg.TARGET_DOMAINS)}

   INTERNSHIP PRIORITY: If the title contains intern/internship/trainee/fresher/
   entry-level/junior/co-op/placement/fellowship AND it is tech-related → ALWAYS KEEP IT.
   For non-internship roles, only keep if clearly senior tech engineering roles.

2. CLASSIFY — assign a "category" from:
   {json.dumps(self.cfg.ROLE_CATEGORIES)}

3. CLEAN —
   - Normalise location: use "Remote", "Remote (India)", "Remote (Global)" etc.
   - Normalise job_type: MUST be one of:
     Internship | Full-time | Part-time | Contract | Freelance
   - If title has intern/internship/trainee → set job_type to "Internship"
   - Title-case the job title
   - Strip HTML from description

4. SUMMARISE — 1-2 sentence summary (or "" if no description)

5. DEDUPLICATE — same role at same company → keep only first

Return ONLY a valid JSON array with these exact keys per job:
  id, title, company, location, job_type, category, apply_link, date_posted, source, tags, summary

No markdown fences. No explanation. Pure JSON array only."""

        payload = [
            {k: v for k, v in j.items()
             if k in ("id","title","company","location","job_type",
                       "apply_link","date_posted","source","tags","description")}
            for j in jobs
        ]
        return system, json.dumps(payload, ensure_ascii=False)

    def _call_ai(self, jobs: list[dict]) -> list[dict]:
        system, user = self._build_prompt(jobs)
        dispatch = {
            "groq":       self._call_groq,
            "gemini":     self._call_gemini,
            "openrouter": self._call_openrouter,
            "claude":     self._call_claude,
        }
        fn = dispatch.get(self.backend)
        if not fn:
            raise ValueError(f"Unknown AI_BACKEND: {self.backend}")
        raw = fn(system, user)
        return self._parse(raw)

    def _call_groq(self, system, user) -> str:
        r = self.client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json={
                "model":       self.cfg.AI_MODEL or "llama-3.3-70b-versatile",
                "messages":    [{"role":"system","content":system},
                                {"role":"user","content":user}],
                "max_tokens":  4000,
                "temperature": 0,
            },
            headers={"Authorization": f"Bearer {self.cfg.AI_API_KEY}",
                     "Content-Type": "application/json"},
        )
        if r.status_code == 429:
            wait = 40
            logger.warning(f"Groq rate limit — waiting {wait}s …")
            time.sleep(wait)
            return self._call_groq(system, user)
        if r.status_code != 200:
            logger.error(f"Groq error {r.status_code}: {r.text[:200]}")
            return "[]"
        return r.json()["choices"][0]["message"]["content"]

    def _call_gemini(self, system, user) -> str:
        model = self.cfg.AI_MODEL or "gemini-2.0-flash"
        r = self.client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": self.cfg.AI_API_KEY},
            json={
                "system_instruction": {"parts": [{"text": system}]},
                "contents": [{"parts": [{"text": user}]}],
                "generationConfig": {"temperature": 0, "maxOutputTokens": 4000},
            },
        )
        if r.status_code != 200:
            logger.error(f"Gemini error {r.status_code}: {r.text[:200]}")
            return "[]"
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openrouter(self, system, user) -> str:
        r = self.client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model":      self.cfg.AI_MODEL or "meta-llama/llama-3.3-70b-instruct:free",
                "messages":   [{"role":"system","content":system},
                               {"role":"user","content":user}],
                "max_tokens": 4000,
            },
            headers={"Authorization": f"Bearer {self.cfg.AI_API_KEY}",
                     "Content-Type": "application/json"},
        )
        if r.status_code != 200:
            logger.error(f"OpenRouter error {r.status_code}: {r.text[:200]}")
            return "[]"
        return r.json()["choices"][0]["message"]["content"]

    def _call_claude(self, system, user) -> str:
        r = self.client.post(
            "https://api.anthropic.com/v1/messages",
            json={
                "model":      self.cfg.AI_MODEL or "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "system":     system,
                "messages":   [{"role":"user","content":user}],
            },
            headers={
                "x-api-key":         self.cfg.AI_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type":      "application/json",
            },
        )
        if r.status_code == 400:
            logger.error(f"Claude error: {r.json().get('error',{}).get('message')}")
            return "[]"
        r.raise_for_status()
        return "".join(b["text"] for b in r.json()["content"] if b.get("type")=="text")

    def _parse(self, raw: str) -> list[dict]:
        raw   = re.sub(r"```(?:json)?|```", "", raw).strip()
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            logger.warning("AI returned no parsable JSON.")
            return []
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}")
            return []

    def __del__(self):
        try:
            self.client.close()
        except Exception:
            pass
