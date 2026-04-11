"""
collectors.py — fetches raw job listings with 90% internship focus.

Sources:
  • Remotive       — remotive.com/api  (free, no key)
  • Arbeitnow      — arbeitnow.com/api (free, no key)
  • FindWork       — findwork.dev/api  (free key optional)
  • The Muse       — themuse.com/api   (free, no key)
"""

import hashlib
import logging
import time
from datetime import datetime, timezone

import httpx

from config import Config

logger = logging.getLogger(__name__)

# Internship-first keywords — used for pre-filtering
INTERNSHIP_KEYWORDS = {
    "intern", "internship", "trainee", "apprentice", "graduate program",
    "graduate trainee", "fresher", "entry level", "entry-level",
    "junior", "associate", "student", "co-op", "coop", "placement",
    "summer program", "winter program", "fellowship", "bootcamp",
}

# Tech keywords — must also match one of these
TECH_KEYWORDS = {
    "software", "developer", "engineer", "engineering", "frontend",
    "backend", "fullstack", "full-stack", "full stack", "web dev",
    "machine learning", "artificial intelligence", " ai ", "ml ",
    "data scientist", "data engineer", "quantum", "devops", "cloud",
    "python", "javascript", "typescript", "react", "vue", "angular",
    "java", "golang", "rust", "c++", "kubernetes", "docker", "aws",
    "swe", "sde", "tech", "coding", "programming", "computer science",
    "it ", "information technology", "cyber", "security",
}


def _make_id(*parts) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def _is_internship(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in INTERNSHIP_KEYWORDS)


def _is_tech(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in TECH_KEYWORDS)


def _is_relevant(title: str, description: str = "") -> bool:
    combined = (title + " " + description).lower()
    return _is_tech(combined)


