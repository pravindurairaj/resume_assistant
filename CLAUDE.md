# Resume Workspace — Claude Code Guide

> This file is loaded automatically by **Claude Code** (`claude` CLI).
> It defines the project, structure, and key workflows so Claude can assist
> with any task without re-explaining context.

## Project Purpose

AI-assisted job-hunt pipeline with two core capabilities:

1. **Job Scraper** — scrapes public LinkedIn listings, scores them against a user's
   target roles, and writes a timestamped Excel file.
2. **Resume Tailor** — takes a master resume + job description → produces an ATS-friendly
   `.docx` tailored to that specific JD. Never fabricates skills.

Supports multiple users (separate career profiles + output folders).

---

## AI Assistant Compatibility

This workspace is structured for all major coding assistants:

| Assistant | Config File | Notes |
|-----------|------------|-------|
| Claude Code | `CLAUDE.md` (this file) | Full project context |
| GitHub Copilot | `.github/copilot-instructions.md` | Global context |
| Cursor | `.cursorrules` | Same rules |
| OpenAI Codex / agents | `AGENTS.md` | Behaviour rules |

Skills, prompts, and agents are **mirrored** under both `.github/` (Copilot) and `.claude/`
(Claude Code) so the workspace works identically in both tools.

---

## Repo Structure

```
resume-workspace/
│
├── CLAUDE.md                              ← Claude Code entry point (this file)
├── AGENTS.md                              ← OpenAI agents rules
├── .cursorrules                           ← Cursor rules
├── requirements.txt                       ← Python deps (pip install -r requirements.txt)
│
├── .github/                               ← GitHub Copilot config
│   ├── copilot-instructions.md            ← Global Copilot context
│   ├── instructions/                      ← Per-user career profiles (gitignored — add locally)
│   │   └── career-profile-template.instructions.md   ← starter template
│   ├── skills/
│   │   ├── job-scraper/
│   │   │   ├── SKILL.md                   ← Copilot skill definition
│   │   │   └── scripts/scrape-linkedin-jobs.py
│   │   └── resume-tailor/
│   │       ├── SKILL.md                   ← Copilot skill definition
│   │       ├── assets/                    ← Markdown + LaTeX resume templates
│   │       ├── references/                ← ATS guidelines
│   │       └── scripts/                   ← All Python scripts
│   ├── prompts/                           ← Slash-command prompts
│   ├── agents/                            ← Agent definitions
│   ├── context/                           ← Architecture & developer notes
│   └── Users/                             ← Master resumes (gitignored — add locally)
│       └── ExampleUser/                   ← Template user folder
│
├── .claude/                               ← Claude Code config (mirrors .github/)
│   └── (same structure as .github/)
│
├── docs/                                  ← Architecture diagrams
│   └── architecture.mmd                   ← Mermaid flowchart
│
├── {UserName}/                            ← User-specific output (gitignored content)
│   ├── Resumes/{Company}/                 ← Tailored .docx output
│   ├── JobSearch/                         ← Scraped Excel + batch manifests
│   └── History/                           ← resumes_created.xlsx tracker
│
└── .venv/                                 ← Python venv (gitignored)
```

---

## Quick Setup (New Machine)

```bash
# 1. Clone repo
git clone <repo-url>
cd resume-workspace

# 2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your career profile (gitignored — personal PII)
#    Copy template and fill in your details
cp .github/instructions/career-profile-template.instructions.md \
   .github/instructions/career-profile-{YourName}.instructions.md

# Also copy to .claude/ for Claude Code
cp .github/instructions/career-profile-{YourName}.instructions.md \
   .claude/instructions/career-profile-{YourName}.instructions.md

# 5. Create your master resume
mkdir -p .github/Users/{YourName}
# Place {YourName}_Resume.md here, or extract from .docx/.pdf:
python .github/skills/resume-tailor/scripts/extract-resume.py \
  "path/to/Resume.docx" -o ".github/Users/{YourName}/{YourName}_Resume.md"

# Also mirror to .claude/Users/
mkdir -p .claude/Users/{YourName}
cp .github/Users/{YourName}/{YourName}_Resume.md \
   .claude/Users/{YourName}/{YourName}_Resume.md

# 6. Create output folders
mkdir -p {YourName}/Resumes {YourName}/JobSearch/archive {YourName}/History
```

---

## Key Scripts

All scripts live under `.github/skills/*/scripts/` (mirrored in `.claude/`).

### Resume Tailor

