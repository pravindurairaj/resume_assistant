---
description: "Scrape LinkedIn jobs for Navya and produce a scored Excel. Use when: job-scraper navya, scrape jobs navya, find jobs navya, linkedin jobs navya."
name: "job-scraper-navya"
argument-hint: "[--date day|week|month] [-k keyword] [--max 50]"
---

Scrape LinkedIn jobs for **Navya Gopala Reddy**. Follow `.github/skills/job-scraper/SKILL.md`.

Run immediately — no confirmation:

```powershell
# Run from the project root (wherever this repo is cloned)
.\.venv\Scripts\python.exe .github\skills\job-scraper\scripts\scrape-linkedin-jobs.py --user Navya
```

Add any optional flags the user included (`-k`, `-l`, `-d`, `--max`).

After completion: show results table and Excel path saved to `Navya/JobSearch/`.
