---
description: "Autonomously tailor resumes for Navya from latest manifest. Use when: resume-tailor navya, batch resume navya, tailor navya, process jobs navya."
name: "resume-tailor-navya"
argument-hint: "[auto|single|status] [--min-fit 50] [--llm-polish-above 75]"
---

Tailor resumes for **Navya Gopala Reddy**. Follow `.github/skills/resume-tailor/SKILL.md`.

Second word selects mode:

| Argument | Mode |
|----------|------|
| *(none)* or `auto` | Autonomous batch via `batch-pipeline.py` |
| `single` | One job — paste JD below |
| `status` | Show `resumes_created.xlsx` summary |
| `manifest` | Generate fresh manifest from latest Excel |

## Auto mode (default)

```powershell
# Run from the project root (wherever this repo is cloned)
$manifest = Get-ChildItem "Navya\JobSearch\batch_manifest_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
.\.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\batch-pipeline.py --manifest $manifest --min-fit 50 --llm-polish-above 75
```

If no manifest: run `batch-job-reader.py --user Navya` first.

## Single mode

Ask for JD, then:
```powershell
.\.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\tailor-resume.py `
  --manifest-entry _single_job.json `
  --master .github\Users\Navya\Navya_Resume.md `
  --author "Navya Gopala Reddy"
```

## Status mode

```powershell
.\.venv\Scripts\python.exe -c "import openpyxl; from pathlib import Path; wb=openpyxl.load_workbook('Navya/History/resumes_created.xlsx'); ws=wb.active; rows=list(ws.iter_rows(min_row=2,values_only=True)); print(f'Total: {len(rows)}'); [print(r[0],r[1][:22],r[2][:28],r[6]) for r in rows[-10:]]"
```