```bash
# Convert .docx / .pdf → Markdown
python .github/skills/resume-tailor/scripts/extract-resume.py \
  "Resume.docx" -o ".github/Users/{Name}/{Name}_Resume.md"

# Convert .md → styled .docx
python .github/skills/resume-tailor/scripts/md-to-docx.py \
  ".github/Users/{Name}/{Name}_Resume_Acme.md" \
  "{Name}/Resumes/Acme" \
  "{Full Name}"

# Generate batch manifest from latest Excel
python .github/skills/resume-tailor/scripts/batch-job-reader.py \
  --user {Name} --min-fit 50

# Run autonomous batch pipeline
python .github/skills/resume-tailor/scripts/batch-pipeline.py \
  --manifest {Name}/JobSearch/batch_manifest_{ts}.json \
  --min-fit 50 --llm-polish-above 75

# Log an application
python .github/skills/resume-tailor/scripts/log-application.py \
  --user {Name} --company Acme --title "Data Analyst" \
  --location "Dublin, Ireland" --link "https://..." \
  --resume-file "{Name}/Resumes/Acme/{Name}_Resume_Acme.docx" --fit 85
```

### Job Scraper

```bash
# Scrape all target roles (reads career profile automatically)
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user {Name}

# Custom keyword / location / date
python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "Data Analyst" -k "Senior Analyst" \
  -l "Dublin, Ireland" -d week -m 50 --user {Name}
```

---

## Agent / Skill Invocation (GitHub Copilot / Claude Code)

### Single resume tailoring
```
/resume-tailor {Name} <paste job description>
```

### Batch (agent reads latest Excel, queues all jobs)
```
/resume-tailor batch {Name}
/resume-tailor auto-batch {Name} --min-fit 75
```

### Job scraping
```
/job-scraper {Name}
```

### Full pipeline (scrape → manifest → batch → log)
```
@job-search-agent {Name} full
```

---

## Data Model

### Career Profile (`.github/instructions/career-profile-{Name}.instructions.md`)
- Contact info, target roles, target industries
- Resume constraints (max pages, ATS rules)
- Used by both job-scraper (for keyword extraction) and resume-tailor (for skill matching)

### Master Resume (`.github/Users/{Name}/{Name}_Resume.md`)
- Markdown format — all skills, full history, all bullets
- This is the source; tailored versions are derived from it
- Never delete bullets from master — always keep everything

### Job Excel (`{Name}/JobSearch/LinkedIn_Jobs_{ts}.xlsx`)
- Columns: `#`, `Company`, `Job Title`, `Location`, `Job Link`, `Date Scraped`, `Fit %`, `Best Matching Role`
- Rows 1–3: metadata; Row 4: headers; Row 5+: data
- Color-coded: green ≥75%, amber 50–74%, red <50%

### Batch Manifest (`{Name}/JobSearch/batch_manifest_{ts}.json`)
- Generated by `batch-job-reader.py`
- Contains: job list with company, title, link, fit %, output paths, status
- `--manifest` flag in batch-pipeline.py resumes interrupted runs

### Application Tracker (`{Name}/History/resumes_created.xlsx`)
- Append-only; written by `log-application.py`
- Columns: Date, Company, Title, Location, Link, Resume File, Fit %

---

## ATS Rules (always enforced)

1. Standard section order: `Professional Summary → Skills → Work Experience → Education → Projects → Certifications → Right to Work`
2. No tables, text boxes, columns, or graphics
3. Date format: `MMM YYYY` (e.g. `Jan 2023`)
4. No first-person pronouns
5. Right to Work line is mandatory (Irish employers)
6. Projects omitted if zero JD-relevant or page limit exceeded
7. `"kubernetes"` never in Professional Summary (use "container orchestration")
8. Font: Calibri Light 11pt, navy headings (#1F4E79), grey dates (#555555)

---

## Development Notes

- `.github/` and `.claude/` **must stay in sync** — same skills, scripts, prompts, agents
- Career profiles and master resumes are **gitignored** (PII) — each user adds locally
- Scripts use **relative paths** from project root — no hardcoded absolute paths
- Output `.docx` author metadata is set to the user's full name via `md-to-docx.py`
- LinkedIn individual JD pages require auth — scraper uses guests search API (listing only)

---

## Adding a New User

1. Copy and fill career profile template → `.github/instructions/career-profile-{Name}.instructions.md`
2. Copy same file → `.claude/instructions/career-profile-{Name}.instructions.md`
3. Create `.github/Users/{Name}/{Name}_Resume.md` (master resume)
4. Mirror to `.claude/Users/{Name}/{Name}_Resume.md`
5. Create output dirs: `{Name}/Resumes/`, `{Name}/JobSearch/archive/`, `{Name}/History/`
6. Add `.gitkeep` files in each empty output dir

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `markitdown` import error | `pip install 'markitdown[docx,pdf]'` |
| LinkedIn scraper returns 0 results | Rate-limited — wait 5–10 mins, reduce `-m` |
| `.docx` opens with wrong font | Calibri Light must be installed on the machine |
| Batch interrupted mid-run | Re-run with `--manifest` flag — skips completed jobs |
| Author metadata wrong in .docx | Pass full name as 3rd arg to `md-to-docx.py` |
