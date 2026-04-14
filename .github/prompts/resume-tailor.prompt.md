---
description: "Tailor a resume to job descriptions — single job, batch autonomous, or LLM review. Use when: resume-tailor, tailor resume, batch resume, process manifest, auto tailor, resume to job, match resume."
argument-hint: "Pravin|Navya [batch|single|auto|status] [--min-fit 50] [--llm-polish-above 75]"
---

# Resume Tailor

Follow the `.github/skills/resume-tailor/SKILL.md` procedure.

**User** is the first word of the argument (e.g. `Pravin`).  
**Mode** is the second word (optional):

| Mode | What happens |
|------|-------------|
| `auto` (default) | Run `batch-pipeline.py` — autonomous, no approvals |
| `batch` | Agent-driven batch from latest manifest |
| `single` — paste JD | Tailor one job via `tailor-resume.py` |
| `status` | Show `resumes_created.xlsx` summary |

## Auto mode (default)

Find latest manifest and run pipeline:

```powershell
# Run from the project root (wherever this repo is cloned)
$manifest = Get-ChildItem "{User}\JobSearch\batch_manifest_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
.\.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\batch-pipeline.py --manifest $manifest --min-fit 50 --llm-polish-above 75
```

If no manifest exists, run `batch-job-reader.py` first to generate one.

## Single mode

Ask user to paste the job description, then run:

```powershell
.\.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\tailor-resume.py `
  --manifest-entry _single_job.json `
  --master .github\Users\{User}\{User}_Resume.md `
  --author "{UserFullName}"
```