def _fmt_date(raw) -> str:
    if not raw:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw = str(raw)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(raw[:19], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw[:10] if len(raw) >= 10 else raw


def _normalize_type(raw: str) -> str:
    low = raw.lower()
    if any(k in low for k in ["intern", "trainee", "apprentice",
                                "fresher", "co-op", "placement", "fellowship"]):
        return "Internship"
    if "contract" in low:  return "Contract"
    if "part" in low:      return "Part-time"
    if "freelance" in low: return "Freelance"
    return "Full-time"


def _truncate(text: str, limit: int) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", text)
    text = " ".join(text.split())
    return text[:limit] + ("…" if len(text) > limit else "")


class JobCollector:
    def __init__(self, cfg: Config):
        self.cfg    = cfg
        self.client = httpx.Client(
            timeout=25,
            headers={"User-Agent": "TechInternshipPipeline/3.0 (educational project)"},
            follow_redirects=True,
        )

    def collect_all(self) -> list[dict]:
        all_jobs: list[dict] = []
        sources = [
            ("Remotive",  self._fetch_remotive),
            ("Arbeitnow", self._fetch_arbeitnow),
            ("The Muse",  self._fetch_muse),
        ]
        if self.cfg.FINDWORK_API_KEY:
            sources.append(("FindWork", self._fetch_findwork))

        for name, fn in sources:
            try:
                jobs = fn()
                logger.info(f"  {name}: {len(jobs)} listings")
                all_jobs.extend(jobs)
            except Exception as e:
                logger.warning(f"  {name} failed: {e}")
            time.sleep(0.5)

        # Deduplicate within batch
        seen, unique = set(), []
        for j in all_jobs:
            if j["id"] not in seen:
                seen.add(j["id"])
                unique.append(j)

        # Sort: internships first (90% priority)
        internships = [j for j in unique if j["job_type"] == "Internship"]
        others      = [j for j in unique if j["job_type"] != "Internship"]
        logger.info(f"  Pre-filter: {len(internships)} internships, {len(others)} other roles")

        # Return internships first, then a small number of other tech roles
        max_others = max(1, len(internships) // 9)   # ~10% non-internship
        return internships + others[:max_others]

    # ── Remotive ──────────────────────────────────────────────────────────────
    def _fetch_remotive(self) -> list[dict]:
        jobs: list[dict] = []

        # Dedicated internship search
        internship_searches = [
            {"search": "intern software"},
            {"search": "intern developer"},
            {"search": "intern machine learning"},
            {"search": "intern data"},
            {"search": "intern frontend"},
            {"search": "intern backend"},
            {"search": "intern python"},
            {"search": "internship engineering"},
        ]

        for params in internship_searches:
            try:
                r = self.client.get(self.cfg.REMOTIVE_API_URL,
                                    params={**params, "limit": 20})
                r.raise_for_status()
                for j in r.json().get("jobs", []):
                    title = j.get("title", "")
                    if not _is_relevant(title, j.get("description", "")):
                        continue
                    jobs.append(self._remotive_job(j))
            except Exception as e:
                logger.debug(f"Remotive search {params}: {e}")
            time.sleep(0.3)

        # Also fetch by category for general tech roles
        for cat in ["software-dev", "data", "devops-sysadmin"]:
            try:
                r = self.client.get(self.cfg.REMOTIVE_API_URL,
                                    params={"category": cat, "limit": 30})
                r.raise_for_status()
                for j in r.json().get("jobs", []):
                    title = j.get("title", "")
                    if _is_internship(title) and _is_relevant(title):
                        jobs.append(self._remotive_job(j))
            except Exception as e:
                logger.debug(f"Remotive cat {cat}: {e}")

        return jobs

    def _remotive_job(self, j: dict) -> dict:
        title = j.get("title", "")
        return {
            "id":          _make_id("remotive", str(j.get("id", ""))),
            "title":       title,
            "company":     j.get("company_name", ""),
            "location":    j.get("candidate_required_location") or "Remote",
            "job_type":    _normalize_type(j.get("job_type", "") + " " + title),
            "apply_link":  j.get("url", ""),
            "date_posted": _fmt_date(j.get("publication_date")),
            "description": _truncate(j.get("description", ""), 500),
            "source":      "Remotive",
            "tags":        ", ".join(j.get("tags", [])[:8]),
        }

    # ── Arbeitnow ─────────────────────────────────────────────────────────────
    def _fetch_arbeitnow(self) -> list[dict]:
        jobs: list[dict] = []
        for page in range(1, 6):   # fetch more pages
            try:
                r = self.client.get(self.cfg.ARBEITNOW_API_URL,
                                    params={"page": page})
                r.raise_for_status()
                data = r.json().get("data", [])
                if not data:
                    break
                for j in data:
                    title    = j.get("title", "")
                    desc     = j.get("description", "")
                    is_intern = _is_internship(title + " " + desc)
                    is_tech   = _is_relevant(title, desc)

                    # Accept internships OR tech roles
                    if not is_tech:
                        continue

                    loc_parts = []
                    if j.get("remote"):      loc_parts.append("Remote")
                    if j.get("location"):    loc_parts.append(j["location"])

                    raw_types = j.get("job_types", [""])
                    raw_type  = raw_types[0] if raw_types else ""
                    job_type  = _normalize_type(raw_type + " " + title)

                    jobs.append({
                        "id":          _make_id("arbeitnow", j.get("slug", title)),
                        "title":       title,
                        "company":     j.get("company_name", ""),
                        "location":    " / ".join(loc_parts) or "Not specified",
                        "job_type":    job_type,
                        "apply_link":  j.get("url", ""),
                        "date_posted": _fmt_date(str(j.get("created_at", ""))),
                        "description": _truncate(desc, 500),
                        "source":      "Arbeitnow",
                        "tags":        ", ".join(j.get("tags", [])[:8]),
                    })
            except Exception as e:
                logger.debug(f"Arbeitnow page {page}: {e}")
                break
        return jobs

    # ── FindWork ──────────────────────────────────────────────────────────────
    def _fetch_findwork(self) -> list[dict]:
        jobs: list[dict] = []
        searches = [
            "software intern", "developer intern", "ml intern",
            "data intern", "frontend intern", "backend intern",
        ]
        for kw in searches:
            try:
                r = self.client.get(
                    self.cfg.FINDWORK_API_URL,
                    params={"search": kw, "sort_by": "date"},
                    headers={"Authorization": f"Token {self.cfg.FINDWORK_API_KEY}"},
                )
                r.raise_for_status()
                for j in r.json().get("results", []):
                    title = j.get("role", "")
                    jobs.append({
                        "id":          _make_id("findwork", str(j.get("id", ""))),
                        "title":       title,
                        "company":     j.get("company_name", ""),
                        "location":    "Remote" if j.get("remote") else j.get("location", ""),
                        "job_type":    _normalize_type(title),
                        "apply_link":  j.get("url", ""),
                        "date_posted": _fmt_date(j.get("date_posted")),
                        "description": _truncate(j.get("text", ""), 500),
                        "source":      "FindWork",
                        "tags":        ", ".join(j.get("keywords", [])[:8]),
                    })
                time.sleep(0.3)
            except Exception as e:
                logger.debug(f"FindWork '{kw}': {e}")
        return jobs

    # ── The Muse ──────────────────────────────────────────────────────────────
    def _fetch_muse(self) -> list[dict]:
        jobs: list[dict] = []
        searches = [
            {"category": "Software Engineer", "level": "Internship"},
            {"category": "Engineer",          "level": "Internship"},
            {"category": "Data Science",      "level": "Internship"},
            {"category": "IT & Security",     "level": "Internship"},
            {"category": "Software Engineer", "level": "Entry Level"},
            {"category": "Engineer",          "level": "Entry Level"},
        ]
        for params in searches:
            try:
                r = self.client.get(self.cfg.MUSE_API_URL,
                                    params={**params, "page": 1,
                                            "descending": "true"})
                r.raise_for_status()
                for j in r.json().get("results", []):
                    title  = j.get("name", "")
                    levels = [lv.get("name", "") for lv in j.get("levels", [])]
                    locs   = [lo.get("name", "") for lo in j.get("locations", [])]
                    desc   = j.get("contents", "")
                    jobs.append({
                        "id":          _make_id("muse", str(j.get("id", ""))),
                        "title":       title,
                        "company":     j.get("company", {}).get("name", ""),
                        "location":    ", ".join(locs) or "Not specified",
                        "job_type":    _normalize_type(" ".join(levels) + " " + title),
                        "apply_link":  j.get("refs", {}).get("landing_page", ""),
                        "date_posted": _fmt_date(j.get("publication_date")),
                        "description": _truncate(desc, 500),
                        "source":      "The Muse",
                        "tags":        ", ".join(levels[:4]),
                    })
                time.sleep(0.3)
            except Exception as e:
                logger.debug(f"The Muse {params}: {e}")
        return jobs

    def __del__(self):
        try:
            self.client.close()
        except Exception:
            pass
