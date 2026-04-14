---
description: "Scrape LinkedIn jobs for a user and produce a scored Excel file. Use when: job-scraper, scrape jobs, find jobs, linkedin jobs, job hunt, new jobs."
argument-hint: "Pravin|Navya [keywords] [--date week|month] [--max 50]"
---

# Job Scraper

Follow the `.github/skills/job-scraper/SKILL.md` procedure.

**User** is the first word of the argument (e.g. `Pravin`).

Run immediately — no confirmation needed:

```powershell
# Run from the project root (wherever this repo is cloned)
.\.venv\Scripts\python.exe .github\skills\job-scraper\scripts\scrape-linkedin-jobs.py --user {User}
```

Add any extra flags the user specified (`-k`, `-l`, `-d`, `-m`).

After completion: show results table (Company, Title, Fit %, Link), report Excel path saved to `{User}/JobSearch/`.
