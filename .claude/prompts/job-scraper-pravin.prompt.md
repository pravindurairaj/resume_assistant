---
description: "Scrape LinkedIn jobs for Pravin and produce a scored Excel. Use when: job-scraper pravin, scrape jobs pravin, find jobs pravin, linkedin jobs pravin."
name: "job-scraper-pravin"
argument-hint: "[--date day|week|month] [-k keyword] [--max 50]"
---

Scrape LinkedIn jobs for **Pravin Kumar Durairaj**. Follow `.github/skills/job-scraper/SKILL.md`.

Run immediately — no confirmation:

```powershell
# Run from the project root (wherever this repo is cloned)
.\.venv\Scripts\python.exe .github\skills\job-scraper\scripts\scrape-linkedin-jobs.py --user Pravin
```

Add any optional flags the user included (`-k`, `-l`, `-d`, `--max`).

After completion: show results table and Excel path saved to `Pravin/JobSearch/`.
