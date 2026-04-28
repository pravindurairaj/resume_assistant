# Resume Tailor

Tailor a resume to a specific job description. Follow the complete procedure in `.claude/skills/resume-tailor/SKILL.md`.

## Arguments

- **First word** = user name (e.g., `Pravin`, `Navya`)
- **Second word** (optional) = mode: `single`, `batch`, `auto-batch`, or `status`
  - `auto-batch` (default): Run autonomous batch pipeline → skip approval loops
  - `batch`: Agent-driven batch with job selection
  - `single`: Tailor one job (paste JD in chat)
  - `status`: Show application history
- **Remaining flags** (optional):
  - `--min-fit 50`: Filter jobs by fit threshold (default: 50)
  - `--llm-polish-above 75`: Flag high-fit jobs for optional LLM review

## Examples

```
/resume-tailor Pravin <paste job description>
/resume-tailor Pravin batch --min-fit 75
/resume-tailor Pravin auto-batch --min-fit 75 --llm-polish-above 85
/resume-tailor Pravin status
```

## Python execution (when needed)

The underlying script uses: `resume_assistant/Scripts/python.exe`

Run commands via:
```powershell
resume_assistant/Scripts/python.exe .github/skills/resume-tailor/scripts/tailor-resume.py ...
resume_assistant/Scripts/python.exe .github/skills/resume-tailor/scripts/batch-pipeline.py ...
```
