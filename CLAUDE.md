# Resume Workspace — Claude Code Guide

> Full project reference: @README.md
> Skill development history: @.github/context/resume_tailor.md and @.github/context/job_scraper.md

---

## Project Purpose

AI-assisted job-hunt pipeline:
1. **Job Scraper** — scrapes LinkedIn public listings, scores against user target roles, writes Excel.
2. **Resume Tailor** — master resume + JD → ATS-friendly `.docx`. Never fabricates skills.
3. **setup-users.py** — bootstraps/updates user directories from `{Name}_Resume.docx` files at project root.

Multi-user: Pravin (SRE/DevOps), Navya (Finance/Accounting). Each has separate career profile + output folders.

---

## Virtual Environment

Venv is named **`resume_assistant`** (not `.venv`).

```bash
# Activate (Windows PowerShell)
.\resume_assistant\Scripts\Activate.ps1

# Activate (Windows cmd)
resume_assistant\Scripts\activate.bat

# Run scripts directly without activating
resume_assistant/Scripts/python <script.py>
```

---

## Key Commands

```bash
# Onboard / refresh user from .docx at project root (auto-discovers *_Resume.docx)
resume_assistant/Scripts/python setup-users.py
resume_assistant/Scripts/python setup-users.py Pravin     # specific user only

# Scrape jobs
resume_assistant/Scripts/python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user Pravin

# Extract .docx to .md (single file)
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/extract-resume.py \
  "Resume.docx" -o ".github/Users/{Name}/{Name}_Resume.md"

# Generate .docx from .md
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/md-to-docx.py \
  ".github/Users/{Name}/{Name}_Resume_{Co}.md" "{Name}/Resumes/{Co}" "{Full Name}"

# Batch manifest then autonomous pipeline
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/batch-job-reader.py --user Pravin --min-fit 50
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/batch-pipeline.py \
  --manifest Pravin/JobSearch/batch_manifest_{ts}.json --min-fit 50 --llm-polish-above 75
```

---

## Skill / Agent Invocation

```
/resume-tailor Pravin <paste JD>    # tailor single resume
/resume-tailor batch Pravin         # auto-batch from latest Excel
/job-scraper Pravin                 # scrape + score LinkedIn
```

---

## ATS Rules (ALWAYS enforced — non-negotiable)

1. Section order: `Professional Summary → Skills → Work Experience → Education → Projects → Certifications → Right to Work`
2. No tables, text boxes, columns, or graphics
3. Date format: `MMM YYYY` (e.g., `Jan 2023`) — never numeric dates
4. No first-person pronouns
5. Right to Work line mandatory (Irish employers)
6. `"kubernetes"` never in Professional Summary (use "container orchestration")
7. Font: Calibri Light 11pt, navy headings `#1F4E79`, grey dates `#555555`
8. **Pravin: max 2 pages** — Murex role max 10 bullets, must fit on page 1
9. **Navya: max 3 pages**
10. Projects section omitted if zero JD-relevant projects or page limit exceeded

---

## File Sync Rule

`.github/` and `.claude/` must stay **identical** — same skills, scripts, prompts, agents, instructions.
Always update both when changing either.

---

## User Data Locations

| Asset | Path |
|-------|------|
| Master resume (Pravin) | `.github/Users/Pravin/Pravin_Resume.md` |
| Master resume (Navya) | `.github/Users/Navya/Navya_Resume.md` |
| Career profile (gitignored PII) | `.github/instructions/career-profile-{Name}.instructions.md` |
| Tailored output | `{Name}/Resumes/{Company}/{Name}_Resume_{Company}.docx` |
| Application log | `{Name}/History/resumes_created.xlsx` |

---

## Development Constraints

- Scripts use **relative paths** from project root — no hardcoded absolute paths
- Career profiles and master resumes are **gitignored** (PII) — each user adds locally
- `setup-users.py` reuses `extract()` from `extract-resume.py` via `importlib` — no logic duplication
- **DRY rule**: extract only when a second consumer exists; document DRY opportunities in context files

---

## Claude Code Best Practices

Following [Claude Code best practices](https://code.claude.com/docs/en/best-practices):

- **CLAUDE.md is short** — only what Claude can't infer from code; full docs live in README.md
- **Skills** in `.claude/skills/` with `SKILL.md` — invoked via `/resume-tailor`, `/job-scraper`
- **Agents** in `.claude/agents/` — full pipeline orchestration
- **Context files** in `.github/context/` and `.claude/context/` — updated every session with learnings
- **Verification**: always run scripts and check output files before reporting task complete
- **Explore → Plan → Implement** workflow for non-trivial multi-file changes
- **Context**: run `/clear` between unrelated tasks; use subagents for codebase investigations
