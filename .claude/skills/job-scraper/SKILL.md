---
name: job-scraper
description: "Scrape LinkedIn public job listings by keyword, location, and date. Creates a timestamped Excel file with Company, Job Title, Job Link, and fit rating against the user's career profile target roles. Use when: job search, linkedin jobs, scrape jobs, find jobs, job listings, job hunt."
argument-hint: "<UserName> [keywords] [location] [date-posted]"
tools: run_in_terminal, read_file, create_file, get_errors
---

# Job Scraper

Scrape public LinkedIn job listings and produce a timestamped Excel report with fit ratings against a user's career profile. Auto-reads keywords (Target Roles) and location from the user's career profile instructions file.

## Prerequisites

> Ensure these are satisfied before running the scraper.

- **Python 3.10+** installed and available
- **Virtual environment** activated: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
- **Dependencies installed**: `pip install -r requirements.txt` (needs `requests`, `beautifulsoup4`, `openpyxl`)
- **Career profile exists**: `.github/instructions/career-profile-{UserName}.instructions.md` with `Target Roles` and `Location` filled in
- **Output folder**: `{UserName}/JobSearch/` (auto-created by the script if missing)

> **Execution policy:** Run the scraper script immediately using `run_in_terminal` without asking for confirmation. Do not prompt the user before executing — just run, show output, and report results.

## Available Users

Add any user who has a career profile in `.github/instructions/`:

| `--user` value | Profile file | Output folder |
|----------------|-------------|---------------|
| `Pravin` *(default)* | `career-profile-pravin.instructions.md` | `Pravin/JobSearch/` |
| `Navya` | `career-profile-navya.instructions.md` | `Navya/JobSearch/` |

To add a new user: create `.github/instructions/career-profile-{name}.instructions.md` with **Contact Information** (Location) and **Target Roles** sections.

## When to Use

- Search for jobs matching specific keywords and location
- Build a spreadsheet of open positions for review
- Rate job listings against a user's target roles
- Run a full scan of ALL target roles from a career profile in one command

## Invocation

### Minimal — auto-reads everything from a user's career profile

```bash
# Pravin (default)
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user Pravin

# Navya
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user Navya
```

For each user this reads their `.github/instructions/career-profile-{user}.instructions.md` and:
- Uses **all Target Roles** as search keywords (one search per role)
- Uses **Location** from contact info as location filter
- Defaults to **past 24 hours** (`day`)
- Saves to `{UserName}/JobSearch/LinkedIn_Jobs_AllRoles_{timestamp}.xlsx`
- Deduplicates jobs found across multiple keyword searches

### Override keywords only

```bash
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "Data Analyst" --user Pravin

python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "Financial Analyst" --user Navya
```

### Multiple explicit keywords

```bash
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "DevOps" -k "SRE" -k "Platform Engineer" --user Pravin

python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "Financial Accountant" -k "Finance Business Partner" --user Navya
```

### Full manual control

```bash
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "DevOps Engineer" -l "London, UK" -d week -m 50 --user Pravin
```

## Procedure

### Step 0 — Execute Immediately

**Run the script now** using `run_in_terminal`. Do not ask for confirmation.

Construct the command from the arguments provided:

```bash
# Run from the project root (wherever this repo is cloned)
.\.venv\Scripts\python.exe .github\skills\job-scraper\scripts\scrape-linkedin-jobs.py --user {UserName}
```

Add optional flags only if explicitly provided by the user:
- `-k "keyword"` — one per keyword (repeatable)
- `-l "location"` — override location
- `-d week|month|any` — override date filter (default `day`)
- `-m 50` — override max results (default 100)

Then wait for terminal output and report results.

### Step 1 — Load Career Profile & Resolve Parameters

The script reads `.github/instructions/career-profile-{user}.instructions.md` and extracts:
- **Full Name** — from contact table
- **Location** — from contact table (default location filter)
- **Target Roles** — default keywords AND fit rating source
- **Target Industries** — stored for future use

Parameters then resolved with this priority chain (CLI overrides profile):
- **Keywords**: `--keywords` if provided → else all Target Roles from profile
- **Location**: `--location` if provided → else Location from profile
- **Output dir**: `--output-dir` if provided → else `{UserName}/JobSearch/`
- **Date filter**: `--date-posted` → default `day` (24 hours)

