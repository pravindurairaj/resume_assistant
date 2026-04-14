---
description: "Convert a resume file (.docx, PDF, or text) into a formatted Markdown or LaTeX file. Use when: convert resume to markdown, resume to latex, export resume, format resume, resume conversion, docx to markdown, docx to latex."
agent: "agent"
argument-hint: "Path to the resume file, or attach it. Optionally specify format: md (default) or latex"
tools: ["readFile", "runCommand", "createFile"]
---

Convert the provided resume into a well-formatted file using the correct template.

## Inputs

The user provides:
1. **Resume** — a `.docx` or `.pdf` file path, or the resume attached/pasted in chat
2. **Output format** — `md` (Markdown, default) or `latex` (LaTeX `.tex`)

If no format is specified, use **Markdown**.

## Step 1 — Determine Input Source

**If the resume is a `.docx` or `.pdf` file on disk:**

Run the extraction script to get clean Markdown:

```
python .github/skills/resume-tailor/scripts/extract-resume.py "<path/to/resume.docx>"
```

If `markitdown` is not installed, install it first:
```
pip install 'markitdown[docx,pdf]'
```

Optionally save directly to a `.md` file:
```
python .github/skills/resume-tailor/scripts/extract-resume.py "<path/to/resume.docx>" -o extracted.md
```

Use the script's output (the text between `=== EXTRACTED RESUME ===` and `=== END OF RESUME ===`) as the source content.
The output is clean Markdown — headings, bullets, and plain text are already structured.

**If the resume is attached in chat or pasted as text:**

Read it directly from the chat content.

## Step 2 — Parse the Content

From the extracted resume text, identify and extract:

| Field | What to Look For |
|-------|-----------------|
| **Full Name** | First prominent line, or `## SECTION: NAME` |
| **Contact Info** | Email, phone, LinkedIn, location — usually near the top |
| **Summary / Profile** | Section labelled Summary, Profile, Objective, or About |
| **Skills** | Section labelled Skills, Technical Skills, Core Competencies |
| **Work Experience** | Roles with company names, dates, and bullet points |
| **Projects** | Section labelled Projects, Key Projects, Portfolio |
| **Education** | Degrees, institutions, graduation dates |
| **Certifications** | Certs, licences, professional qualifications |

Parse `>>> Subheading` markers as role titles or company names.
Parse `  - Bullet` markers as experience bullets.

## Step 3 — Select and Fill the Template

### For Markdown output (`md`):

Use [template-markdown.md](../skills/resume-tailor/assets/template-markdown.md) as the structure.

Formatting rules:
- Name as `# Full Name` (H1)
- Contact line: `**City, Country** | Phone | Email | [LinkedIn](URL)`
- Section headers as `## Section Name` (H2)
- Role headers as `### Job Title | Company Name` with dates on the next line in bold
- Bullets starting with `- ` (dash space)
- Skills grouped in bold categories: `**Category:** Skill1, Skill2`
- No tables, no HTML, no columns

### For LaTeX output (`latex`):

Use [template-latex.tex](../skills/resume-tailor/assets/template-latex.tex) as the structure.

Formatting rules:
- Escape special LaTeX characters in content: `&`, `%`, `$`, `#`, `_`, `^`, `{`, `}`, `~`, `\`
  - e.g. `C#` → `C\#`, `&` → `\&`, `%` → `\%`
- Name in `{\LARGE\bfseries FULL NAME}`
- Dates right-aligned using `\hfill`
- Bullet points inside `itemize` environments
- Section titles via `\section{}`

## Step 4 — Apply Formatting Quality Rules

Follow the [ATS guidelines](../skills/resume-tailor/references/ats-guidelines.md):

- [ ] No first-person pronouns
- [ ] Each bullet starts with an action verb
- [ ] Consistent date format: `MMM YYYY – MMM YYYY` (or `Present`)
- [ ] No "References available on request"
- [ ] No photo, nationality, DOB, or marital status
- [ ] Section order: Summary → Skills → Work Experience → Projects → Education → Certifications

## Step 5 — Save the Output File

Determine the output filename:
- Derive from the input filename: e.g. `Pravin_Resume.docx` → `Pravin_Resume.md` or `Pravin_Resume.tex`
- Save in the same directory as the input file (or workspace root if pasted as text)

Create the output file with the formatted content.

## Step 6 — Confirm

Report to the user:
> "Converted to `<output_filename>`. Format: [Markdown / LaTeX]. Sections found: [list them]. If anything looks off, let me know and I'll fix it."
