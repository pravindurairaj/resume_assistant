# Resume Workspace — Agent Behaviour Rules

> This file is read by OpenAI Codex, GPT-4o, and any OpenAI-compatible agent
> operating in this workspace. It defines mandatory rules and project context.

## Project Overview

AI-assisted job-hunt pipeline:

1. **Job Scraper** — scrapes public LinkedIn listings, scores against target roles
2. **Resume Tailor** — JD → ATS-optimised `.docx` tailored to a specific posting

## Mandatory Rules

### Never Fabricate

- Only use skills, experience, and achievements from the candidate's master resume
- If a required skill is absent → note the gap; do not invent it
- Never add certifications, degrees, or companies not in the source resume

### Relative Paths Only

- All file paths must be relative to the project root
- No hardcoded absolute paths (e.g., `C:\Users\...` or `/home/...`)
- Use `.github/skills/resume-tailor/scripts/` for script references

### ATS Compliance

- No tables, text boxes, columns, or graphics in generated resumes
- Standard section order: `Professional Summary → Skills → Work Experience → Education → Projects → Certifications → Right to Work`
- Date format: `MMM YYYY` (e.g. `Jan 2023`)
- No first-person pronouns
- Right to Work line is mandatory for every resume

### PII Handling

- Career profiles (`.github/instructions/career-profile-*.instructions.md`) contain PII — never log, print, or expose them in output unless directly requested by the user
- Master resumes are personal — treat with same care as PII

## Project Structure

```text
resume-workspace/
├── CLAUDE.md                    ← full developer guide
├── AGENTS.md                    ← this file
├── requirements.txt             ← Python deps
├── .github/
│   ├── copilot-instructions.md  ← GitHub Copilot context
│   ├── instructions/            ← career profiles (gitignored — user adds locally)
│   ├── skills/job-scraper/      ← scraper skill + scripts
│   ├── skills/resume-tailor/    ← tailor skill + scripts
│   ├── prompts/                 ← slash-command prompts
│   ├── agents/                  ← agent definitions
│   └── Users/                   ← master resumes (gitignored — user adds locally)
├── .claude/                     ← mirrors .github/ for Claude Code
└── {UserName}/                  ← user output (gitignored content)
    ├── Resumes/{Company}/       ← tailored .docx
    ├── JobSearch/               ← Excel + batch manifests
    └── History/                 ← resumes_created.xlsx
```

## Key Commands

```bash
# Bootstrap user from .docx at project root
resume_assistant/Scripts/python setup-users.py {Name}

# Scrape LinkedIn jobs
resume_assistant/Scripts/python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user {Name}

# Generate batch manifest
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/batch-job-reader.py --user {Name} --min-fit 50

# Autonomous batch tailoring
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/batch-pipeline.py \
  --manifest {Name}/JobSearch/batch_manifest_{ts}.json

# Convert .md → .docx
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/md-to-docx.py \
  ".github/Users/{Name}/{Name}_Resume_{Co}.md" "{Name}/Resumes/{Co}" "{Full Name}"
```

## When Generating Resumes

1. Read the master resume from `.github/Users/{Name}/{Name}_Resume.md`
2. Read the career profile from `.github/instructions/career-profile-{name}.instructions.md`
3. Parse the JD — extract required skills, keywords, role title, company
4. Build a skill match matrix — mark present / absent / partial
5. Generate tailored markdown — JD keywords in summary + bullets, trimmed skills
6. Call `md-to-docx.py` to produce the final `.docx`
7. Log the application via `log-application.py`

## Python Environment

The venv is named **`resume_assistant`** (not `.venv`).

```bash
# Activate venv (Windows PowerShell)
.\resume_assistant\Scripts\Activate.ps1

# Activate venv (macOS / Linux)
source resume_assistant/bin/activate

# Run scripts directly without activating
resume_assistant/Scripts/python <script.py>

# Install deps
pip install -r requirements.txt
```

See `CLAUDE.md` for the complete developer guide.
