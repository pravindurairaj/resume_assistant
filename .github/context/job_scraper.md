# Job Scraper — Development Context

## Overview

The job-scraper skill scrapes public LinkedIn job listings (no login required) and rates each listing against a user's career profile target roles, generating a colour-coded Excel report.

## Architecture & Data Flow

```
career-profile-{user}.instructions.md
        │
        ├── Location      → default --location
        ├── Target Roles  → default --keywords (one search per role)
        └── Target Roles  → fit % rating for every job
                │
                ▼
  For each keyword in keyword_list:
    LinkedIn Guest API (no auth)
    GET /jobs-guest/jobs/api/seeMoreJobPostings/search
        │
        ▼
  Deduplicate by job link across all keyword runs
        │
        ▼
  Calculate fit % (keyword coverage + Jaccard vs Target Roles)
        │
        ▼
  Excel output: {UserName}/JobSearch/LinkedIn_Jobs_{kw|AllRoles}_{ts}.xlsx
    ├── Sheet 1: LinkedIn Jobs  (sorted by fit %, colour-coded)
    └── Sheet 2: Summary        (high / medium / low counts)
```

## Key Functions

| Function | Purpose | Reusable? |
|----------|---------|-----------|
| `find_repo_root()` | Walk up dirs to find .github/ | Yes — potential shared util |
| `load_career_profile(user)` | Parse instructions.md: full_name, location, target_roles, target_industries | Yes — any skill needing user data |
| `scrape_linkedin_jobs(kw, loc, date, max)` | Fetch LinkedIn guest search, paginated | Scraper-specific |
| `calculate_fit(title, roles)` | Rate job title vs target roles 0-100% | Yes — any job-matching tool |
| `save_to_excel(jobs, path, roles, meta)` | Styled .xlsx with fit ratings | Scraper-specific |

## DRY Opportunities (documented; not yet extracted)

1. **`load_career_profile()`** — lives in `scrape-linkedin-jobs.py`. When a second consumer (e.g., cover-letter skill) needs profile data, extract to `.github/skills/_shared/profile_loader.py`.

2. **`find_repo_root()`** — same upward-walk pattern exists conceptually across skill scripts. Move to shared utils once two consumers exist.

3. **`calculate_fit()`** — pure function, no side effects. Could be shared by any future job-matching or resume-scoring tool.

4. **Excel styling constants** — `hdr_fill` (navy `1F4E79`), `thin_border`, green/amber/red fills are defined inline. Extract to a shared styles module if more Excel-generating skills are added.

> **Rule applied:** Extract only when a second consumer exists (YAGNI). All four are documented here for the next engineer.

## Parameter Resolution Chain

```
CLI --keywords   →  (if None)  →  career-profile Target Roles  →  (if none) → sys.exit(1)
CLI --location   →  (if None)  →  career-profile Location      →  (if none) → "Any location"
CLI --output-dir →  (if None)  →  {UserName}/JobSearch/
CLI --date-posted              →  default: "day"  (24 hours)
```

## CLI Quick Reference

```bash
# Minimal — auto-reads everything from Pravin's profile
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user Pravin

# Single keyword override
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py -k "Data Analyst" --user Pravin

# Multi-keyword with dedup
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py -k "DevOps" -k "SRE" --user Pravin

# Full manual
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "Platform Engineer" -l "London, UK" -d week -m 50 --user Pravin
```

## Session History

### v3 — 2026-04-16 (current)

| Change | Detail |
|--------|--------|
| Venv renamed | `.venv` → `resume_assistant` — update all run commands to use `resume_assistant/Scripts/python` |
| README updated | Setup steps renumbered; `setup-users.py` step added before career profile step |
| CLAUDE.md | Updated key commands to reference `resume_assistant/Scripts/python` |
| No script changes | Scraper logic unchanged; only docs + venv reference updated |

### v2 — 2026-04-10 (previous)

