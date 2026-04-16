---
# GitHub Copilot — Project Instructions
# Loaded automatically for all Copilot Chat sessions in this workspace.
---

# Resume Workspace

AI-assisted job-hunt pipeline for multiple users. Two skills handle the full workflow:
scrape LinkedIn jobs → tailor resume to JD → export ATS-friendly `.docx`.

## Workspace Layout

```
.github/
  instructions/   ← career profiles (gitignored, add locally per user)
  skills/
    job-scraper/  ← SKILL.md + scrape-linkedin-jobs.py
    resume-tailor/← SKILL.md + md-to-docx.py + batch-pipeline.py + others
  prompts/        ← slash-command prompts
  agents/         ← job-search.agent.md (full pipeline)
  context/        ← architecture notes
  Users/{Name}/   ← master resumes (gitignored, add locally)

{UserName}/        ← per-user output (gitignored content)
  Resumes/{Company}/   ← tailored .docx
  JobSearch/           ← scraped Excel + batch manifests
  History/             ← resumes_created.xlsx
```

## Active Users

| User | Role | Profile |
|------|------|---------|
| Pravin | SRE/DevOps at Murex, Dublin | `career-profile-pravin.instructions.md` |
| Navya | Financial Accountant, Dublin | `career-profile-navya.instructions.md` |

Add a new user by placing `{Name}_Resume.docx` in the project root and running `setup-users.py {Name}`.
Then create `.github/instructions/career-profile-{Name}.instructions.md` from the template.

## Key Rules

- **Never fabricate** skills or experience — only use what's in the master resume
- **Relative paths only** — no hardcoded absolute paths in scripts or prompts
- **ATS rules** — no tables, text boxes, columns, or graphics in generated resumes
- **Right to Work line is mandatory** for every tailored resume
- **Career profiles are gitignored** — they contain PII; users add them locally

## Skill Invocation

```
/job-scraper {Name}
/resume-tailor {Name} <paste JD>
/resume-tailor batch {Name}
/resume-tailor auto-batch {Name}
@job-search-agent {Name} full
```

## Python Environment

```powershell
# Venv is named resume_assistant (not .venv)
.\resume_assistant\Scripts\Activate.ps1
pip install -r requirements.txt

# Run scripts directly without activating
resume_assistant\Scripts\python setup-users.py
```

All scripts: `.github/skills/resume-tailor/scripts/` and `.github/skills/job-scraper/scripts/`

See `CLAUDE.md` for the full developer guide.
