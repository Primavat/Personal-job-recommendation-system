"""
collectors.py — fetches raw job listings with 80% India focus.

Sources (India-first):
  • Adzuna India   — api.adzuna.com/v1/api/jobs/in  (free, needs App ID + Key)
  • JSearch        — jsearch.p.rapidapi.com          (free tier, scrapes Naukri/LinkedIn India)
  • Remotive       — remotive.com/api                (free, no key — remote/global)
  • Arbeitnow      — arbeitnow.com/api               (free, no key — global fallback)
  • The Muse       — themuse.com/api                 (free, no key — global fallback)
  • FindWork       — findwork.dev/api                (free key optional — global fallback)

80/20 Strategy:
  India sources (Adzuna IN + JSearch IN) are fetched first and prioritized.
  Global sources fill the remaining ~20% quota.
"""

import hashlib
import logging
import time
from datetime import datetime, timezone

import httpx

from config import Config

logger = logging.getLogger(__name__)

# ── Keyword filters ───────────────────────────────────────────────────────────

INTERNSHIP_KEYWORDS = {
    "intern", "internship", "trainee", "apprentice", "graduate program",
    "graduate trainee", "fresher", "entry level", "entry-level",
    "junior", "associate", "student", "co-op", "coop", "placement",
    "summer program", "winter program", "fellowship", "bootcamp",
}

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

