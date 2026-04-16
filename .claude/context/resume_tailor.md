# Resume Tailor — Development Context

## Overview

The resume-tailor skill creates ATS-friendly, JD-tailored resumes from stored master resumes. Integrates with job-scraper output to let users pick jobs from scraped listings.

## Architecture & Data Flow

```
.github/Users/{Name}/{Name}_Resume.md    ← master resume (all skills, full history)
        │
        ▼
  Step 0: Resolve candidate (name match in .github/Users/)
        │
        ▼
  Step 0.5: No JD? → Read latest .xlsx from {User}/JobSearch/
            Present numbered job list → user picks → scrape full JD from link
        │
        ▼
  Step 1: Parse master resume (extract all sections)
  Step 2: Parse JD (skills, requirements, keywords)
  Step 3: Skill matching matrix (never fabricate)
        │
        ▼
  Step 4: Generate tailored resume (ATS rules enforced)
        │
        ├──→ Step 5: Save .md to .github/Users/{Name}/{Name}_Resume_{Company}.md
        ├──→ Step 6: Generate .docx to {Name}/Resumes/{Company|Role}/
        └──→ Step 6.5: Log to {Name}/History/applied_jobs.xlsx
        │
        ▼
  Step 7: Print summary table of all resumes for user
```

## Folder Structure

```
{UserName}/
├── Resumes/                     ← tailored .docx files
│   ├── {Company}/
│   │   └── {UserName}_Resume_{Company}.docx
│   └── {Role}/
│       └── {UserName}_Resume_{Role}.docx
├── JobSearch/                   ← scraped job listings (from job-scraper)
│   ├── LinkedIn_Jobs_AllRoles_{ts}.xlsx
│   └── archive/                 ← old scrape files
└── History/
    └── applied_jobs.xlsx        ← application tracker
```

## Key Integration Points

| From | To | Data |
|------|----|------|
| job-scraper → resume-tailor | `{User}/JobSearch/*.xlsx` | Latest scrape file read in Step 0.5 |
| resume-tailor → History | `{User}/History/applied_jobs.xlsx` | Row appended in Step 6.5 |
| resume-tailor → Resumes | `{User}/Resumes/{Company\|Role}/` | .docx saved in Step 6 |

## ATS Format Rules (enforced in Step 4)

- No tables, text boxes, columns, or graphics
- Standard section headings: PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE, EDUCATION, CERTIFICATIONS, RIGHT TO WORK
- Standard fonts: Calibri, Arial, or Times New Roman
- Plain bullets (• or -), no custom symbols
- No underlining except hyperlinks
- MMM YYYY date format, no first-person pronouns
- 1–2 pages max (per career profile constraints)
- .docx output (not PDF unless requested)

## applied_jobs.xlsx Schema

| Column | Type | Description |
|--------|------|-------------|
| Date Applied | date | YYYY-MM-DD |
| Company | string | Company name from JD |
| Job Title | string | Role title from JD |
| Location | string | Job location |
| Job Link | URL | LinkedIn or other job posting URL |
| Resume File | path | Relative path to generated .docx |
| Fit % | int | Fit score from job-scraper (if picked from list) |

## Session History

### 2026-04-16 — v3 Updates (Setup & Onboarding)

| Change | Detail |
|--------|--------|
| `setup-users.py` added | Root-level script; auto-discovers `*_Resume.docx`, extracts via `importlib` reuse of `extract-resume.py`'s `extract()`, writes to both `.github/Users` and `.claude/Users`, creates output dirs |
| Venv renamed | `.venv` → `resume_assistant` (project-specific name for clarity) |
| Users bootstrapped | Pravin and Navya resumes extracted from `.docx` to `.md` in both `.github/Users/` and `.claude/Users/` |
| CLAUDE.md trimmed | Follows CC best practices — short, imports README via `@README.md`, only includes non-inferable context |
| README.md updated | Step 3 (setup-users.py), step numbering fixed, best practices section added, "Adding a new user" simplified |
| `.gitignore` updated | Added `resume_assistant/` venv entry |
| Output dirs created | `Navya/Resumes/`, `Navya/History/`, `Pravin/Resumes/`, `Pravin/History/` created with `.gitkeep` |

### Known Issues (v3)

| Issue | Status |
|-------|--------|
| Navya career profile | Template only — fill in real details for `career-profile-navya.instructions.md` |
| Pravin career profile | Template only — fill in real details for `career-profile-pravin.instructions.md` |
| `.github/Users/Pravin/Pravin_Resume.md` was a directory | Fixed — removed, re-extracted from docx correctly |

### 2026-04-10 — v2 Updates

| Change | Detail |
|--------|--------|
| Folder structure | `{User}/{Company}/` → `{User}/Resumes/{Company\|Role}/` |
| Step 0.5 added | Read latest JobSearch Excel, present job list, let user pick |
| ATS rules block | Explicit mandatory rules added to Step 4 (was just a reference link) |
| Step 6.5 added | Log application to `{User}/History/applied_jobs.xlsx` |
| Step 7 updated | Print summary table of all resumes for user |
| Quality checklist | Updated paths + history logging check |
| Known Issues | Added history tracking + folder fix entries |

### Previous (v1)

- Basic JD-paste workflow, no JobSearch integration
- Output to `{User}/{Company}/` (flat, no Resumes/ subfolder)
- No application tracking
- ATS rules only via reference link

## Files

| File | Role |
|------|------|
| `.github/skills/resume-tailor/SKILL.md` | Skill definition and procedure |
| `.github/skills/resume-tailor/scripts/md-to-docx.py` | Markdown → .docx converter |
| `.github/skills/resume-tailor/scripts/extract-resume.py` | .docx/.pdf → Markdown (markitdown) |
| `.github/skills/resume-tailor/assets/template-markdown.md` | Markdown resume template |
| `.github/skills/resume-tailor/references/ats-guidelines.md` | ATS formatting reference |
| `.github/context/resume_tailor.md` | This file — development context |
