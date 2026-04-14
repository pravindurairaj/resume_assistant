---
description: "Autonomously tailor resumes for Pravin from latest manifest. Use when: resume-tailor pravin, batch resume pravin, tailor pravin, process jobs pravin."
name: "resume-tailor-pravin"
argument-hint: "[auto|single|status] [--min-fit 50] [--llm-polish-above 75]"
---

Tailor resumes for **Pravin Kumar Durairaj**. Follow `.github/skills/resume-tailor/SKILL.md`.

Second word selects mode:

| Argument | Mode |
|----------|------|
| *(none)* or `auto` | Autonomous batch via `batch-pipeline.py` |
| `single` | One job — paste JD below |
| `status` | Show `resumes_created.xlsx` summary |
| `manifest` | Generate fresh manifest from latest Excel |

## Auto mode (default)

Check if the newest Excel is newer than the newest manifest. If yes (or no manifest exists), generate a fresh manifest first:

```powershell
# Run from the project root (wherever this repo is cloned)

$latestExcel    = Get-ChildItem "Pravin\JobSearch\LinkedIn_Jobs_AllRoles_*.xlsx" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$latestManifest = Get-ChildItem "Pravin\JobSearch\batch_manifest_*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $latestManifest -or ($latestExcel -and $latestExcel.LastWriteTime -gt $latestManifest.LastWriteTime)) {
    Write-Host "Excel is newer than manifest — generating fresh manifest..."
    .\.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\batch-job-reader.py --user Pravin --min-fit 50 --excel $latestExcel.FullName
}

$manifest = Get-ChildItem "Pravin\JobSearch\batch_manifest_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
.\.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\batch-pipeline.py --manifest $manifest --min-fit 50 --llm-polish-above 75
```

## Single mode

Ask for JD, then:
```powershell
.\.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\tailor-resume.py `
  --manifest-entry _single_job.json `
  --master .github\Users\Pravin\Pravin_Resume.md `
  --author "Pravin Kumar Durairaj"
```

## Status mode

```powershell
.\.venv\Scripts\python.exe -c "import openpyxl; from pathlib import Path; wb=openpyxl.load_workbook('Pravin/History/resumes_created.xlsx'); ws=wb.active; rows=list(ws.iter_rows(min_row=2,values_only=True)); print(f'Total: {len(rows)}'); [print(r[0],r[1][:22],r[2][:28],r[6]) for r in rows[-10:]]"
```
