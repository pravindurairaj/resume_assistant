# Job Scraper

Scrape public LinkedIn job listings and produce a timestamped Excel report with fit ratings. Follow the complete procedure in `.claude/skills/job-scraper/SKILL.md`.

## Arguments

- **First word** = user name (e.g., `Pravin`, `Navya`) — auto-reads keywords and location from career profile
- **Optional flags**:
  - `-k "keyword"` (repeatable): Override keywords (e.g., `-k "DevOps" -k "SRE"`)
  - `-l "location"`: Override location (e.g., `-l "London, UK"`)
  - `-d week|month|any`: Date filter (default: `day` = 24 hours)
  - `-m 50`: Max results per keyword (default: 100)
  - `--skip-jd-scrape`: Fast title-only scan without fetching full JDs (fit capped at 40%)

## Examples

```
/job-scraper Pravin
/job-scraper Pravin -d week -m 50
/job-scraper Pravin -k "DevOps" -k "SRE" -k "Platform Engineer"
/job-scraper Pravin -l "Dublin, Ireland" -d month
/job-scraper Pravin --skip-jd-scrape
```

## Output

Creates: `{User}/JobSearch/LinkedIn_Jobs_AllRoles_{YYYYMMDD_HHMM}.xlsx`

Excel columns: Company | Job Title | Location | Job Link | Date Scraped | Fit % | Best Matching Role

## Python execution (when needed)

The underlying script uses: `resume_assistant/Scripts/python.exe`

```powershell
resume_assistant/Scripts/python.exe .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user Pravin
```