# Major Indian cities — used to tag/prioritize India jobs
INDIA_LOCATIONS = {
    "india", "bangalore", "bengaluru", "mumbai", "delhi", "hyderabad",
    "chennai", "pune", "kolkata", "ahmedabad", "noida", "gurgaon",
    "gurugram", "remote india", "india remote", "pan india",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    return _is_tech((title + " " + description).lower())


def _is_india(location: str) -> bool:
    """Return True if the location string refers to India."""
    low = location.lower()
    return any(city in low for city in INDIA_LOCATIONS)


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
    if "contract" in low:   return "Contract"
    if "part" in low:       return "Part-time"
    if "freelance" in low:  return "Freelance"
    return "Full-time"


def _truncate(text: str, limit: int) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", text)
    text = " ".join(text.split())
    return text[:limit] + ("…" if len(text) > limit else "")


# ── Collector ─────────────────────────────────────────────────────────────────

class JobCollector:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.client = httpx.Client(
            timeout=25,
            headers={"User-Agent": "TechJobPipeline/4.0 (educational project)"},
            follow_redirects=True,
        )

    def collect_all(self) -> list[dict]:
        india_jobs: list[dict] = []
        global_jobs: list[dict] = []

        # ── India-first sources ───────────────────────────────────────────────
        india_sources = []

        if self.cfg.ADZUNA_APP_ID and self.cfg.ADZUNA_APP_KEY:
            india_sources.append(("Adzuna India", self._fetch_adzuna_india))
        else:
            logger.warning("Adzuna credentials missing — skipping Adzuna India source. "
                           "Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env")

        if self.cfg.JSEARCH_API_KEY:
            india_sources.append(("JSearch India", self._fetch_jsearch_india))
        else:
            logger.warning("JSearch API key missing — skipping JSearch source. "
                           "Set JSEARCH_API_KEY in your .env (free tier at rapidapi.com)")

        for name, fn in india_sources:
            try:
                jobs = fn()
                logger.info(f"  {name}: {len(jobs)} listings")
                india_jobs.extend(jobs)
            except Exception as e:
                logger.warning(f"  {name} failed: {e}")
            time.sleep(0.5)

        # ── Global fallback sources ───────────────────────────────────────────
        global_sources = [
            ("Remotive",  self._fetch_remotive),
            ("Arbeitnow", self._fetch_arbeitnow),
            ("The Muse",  self._fetch_muse),
        ]
        if self.cfg.FINDWORK_API_KEY:
            global_sources.append(("FindWork", self._fetch_findwork))

        for name, fn in global_sources:
            try:
                jobs = fn()
                logger.info(f"  {name}: {len(jobs)} listings")
                global_jobs.extend(jobs)
            except Exception as e:
                logger.warning(f"  {name} failed: {e}")
            time.sleep(0.5)

        # ── Deduplicate each pool separately ─────────────────────────────────
        india_jobs  = _dedup(india_jobs)
        global_jobs = _dedup(global_jobs)

        # ── 80/20 merge ───────────────────────────────────────────────────────
        # Target: 80% India, 20% global (by count)
        # If India pool is large enough, cap globals at 25% of India count.
        # If India pool is small, still include all India + fill with globals.
        india_count  = len(india_jobs)
        global_quota = max(5, india_count // 4)   # 25% of india = ~20% of total
        merged = india_jobs + global_jobs[:global_quota]

        # Final dedup across both pools (same job might appear in both)
        merged = _dedup(merged)

        # Sort: internships first within each group
        internships = [j for j in merged if j["job_type"] == "Internship"]
        others      = [j for j in merged if j["job_type"] != "Internship"]

        india_ratio = india_count / max(len(merged), 1) * 100
        logger.info(
            f"  Final pool: {len(merged)} jobs | "
            f"India: {india_count} ({india_ratio:.0f}%) | "
            f"Global: {len(merged) - india_count} | "
            f"Internships: {len(internships)}"
        )

        return internships + others

    # ── 🇮🇳 Adzuna India ─────────────────────────────────────────────────────
    # Free API — register at https://developer.adzuna.com/
    # Gives 250 requests/day on free tier. Covers India jobs well.
    # Set in .env:  ADZUNA_APP_ID=xxx  ADZUNA_APP_KEY=yyy

    def _fetch_adzuna_india(self) -> list[dict]:
        """
        Fetch tech jobs from Adzuna's India endpoint.
        /v1/api/jobs/in/search/{page} — 'in' is the country code for India.
        """
        jobs: list[dict] = []
        searches = [
            "software engineer",
            "software developer",
            "python developer",
            "react developer",
            "data scientist",
            "machine learning engineer",
            "devops engineer",
            "backend developer",
            "frontend developer",
            "java developer",
            "software intern",
            "developer intern",
            "fresher software",
            "entry level software",
        ]

        base_url = "https://api.adzuna.com/v1/api/jobs/in/search"

        for query in searches:
            for page in range(1, 3):   # 2 pages per query
                try:
                    r = self.client.get(
                        f"{base_url}/{page}",
                        params={
                            "app_id":        self.cfg.ADZUNA_APP_ID,
                            "app_key":       self.cfg.ADZUNA_APP_KEY,
                            "what":          query,
                            "results_per_page": 20,
                            "sort_by":       "date",
                            "content-type":  "application/json",
                        },
                    )
                    r.raise_for_status()
                    for j in r.json().get("results", []):
                        title = j.get("title", "")
                        desc  = j.get("description", "")
                        if not _is_relevant(title, desc):
                            continue

                        location = (
                            j.get("location", {}).get("display_name", "India")
                            or "India"
                        )
                        # Ensure India tag even if Adzuna returns city only
                        if not _is_india(location):
                            location = f"{location}, India"

                        jobs.append({
                            "id":          _make_id("adzuna_in", str(j.get("id", ""))),
                            "title":       title,
                            "company":     j.get("company", {}).get("display_name", ""),
                            "location":    location,
                            "job_type":    _normalize_type(
                                               j.get("contract_type", "") + " " +
                                               j.get("contract_time", "") + " " + title
                                           ),
                            "apply_link":  j.get("redirect_url", ""),
                            "date_posted": _fmt_date(j.get("created")),
                            "description": _truncate(desc, 500),
                            "source":      "Adzuna India",
                            "tags":        "",
                        })
                    time.sleep(0.4)
                except Exception as e:
                    logger.debug(f"Adzuna India '{query}' page {page}: {e}")
                    break   # stop paging on error for this query

        return jobs

    # ── 🇮🇳 JSearch (Naukri/LinkedIn India scraper) ───────────────────────────
    # Free tier: 200 requests/month — https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
    # Pulls from Naukri, LinkedIn, Glassdoor India.
    # Set in .env:  JSEARCH_API_KEY=xxx

    def _fetch_jsearch_india(self) -> list[dict]:
        """
        Fetch India jobs via JSearch RapidAPI (aggregates Naukri, LinkedIn, Indeed India).
        """
        jobs: list[dict] = []
        queries = [
            "software engineer in India",
            "software developer Bangalore",
            "python developer India",
            "react developer India",
            "data scientist India",
            "machine learning India",
            "software intern India",
            "fresher developer India",
            "entry level software engineer India",
            "devops engineer India",
            "java developer India",
            "backend developer Hyderabad",
            "frontend developer Pune",
            "full stack developer India",
        ]

        headers = {
            "X-RapidAPI-Key":  self.cfg.JSEARCH_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }

        for query in queries:
            try:
                r = self.client.get(
                    "https://jsearch.p.rapidapi.com/search",
                    params={
                        "query":               query,
                        "page":                "1",
                        "num_pages":           "2",
                        "date_posted":         "month",
                        "employment_types":    "FULLTIME,INTERN,CONTRACTOR",
                    },
                    headers=headers,
                )
                r.raise_for_status()
                for j in r.json().get("data", []):
                    title = j.get("job_title", "")
                    desc  = j.get("job_description", "")
                    if not _is_relevant(title, desc):
                        continue

                    city    = j.get("job_city", "")
                    country = j.get("job_country", "")
                    state   = j.get("job_state", "")
                    is_remote = j.get("job_is_remote", False)

                    if is_remote:
                        location = "Remote, India"
                    elif city:
                        location = f"{city}, {state or country or 'India'}".strip(", ")
                        if not _is_india(location):
                            continue   # skip non-India JSearch results
                    else:
                        location = "India"

                    emp_type = j.get("job_employment_type", "")
                    jobs.append({
                        "id":          _make_id("jsearch", str(j.get("job_id", ""))),
                        "title":       title,
                        "company":     j.get("employer_name", ""),
                        "location":    location,
                        "job_type":    _normalize_type(emp_type + " " + title),
                        "apply_link":  j.get("job_apply_link", ""),
                        "date_posted": _fmt_date(
                                           j.get("job_posted_at_datetime_utc") or
                                           j.get("job_offer_expiration_datetime_utc")
                                       ),
                        "description": _truncate(desc, 500),
                        "source":      "JSearch (Naukri/LinkedIn)",
                        "tags":        ", ".join(
                                           (j.get("job_required_skills") or [])[:8]
                                       ),
                    })
                time.sleep(0.4)
            except Exception as e:
                logger.debug(f"JSearch '{query}': {e}")

        return jobs

    # ── Remotive (global remote — kept as top-up) ─────────────────────────────
    def _fetch_remotive(self) -> list[dict]:
        jobs: list[dict] = []
        searches = [
            {"search": "intern software"},
            {"search": "intern developer"},
            {"search": "intern machine learning"},
            {"search": "intern data"},
            {"search": "intern frontend"},
            {"search": "intern backend"},
            {"search": "intern python"},
            {"search": "internship engineering"},
        ]
        for params in searches:
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

    # ── Arbeitnow (global fallback) ───────────────────────────────────────────
    def _fetch_arbeitnow(self) -> list[dict]:
        jobs: list[dict] = []
        for page in range(1, 4):   # reduced pages since it's now just a fallback
            try:
                r = self.client.get(self.cfg.ARBEITNOW_API_URL,
                                    params={"page": page})
                r.raise_for_status()
                data = r.json().get("data", [])
                if not data:
                    break
                for j in data:
                    title = j.get("title", "")
                    desc  = j.get("description", "")
                    if not _is_relevant(title, desc):
                        continue
                    loc_parts = []
                    if j.get("remote"):   loc_parts.append("Remote")
                    if j.get("location"): loc_parts.append(j["location"])
                    raw_types = j.get("job_types", [""])
                    raw_type  = raw_types[0] if raw_types else ""
                    jobs.append({
                        "id":          _make_id("arbeitnow", j.get("slug", title)),
                        "title":       title,
                        "company":     j.get("company_name", ""),
                        "location":    " / ".join(loc_parts) or "Not specified",
                        "job_type":    _normalize_type(raw_type + " " + title),
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

    # ── FindWork (global fallback) ────────────────────────────────────────────
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

    # ── The Muse (global fallback) ────────────────────────────────────────────
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
                                    params={**params, "page": 1, "descending": "true"})
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


# ── Utility ───────────────────────────────────────────────────────────────────

def _dedup(jobs: list[dict]) -> list[dict]:
    """Remove duplicate job IDs, preserving order."""
    seen, unique = set(), []
    for j in jobs:
        if j["id"] not in seen:
            seen.add(j["id"])
            unique.append(j)
    return unique