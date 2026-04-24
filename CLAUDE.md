# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Full project docs: @README.md
> Skill procedures: @.github/skills/resume-tailor/SKILL.md · @.github/skills/job-scraper/SKILL.md
> Development history: @.github/context/resume_tailor.md · @.github/context/job_scraper.md

---

## Project Purpose

AI-assisted job-hunt pipeline for multiple users:

1. **`setup-users.py`** — onboards users from `{Name}_Resume.docx` at project root → extracts Markdown → creates all directories.
2. **Job Scraper** (`scrape-linkedin-jobs.py`) — scrapes LinkedIn public listings, scores against career profile target roles, writes Excel.
3. **Resume Tailor** — master resume + JD → ATS-friendly `.docx`. Never fabricates skills or experience.

Active users: **Pravin** (SRE/DevOps, Murex Dublin) · **Navya** (Financial Accountant, Dublin).

---

## Virtual Environment

Venv is named **`resume_assistant`** — not `.venv`.

```bash
# Windows PowerShell
.\resume_assistant\Scripts\Activate.ps1

# Windows cmd
resume_assistant\Scripts\activate.bat

# Run without activating (preferred in scripts/CI)
resume_assistant/Scripts/python <script.py>
```

---

## Key Commands

```bash
# Onboard / refresh a user from *_Resume.docx in project root
resume_assistant/Scripts/python setup-users.py
resume_assistant/Scripts/python setup-users.py Pravin          # specific user

# Scrape LinkedIn jobs (auto-reads keywords + location from career profile)
# Default: fetches JD per job → full Phase-1+2 fit scoring; saves JDs to {User}/JobSearch/jds/
resume_assistant/Scripts/python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user Pravin
resume_assistant/Scripts/python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py \
  -k "DevOps" -k "SRE" -l "Dublin, Ireland" -d week --user Pravin
# Add --skip-jd-scrape for a fast title-only scan (fit %% capped at 40, no JD fetch)
resume_assistant/Scripts/python .github/skills/job-scraper/scripts/scrape-linkedin-jobs.py --user Pravin --skip-jd-scrape

# Single-file docx → md extract
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/extract-resume.py \
  "Name_Resume.docx" -o ".github/Users/{Name}/{Name}_Resume.md"

# md → docx (3 args: md path, output folder, author full name)
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/md-to-docx.py \
  ".github/Users/{Name}/{Name}_Resume_{Co}.md" "{Name}/Resumes/{Co}" "{Full Name}"

# Build batch manifest from latest Excel, then run autonomous pipeline
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/batch-job-reader.py \
  --user Pravin --min-fit 50
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/batch-pipeline.py \
  --manifest Pravin/JobSearch/batch_manifest_{ts}.json --min-fit 50 --llm-polish-above 75
```

### Skill invocation (Claude Code chat)

```
/job-scraper Pravin
/resume-tailor Pravin <paste JD>
/resume-tailor batch Pravin
/resume-tailor auto-batch Pravin --min-fit 75
```

---

## Architecture

### Data flow

```
{Name}_Resume.docx  →  setup-users.py  →  .github/Users/{Name}/{Name}_Resume.md
                                       →  .claude/Users/{Name}/{Name}_Resume.md
                                       →  {Name}/Resumes/, JobSearch/, History/

career-profile-{name}.instructions.md  →  scrape-linkedin-jobs.py
  (Target Roles + Location)               →  {Name}/JobSearch/LinkedIn_Jobs_AllRoles_{ts}.xlsx

latest .xlsx  →  batch-job-reader.py  →  batch_manifest_{ts}.json
manifest      →  batch-pipeline.py   →  tailor-resume.py (per job, via importlib)
                                       →  md-to-docx.py → {Name}/Resumes/{Co}/{Name}_Resume_{Co}.docx
                                       →  log-application.py → {Name}/History/resumes_created.xlsx
```

### Importing hyphenated-filename scripts