| Change | Detail |
|--------|--------|
| `load_career_profile()` | Replaces `load_target_roles()`. Now extracts full_name, location, target_roles, target_industries in one pass (DRY) |
| `--keywords` optional | `action="append"`, falls back to all Target Roles from profile |
| `--location` optional | Falls back to Location from profile contact table |
| Default time: `day` | Changed from `week` to `day` (24h) |
| Multi-keyword loop | Iterates keyword_list, scrapes each, deduplicates via `seen_links` set |
| Output dir default | `{UserName}/JobSearch` instead of CWD |
| Filename | Single kw → `LinkedIn_Jobs_{kw}_{ts}.xlsx`, multi → `LinkedIn_Jobs_AllRoles_{ts}.xlsx` |
| `cell()` closure fix | Added `_rn=row_num, _rf=row_fill` default params to prevent loop variable capture bug |
| Removed `GradientFill` | Was imported but never used |

### v1 — Initial creation (same session)

- LinkedIn guest API scraping, no auth
- openpyxl Excel output with navy headers, colour-coded fit, hyperlinks, summary sheet
- `load_target_roles()` extracted Target Roles from career profile for fit rating
- `--keywords` required, `--date-posted` defaulted to `week`

## Regression Testing Checklist

| # | Command | Expected |
|---|---------|----------|
| 1 | `--user Pravin` (no -k) | Auto-uses 6 Target Roles + Dublin + day; file: `Pravin/JobSearch/LinkedIn_Jobs_AllRoles_{ts}.xlsx` |
| 2 | `-k "Data Analyst" --user Pravin` | Single keyword search; file: `LinkedIn_Jobs_Data_Analyst_{ts}.xlsx` |
| 3 | `-k "DevOps" -k "SRE" --user Pravin` | Two searches, dedup count in console |
| 4 | `-l "London, UK" --user Pravin` | Overrides profile Dublin; loc_display shows London |
| 5 | `-d week --user Pravin` | Overrides default 24h; uses `r604800` filter |
| 6 | `--user Navya` (no -k) | Placeholder profile → no target roles → error: "provide at least one -k" |
| 7 | `--user Navya -k "Test"` | Works; no fit rating (no roles in profile) |
| 8 | `--user Unknown` (no -k) | "No career profile found" + error: "provide at least one -k" |
| 9 | Excel output | Frozen panes row 5+, clickable links, green/amber/red Fit %, Summary sheet |
| 10 | Dedup | Same job from two keyword searches appears only once |

## Files

| File | Role |
|------|------|
| `.github/skills/job-scraper/scripts/scrape-linkedin-jobs.py` | Main scraper script |
| `.github/skills/job-scraper/SKILL.md` | Skill definition and invocation docs |
| `.github/instructions/career-profile-{user}.instructions.md` | Source of auto-filled keywords, location, fit roles |
| `.github/context/job_scraper.md` | This file — development context |
| `requirements.txt` | `requests beautifulsoup4 openpyxl` (+ python-docx, markitdown) |

## Folder Structure (updated 2026-04-10)

```
{UserName}/
├── JobSearch/
│   ├── LinkedIn_Jobs_AllRoles_{ts}.xlsx    ← latest scrape
│   ├── LinkedIn_Jobs_Master_{date}.xlsx    ← collated master (future)
│   └── archive/                            ← old individual scrape files
├── Resumes/                                ← tailored .docx (from resume-tailor)
│   └── {Company|Role}/
└── History/
    └── applied_jobs.xlsx                   ← application tracker (from resume-tailor)
```

## Cross-Skill Integration

| Integration | Direction | Detail |
|------------|-----------|--------|
| job-scraper → resume-tailor | `{User}/JobSearch/*.xlsx` | resume-tailor Step 0.5 reads latest Excel to present job list |
| resume-tailor → History | `{User}/History/applied_jobs.xlsx` | resume-tailor Step 6.5 appends row after generating .docx |
| Cleanup/collate | Manual or future script | Merge all `.xlsx` in JobSearch/ → master, archive old files |

## Maintenance — Cleanup Procedure

When `JobSearch/` has multiple Excel files:
1. Read all `.xlsx`, merge rows, deduplicate by Job Link
2. Save `LinkedIn_Jobs_Master_{YYYYMMDD}.xlsx`
3. Move old files to `{User}/JobSearch/archive/`