### Step 2 — Scrape LinkedIn (per keyword)

Uses LinkedIn's public guest job search API (no login required):

```
GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
  ?keywords={keywords}
  &location={location}
  &f_TPR={time_filter}
  &start={offset}
```

Time filter values:
| `--date-posted` | Filter value |
|-----------------|-------------|
| `day` / `24h` (default) | `r86400` |
| `week` | `r604800` |
| `month` | `r2592000` |
| `any` | *(omitted)* |

- Paginates 25 results/page up to `--max-results`
- 2-second delay between pages (rate-limit safe)
- 30-second wait + retry on HTTP 429
- **Deduplicates** jobs across keyword runs by link URL

### Step 3 — Calculate Fit

Compares each job title against user's **Target Roles**:
- **95%** — exact target role phrase found in job title
- **High (75-94%)** — strong keyword coverage or Jaccard overlap
- **Medium (50-74%)** — partial keyword match
- **Low (<50%)** — minimal or no match

### Step 4 — Generate Excel

Output: `LinkedIn_Jobs_{keyword}_{ts}.xlsx` (single) or `LinkedIn_Jobs_AllRoles_{ts}.xlsx` (multi)

| # | Company | Job Title | Location | Job Link | Fit % | Best Matching Role |
|---|---------|-----------|----------|----------|-------|--------------------|

- Navy header row, bordered cells, alternating row colors
- Clickable "Open Job ↗" hyperlinks
- Color-coded Fit %: 🟢 Green ≥75% · 🟡 Amber 50-74% · 🔴 Red <50%
- Sorted by Fit % descending, frozen header row
- Summary sheet with high/medium/low counts

## CLI Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--keywords` | `-k` | *(from Target Roles)* | Search keywords (repeatable `-k`). Auto-filled from profile if omitted |
| `--location` | `-l` | *(from profile Location)* | Location filter. Auto-filled from profile if omitted |
| `--date-posted` | `-d` | `day` | `day` \| `24h` \| `week` \| `month` \| `any` |
| `--user` | `-u` | `Pravin` | User name — matches `career-profile-{user}.instructions.md` (case-insensitive). See Available Users above |
| `--max-results` | `-m` | `100` | Max listings per keyword search |
| `--output-dir` | `-o` | `{UserName}/JobSearch` | Output directory |

## Requirements

```bash
pip install -r .github/requirements.txt
# or: pip install requests beautifulsoup4 openpyxl
```

## Notes

- LinkedIn's public guest API requires no authentication or API key
- Default time window is **24 hours** (`day`) to get fresh listings
- `--user` does a case-insensitive partial match against `career-profile-*.instructions.md` filenames
- Jobs are deduplicated across multi-keyword searches by link URL
- Fit % is title-based only — open the job link to verify full JD match
- Profile fields wrapped in `{...}` (placeholders) are automatically skipped
- Output folder `{UserName}/JobSearch/` is created automatically if it does not exist

## Maintenance — Cleanup & Collation

Over time, `{UserName}/JobSearch/` accumulates multiple Excel files. Keep it clean:

### Collate into single master file

When multiple `.xlsx` exist in `JobSearch/`:
1. Read all `.xlsx` files in `{UserName}/JobSearch/`
2. Merge all rows, deduplicate by **Job Link** (keep latest entry if duplicate)
3. Save as `LinkedIn_Jobs_Master_{YYYYMMDD}.xlsx`
4. Move old individual files to `{UserName}/JobSearch/archive/`

### Folder structure

```
{UserName}/
├── JobSearch/
│   ├── LinkedIn_Jobs_Master_{date}.xlsx   ← collated, deduped master
│   └── archive/                           ← old individual scrape files
│       ├── LinkedIn_Jobs_AllRoles_20260410_183721.xlsx
│       └── ...
├── Resumes/                               ← tailored resumes (from resume-tailor)
│   └── {Company|Role}/
└── History/
    └── applied_jobs.xlsx                  ← application tracker (from resume-tailor)
```

### Cross-references

- **resume-tailor** reads the latest `.xlsx` from `JobSearch/` in Step 0.5 to present jobs
- **resume-tailor** writes to `History/applied_jobs.xlsx` in Step 6.5 after generating a resume
- `History/applied_jobs.xlsx` is the single source of truth for all applications sent