Python cannot import files with hyphens in their names via `import`. The established pattern used throughout this codebase is:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("module_name", Path(...) / "script-name.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
fn = module.function_name
```

`setup-users.py` imports `extract()` from `extract-resume.py` this way.
`batch-pipeline.py` imports `tailor_resume()` from `tailor-resume.py` this way.

### Script responsibilities

| Script | Role |
|--------|------|
| `setup-users.py` | Root bootstrap: discover → extract → write to both mirrors → create dirs |
| `extract-resume.py` | `.docx/.pdf → Markdown` via `markitdown`. Exposes `extract(path) → str` |
| `scrape-linkedin-jobs.py` | LinkedIn guest API scraper. Reads career profile, deduplicates, scores |
| `batch-job-reader.py` | Excel → JSON manifest. Filters by Fit %, auto-scrapes JD text from LinkedIn |
| `batch-pipeline.py` | Orchestrates: manifest → tailor-resume → md-to-docx → log per job |
| `tailor-resume.py` | Deterministic keyword-match resume tailoring (no LLM per job in batch mode) |
| `md-to-docx.py` | Markdown → styled `.docx` with navy headings, clickable LinkedIn hyperlink |
| `log-application.py` | Append-only row to `resumes_created.xlsx` — never overwrites existing rows |

### Output folder naming (`{FolderName}`)

- One role at a company → `{CompanySanitized}` (e.g. `AcmeCorp`)
- Multiple roles at same company → `{CompanySanitized}_{RoleShort}` (e.g. `AcmeCorp_DataAnalyst`)

---

## File Sync Rule — CRITICAL

`.github/` and `.claude/` must stay **identical**. Every skill, script, prompt, agent, instruction, and context file must exist in both locations with the same content. After changing any file in one, immediately copy to the mirror:

```bash
cp .github/skills/resume-tailor/SKILL.md .claude/skills/resume-tailor/SKILL.md
cp .github/context/resume_tailor.md .claude/context/resume_tailor.md
# etc.
```

After any session that modifies `.github/context/` files, also update `.claude/context/`.

---

## User Data Locations

| Asset | Path |
|-------|------|
| Master resume | `.github/Users/{Name}/{Name}_Resume.md` (gitignored PII) |
| Career profile | `.github/instructions/career-profile-{Name}.instructions.md` (gitignored PII) |
| Tailored Markdown | `.github/Users/{Name}/{Name}_Resume_{Co}.md` |
| Per-job context | `.github/Users/{Name}/companies/{FolderName}.md` |
| Tailored `.docx` | `{Name}/Resumes/{FolderName}/{Name}_Resume_{FolderName}.docx` |
| Job search Excel | `{Name}/JobSearch/LinkedIn_Jobs_AllRoles_{ts}.xlsx` |
| Application log | `{Name}/History/resumes_created.xlsx` |

---

## ATS Rules (ALWAYS enforced — non-negotiable)

1. **Section order**: Professional Summary → Skills → Work Experience → Education → Projects → Certifications → Right to Work
2. No tables, text boxes, columns, or graphics — single-column flow only
3. Dates: `MMM YYYY` format only (e.g. `Jan 2023`) — never numeric
4. No first-person pronouns (`I`, `my`, `me`)
5. Right to Work line mandatory in every resume (Irish employers)
6. `"kubernetes"` must never appear in Professional Summary — use "container orchestration"
7. Font: Calibri Light 11pt; navy headings `#1F4E79`; grey dates/locations `#555555`
8. **Pravin**: max 2 pages — Murex role max 10 bullets, must fit entirely on page 1
9. **Navya**: max 3 pages
10. Projects: max 2, only if JD-relevant AND within page limit — drop before shortening experience bullets

---

## Development Constraints

- All scripts use **relative paths from project root** — never hardcode absolute paths
- Career profiles and master resumes are **gitignored** — users add them locally
- **DRY rule**: only extract shared logic when a second consumer exists; document opportunities in context files — do not pre-abstract
- `setup-users.py` uses `importlib` to reuse `extract()` from `extract-resume.py` — do not inline the extraction logic

---

## Context Files (update every session)

After any meaningful change, append a dated `### YYYY-MM-DD — vN` entry to:
- `.github/context/resume_tailor.md` (resume tailor changes)
- `.github/context/job_scraper.md` (scraper changes)

Then sync both to `.claude/context/`.

---

## Behavioral Guidelines (Workflow Discipline)

Behavioral guidelines to reduce common LLM coding mistakes. Apply alongside the project-specific instructions above.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
