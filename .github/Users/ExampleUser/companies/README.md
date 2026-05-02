# companies/ — Per-Job Context Files

This folder holds one Markdown file per tailored job application. Each file is created automatically by the resume-tailor skill during batch or single-job runs.

## File naming

```
{FolderName}.md
```

Where `{FolderName}` follows the output folder naming rule:
- Single job at a company → `{CompanySanitized}` (e.g. `AcmeCorp.md`)
- Multiple jobs at same company → `{CompanySanitized}_{RoleShort}` (e.g. `AcmeCorp_DataAnalyst.md`)

## File contents (auto-generated)

```markdown
# {Company} — {Job Title}

## Metadata
- **Applied**: YYYY-MM-DD
- **Location**: {location}
- **Job Link**: [{link}]({link})
- **Fit Score**: {fit_pct}%
- **Best Matching Role**: {matching_role}
- **Resume**: [{output_docx}]({output_docx})

## Job Description
{full jd_text}

## Match Report
- **Required matched**: X/Y
- **Preferred matched**: A/B
- **Gaps**: {list}

## Notes
_(empty — add interview dates, salary, contacts, feedback here)_
```

> All files in this folder are gitignored — they contain scraped JD text and personal application data.
> This README.md is the only committed file here.
