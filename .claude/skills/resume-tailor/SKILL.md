---
name: resume-tailor
description: "Tailor a resume to a job description. Use when: matching resume to JD, creating ATS-friendly resume, resume optimization, skill matching, resume formatting, job application resume, resume rewrite for job posting, batch tailor all scraped jobs."
argument-hint: "<UserName> <paste job description>  OR  batch <UserName>"
tools: run_in_terminal, read_file, create_file, insert_edit_into_file, get_errors
---

# Resume Tailor

Create an ATS-friendly, JD-tailored resume from a stored candidate resume and a target job description. Only uses skills and experience the candidate actually has — never fabricates. Produces a Markdown file (saved in the candidate folder) and a professional `.docx` file (saved outside `.github/`) as final outputs.

## Prerequisites

> Ensure these are satisfied before tailoring a resume.

- **Python 3.10+** installed and available
- **Virtual environment** activated: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
- **Dependencies installed**: `pip install -r requirements.txt` (needs `python-docx`, `markitdown[docx,pdf]`, `openpyxl`)
- **Career profile exists**: `.github/instructions/career-profile-{UserName}.instructions.md` (PII — add locally, gitignored)
- **Master resume exists**: `.github/Users/{UserName}/{UserName}_Resume.md` (PII — add locally, gitignored)
- **Output folders exist**: `{UserName}/Resumes/`, `{UserName}/JobSearch/`, `{UserName}/History/`

## When to Use

- Match a stored candidate resume against a job description
- Optimise an existing resume for ATS systems
- Rewrite a resume for a specific job posting
- Pick a job from latest job scrape and tailor a resume to it
- **Batch mode** — tailor resumes for all matching jobs from the latest scrape in one run

## Invocation

### Single-job mode
```
/resume-tailor <UserName> <paste job description>
```
- **First word** = user name — used to locate `.github/Users/{Name}/{Name}_Resume.md`
- **Remaining text** (or chat attachment) = job description
- If **no name given** → list available users from `.github/Users/` subfolders and ask user to pick
- If **name only, no JD** → check `{UserName}/JobSearch/` for latest Excel and present job list

### Batch mode
```
/resume-tailor batch <UserName>
/resume-tailor batch <UserName> --min-fit 75
/resume-tailor batch <UserName> --manifest Pravin/JobSearch/batch_manifest_20260411.json
```
- Runs `batch-job-reader.py` to read the latest JobSearch Excel, filter by Fit %, and produce a JSON manifest
- Agent reads the manifest and processes each job: paste JD → match → tailor → save .md → generate .docx → log history
- `--min-fit` overrides fit threshold (default 50%)
- `--manifest` resumes an interrupted batch from the last completed job

### Autonomous batch mode (recommended)
```
/resume-tailor auto-batch <UserName>
/resume-tailor auto-batch <UserName> --min-fit 75 --llm-polish-above 75
```
- Runs `batch-pipeline.py` which autonomously processes all jobs via `tailor-resume.py`
- **No LLM hand-crafting** — deterministic keyword matching selects and reorders bullets
- Writes `.docx` directly (no intermediate `.md` files)
- Jobs with fit >= `--llm-polish-above` are flagged for optional LLM review after
- ~95% token reduction vs agent-driven batch mode

```bash
# Example:
python .github/skills/resume-tailor/scripts/batch-pipeline.py \
  --manifest Pravin/JobSearch/batch_manifest_20260413_122745.json \
  --min-fit 50 --llm-polish-above 75
```

## Candidate Folder Convention

All master resumes live under `.github/Users/`:

```
.github/Users/
├── Pravin/
│   ├── Pravin_Resume.md                      ← master (all skills, full history)
│   ├── Pravin_Resume_IncidentManagement.md   ← tailored output (saved here)
│   └── ...
```

Tailored `.docx` outputs are saved **outside** `.github/` under `{UserName}/Resumes/`:

```
.github/Users/{UserName}/
├── {UserName}_Resume.md                      ← master resume (never edited)
├── {UserName}_Resume_{FolderName}.md         ← tailored markdown (per job)
└── companies/
    └── {FolderName}.md                       ← per-job context: JD + match + metadata

{UserName}/
├── Resumes/
│   ├── {FolderName}/                         ← {Company} or {Company}_{Role}
│   │   └── {UserName}_Resume_{FolderName}.docx
│   └── ...
├── JobSearch/
│   ├── LinkedIn_Jobs_AllRoles_{ts}.xlsx      ← scraped listings (from job-scraper)
│   ├── batch_manifest_{ts}.json             ← batch run manifest
│   └── jds/
│       └── {FolderName}.txt                 ← optional: pre-saved JD text files
└── History/
    └── resumes_created.xlsx               ← all applications logged
```

**Folder naming rules (`{FolderName}`):**
- Single job at company → `{CompanySanitized}` (e.g. `AcmeCorp`)
- Multiple jobs at same company → `{CompanySanitized}_{RoleShort}` (e.g. `AcmeCorp_DataAnalyst`)
- See `batch-job-reader.py` for exact sanitization logic

## Procedure

### Step 0 — Resolve Candidate

**If a name was provided:**
1. Search `.github/Users/` for a subfolder matching the name (case-insensitive, partial match OK)
2. Read `.github/Users/{FolderName}/{FolderName}_Resume.md` as the master resume
3. If no match:
   > "No resume found for '{name}'. Available users: [list subfolders]. Use `/convert-resume` to add a new one."

**If no name was provided:**
1. List subfolders in `.github/Users/` (skip `.gitkeep`)
2. Present as interactive chat prompt:
   > "Available users: 1. Pravin  2. ...  Which user and which job?"

### Step 0.5 — Check JobSearch for Available Roles (single-job mode, no JD provided)

If user invokes with **only a user name** (no JD pasted or attached, and NOT batch mode):

1. Run `batch-job-reader.py` to parse the latest Excel and get filtered job list:
   ```bash
   python .github/skills/resume-tailor/scripts/batch-job-reader.py --user {UserName}
   ```
2. Read the output manifest JSON via `read_file`
3. Present as numbered list to user, sorted by Fit % descending:
   > "Found 16 jobs ready to process (`batch_manifest_20260411_103000.json`):
   >
   > | # | Company | Job Title | Fit % | JD |
   > |---|---------|-----------|-------|----|
   > | 1 | Acme Corp | Senior Data Analyst | 95% | `{job-link}` |
   > | 2 | ... | ... | ... | ... |
   >
   > Pick a job number and paste its JD — or type `batch` to process all."
4. When user picks a number → ask them to paste the JD from LinkedIn (open the link in browser)
5. When user pastes JD → proceed to Step 1 (single-job flow)
6. If `JobSearch/` is empty or missing → skip, ask for JD as normal

> **Note:** JD text is now auto-scraped via the LinkedIn guest API. If scraping fails for any job, the user can paste the JD manually.

### Step 0.5-B — Batch Mode

Triggered when user invokes `/resume-tailor batch <UserName>`:

**B1. Run the manifest generator:**
```bash
# Run from the project root (wherever this repo is cloned)
.venv\Scripts\python.exe .github\skills\resume-tailor\scripts\batch-job-reader.py --user {UserName} [--min-fit N] [--manifest path]
```

**B2. Read the manifest:** `read_file` the JSON path printed by the script.

**B3. Present summary table:**
> "Batch manifest ready — {N} jobs to process, {S} skipped (resumes exist).
>
> | # | Company | Title | Fit % | JD Status |
> |---|---------|-------|-------|-----------|
> | 1 | Acme | Data Analyst | 95% | ✓ Pre-loaded |
> | 2 | ... | ... | ... | ⏳ Paste needed |
>
> Processing in chunks of 5. Confirm to start? (y/n)"

**B4. Collect missing JDs** — For jobs where auto-scraping failed (`jd_source: pending_user_input`):
- Show job title + company + LinkedIn link
- Ask user to paste JD text for that job
- If user skips → mark that job as skipped in working memory
- Collect all JDs before starting the tailoring loop

**B5. Proceed to Step 8 (Batch Loop)**

### Step 1 — Parse the Master Resume

Extract ALL information:

| Category | What to Extract |
|----------|----------------|
| **Contact Info** | Name, email, phone, LinkedIn URL, location |
| **Summary** | Existing summary text |
| **Skills** | Every category and every skill — full inventory |
| **Work Experience** | Each role: title, company, dates, location, all bullets, tech stacks |
| **Projects** | Name, description, technologies, outcomes |
| **Education** | Degrees, institutions, dates, grades |
| **Certifications** | Name, issuer, date |
| **Right to Work** | Visa/work authorisation if present — always preserve |

### Step 2 — Parse the Job Description

Extract:
1. Job title and company name
2. Required hard skills (tools, languages, frameworks, platforms)
3. Preferred/nice-to-have skills
4. Soft skills and domain keywords
5. Years of experience required
6. Key responsibilities (verbs + outcomes)
7. Industry/domain terms and sector-specific language

### Step 3 — Skill Matching

Build a match matrix:

| JD Requirement | Candidate Has? | Evidence in Resume | Match Type |
|----------------|---------------|-------------------|------------|
| {skill} | Yes / No | {role or section} | Hard / Soft / Domain |

**CRITICAL RULES:**
- `No` for any skill not in the master resume — never fabricate
- Use JD's exact phrasing for matched synonyms (e.g. JD says "Kubernetes" → use "Kubernetes" even if resume says "K8s")
- Skills with `No` are **never added** to the output, even if prominent in the JD
- Flag unmatched skills as gaps in the report — do not hide them
- The summary must only contain skills and experience the candidate actually has

Report to user:
> "{Name} vs {Role} at {Company}: {X}/{Y} required matched, {A}/{B} preferred matched. Gaps: [list]."

### Step 4 — Generate Tailored Resume

**ATS FORMAT RULES — MANDATORY:**
- **No tables** — not in headers, skills, or anywhere in the resume
- **No text boxes, columns, or graphics** — single-column flow only
- **Standard section headings** — use exactly: Professional Summary, Skills, Work Experience, Education, Certifications, Projects, Right to Work
- **No headers/footers** — name and contact go in body text at the top
- **Plain bullet points** — standard `•` or `-`, no custom symbols
- **Standard fonts only** — Calibri, Arial, or Times New Roman in the .docx
- **No underlining** except hyperlinks — use **bold** for emphasis
- **File format** — `.docx` (not `.pdf`) unless user explicitly requests PDF
- **Consistent date format** — `MMM YYYY` throughout (e.g. Jan 2023)
- **No first-person pronouns** — no "I", "my", "me"
- **1–2 pages maximum** — trim aggressively per career profile constraints

Also follow the [ATS guidelines reference](./references/ats-guidelines.md) strictly.

#### Contact Info
- Keep exactly as in the master resume — do not alter name, email, phone, or LinkedIn URL

#### Professional Summary (2-3 sentences)
- Open with accurate years of experience + role identity matching the JD title
- Weave in the top 3-5 JD-matched skills naturally (do not force-fit)
- End with a value statement tied to the JD's primary responsibility
- Never include skills the candidate does not have
- **NEVER use the word "Kubernetes" in the Professional Summary** (use "container orchestration" or omit)
- If the JD is a Data Scientist role and the candidate has no relevant data science work experience, keep the summary neutral and skill-focused — do not claim data scientist experience that isn't there

#### Skills Section — KEY RULES
- **Include ONLY skills directly relevant to this specific role** — trim aggressively
- Keep skills that directly match JD requirements or demonstrate relevant breadth
- **Remove entire skill categories** if they score zero relevance to the JD (e.g. drop deep ML tools for an ops role, drop DevOps tools for a finance/data analyst role)
- Within each category: JD-matched skills listed first
- Use the JD's exact phrasing for matched skills
- Group logically: lead with the most JD-relevant category first
- A skill category with only 1-2 entries may be merged or removed for conciseness
- **Minimum 3 categories always shown**

#### Work Experience
- Keep all roles (reverse chronological) **only if at least one bullet is JD-relevant**
- If an older role has zero relevant bullets for this JD, **omit that role entirely**
- Current role: **max 10 bullets**, all JD-relevant; must fit within page 1
- Older roles: max 4 bullets each, only JD-relevant ones
- Rewrite bullets: **Action Verb + What + How/With What + Measurable Result**
- Front-load JD keywords into the first 2 bullets of each role
- Enhance bullets with JD language — but **never change facts or fabricate metrics**
- **Never include a bullet just because it's in the master resume** — every bullet must connect to the JD
- Tech stack lines: keep only technologies relevant to the JD

#### Section Order (mandatory)
Professional Summary → Skills → Work Experience → Education → Projects → Certifications → Right to Work

- **Projects appear AFTER Education**, not before
- Projects are optional — drop entirely before shortening experience bullets if 2-page limit is at risk

#### Projects
- **Maximum 2 projects** — only include if they demonstrate JD-relevant skills AND there is space within the 2-page limit
- Score each project against the JD; include only if relevance score > 0
- Drop academic projects for operational/technical support/platform engineering roles
- If the 2-page limit is at risk, drop all projects before shortening experience bullets
- **Projects are not mandatory** — omit entirely if not needed

#### Education
- Keep institution, degree, dates — always
- **Omit the Modules line** unless the JD contains keywords that directly match the module names (e.g. JD mentions "NLP" → include only if NLP is in modules)
- Never list modules as a default — they waste space and reduce ATS relevance score

#### Certifications
- List JD-relevant certs first
- Keep all Splunk certs (consistently relevant to Pravin's current track)

#### Right to Work
- **ALWAYS include** if present in the master resume — critical for Irish employers; never omit

### Step 5 — Save Tailored Markdown

Save to:
```
.github/Users/{UserName}/{UserName}_Resume_{Company}.md
```

### Step 6 — Generate .docx

Determine output folder name from JD parsing:
- **Company name** takes priority if clearly identifiable from JD
- **Role title** as fallback if company name unclear or missing

Create output folder structure and run conversion script:

```bash
# Create Resumes subfolder structure
mkdir -p "{UserName}/Resumes/{Company|Role}"

# Generate .docx in the Resumes subfolder
# 3rd arg = user's full name → stamped as .docx Author in core properties
python .github/skills/resume-tailor/scripts/md-to-docx.py \
  ".github/Users/{UserName}/{UserName}_Resume_{Company}.md" \
  "{UserName}/Resumes/{Company|Role}" \
  "{User Full Name}"
```

The script produces:
- Name in large navy heading (centred)
- Contact line with **clickable LinkedIn hyperlink** (centred)
- Section headings in navy with bottom border rule (ATS-safe, no graphics)
- Role title bold, date/location in grey italic beneath
- Skill lines: bold category label + plain comma-separated values
- Bullets with consistent indent
- Tech stack lines in small grey italic
- Right to Work line at the footer

Output saved to: `{UserName}/Resumes/{Company|Role}/{UserName}_Resume_{Company}.docx`

### Step 6.5 — Log to Applied History

After generating `.docx`, run `log-application.py` to append a row to `{UserName}/History/resumes_created.xlsx`:

```bash
python .github/skills/resume-tailor/scripts/log-application.py \
  --user "{UserName}" \
  --company "{Company}" \
  --title "{Job Title}" \
  --location "{Location}" \
  --link "{LinkedIn URL}" \
  --resume-file "{output_docx path}" \
  --fit {fit_pct}
```

- Creates `{UserName}/History/` and `applied_jobs.xlsx` if they don't exist
- Appends one row per call — **never overwrites** existing rows
- Columns: Date Applied, Company, Job Title, Location, Job Link (clickable), Resume File, Fit %
- This is the single source of truth for all applications sent

### Step 7 — Review and Iterate

Print summary table of all resumes generated for this user:

> "Tailored resume for **{Role}** at **{Company}** saved:
> - Markdown: `.github/Users/{Name}/{Name}_Resume_{Company}.md`
> - Word: `{Name}/Resumes/{Company|Role}/{Name}_Resume_{Company}.docx`
>
> **All resumes for {Name}:**
>
> | # | Company/Role | File | Date |
> |---|-------------|------|------|
> | 1 | Acme / Data Analyst | `Resumes/Acme/...docx` | 2026-04-10 |
> | 2 | ... | ... | ... |
>
> Want to: 1. Adjust summary  2. Reorder bullets  3. Add/remove sections?"

### Step 8 — Batch Loop

> **Triggered by Step 0.5-B. Skipped in single-job mode.**

Process jobs in chunks of 5 (avoids context window bloat). For each chunk:

**For each job with JD text available:**

a. Print progress: `"Processing {i}/{n}: {title} at {company} (Fit: {fit_pct}%)"`

b. **Step 2 — Parse JD** using `jd_text` from manifest (or user-pasted text)

c. **Step 3 — Skill match** — report: `"{X}/{Y} required matched. Gaps: [list]."`

d. **Step 4 — Generate tailored resume** — parse master resume **once** and reuse for all jobs in batch; do not re-read between jobs

e. **Step 5 — Save .md** to path from manifest `output_md`

f. **Create company context file** at path from manifest `context_file`:
   ```markdown
   # {Company} — {Job Title}

   ## Metadata
   - **Applied**: {YYYY-MM-DD}
   - **Location**: {location}
   - **Job Link**: [{link}]({link})
   - **Fit Score**: {fit_pct}%
   - **Best Matching Role**: {matching_role}
   - **Resume**: [{output_docx}]({output_docx})

   ## Job Description
   {full jd_text}

   ## Match Report
   - **Required matched**: {X}/{Y}
   - **Preferred matched**: {A}/{B}
   - **Gaps**: {list}

   ## Notes
   _(empty — add interview dates, salary, contacts, feedback here)_
   ```
   - Never overwrite if file already exists
   - Create `.github/Users/{UserName}/companies/` dir if missing

g. **Step 6 — Generate .docx** using paths from manifest:
   ```bash
   python .github/skills/resume-tailor/scripts/md-to-docx.py \
     "{output_md}" \
     "{output_folder}" \
     "{user_full_name}"
   ```

h. **Step 6.5 — Log to history** using `log-application.py` (see Step 6.5)

i. If any step fails → log the error and **continue to next job** (do not abort the batch)

**After each chunk of 5:** print progress summary (completed/remaining/failed).

**After all jobs:** print batch summary table:

> "Batch complete — {N} resumes generated, {F} failed, {S} skipped.
>
> | # | Company | Title | Fit % | Status | Output |
> |---|---------|-------|-------|--------|--------|
> | 1 | Acme | Data Analyst | 95% | ✓ Done | Resumes/AcmeCorp/ |
> | 2 | ... | ... | ... | ... | ... |"

## Quality Checklist

Before delivering, verify:

- [ ] No fabricated skills — every skill exists in the master resume
- [ ] No fabricated experience — every bullet reflects actual work done
- [ ] Skills section trimmed to role-relevant categories only; irrelevant categories removed
- [ ] JD keywords in Summary + Skills + Experience
- [ ] No bullet included that has zero relevance to the JD
- [ ] ATS formatting — no tables, columns, graphics; standard headings
- [ ] Bullet formula: Action Verb + Task + Method + Result
- [ ] Consistent dates: MMM YYYY format
- [ ] No first-person pronouns
- [ ] **2 pages maximum** — trim projects first, then older role bullets, then current role bullets
- [ ] Current role fits within page 1
- [ ] LinkedIn URL preserved correctly (not stripped or broken)
- [ ] **Right to Work included** — mandatory for Irish employers
- [ ] **"Kubernetes" NOT in Professional Summary**
- [ ] Projects: max 2, only if JD-relevant AND within 2-page limit
- [ ] Education: modules omitted unless JD keywords match
- [ ] Older roles: max 4 bullets each, only JD-relevant; omit role entirely if zero relevant bullets
- [ ] .docx generated and saved to `{UserName}/Resumes/{Company|Role}/`
- [ ] Applied job logged to `{UserName}/History/resumes_created.xlsx`

## Known Issues & Fixes

| Issue | Fix Applied |
|-------|-------------|
| LinkedIn link rendered as plain text in .docx | `md-to-docx.py` now uses `add_hyperlink()` with proper OOXML relationship — renders as clickable blue underlined link |
| Skill section too verbose (all skills regardless of role) | Step 4 now explicitly requires trimming to JD-relevant skills only |
| Duplicate bullets in master resume after multiple merges | Clean up master resume periodically; deduplicate bullets manually |
| `.docx` saved inside `.github/` | Output dir now under `{UserName}/Resumes/` |
| No record of which jobs were applied to | Step 6.5 uses `log-application.py` — append-only xlsx |
| Agent cannot read `.xlsx` files directly | `batch-job-reader.py` converts Excel → JSON manifest readable by `read_file` |
| LinkedIn job view pages blocked for unauthenticated users | FIXED: Guest API `jobPosting/{id}` works; JDs now auto-scraped in both `scrape-linkedin-jobs.py` and `batch-job-reader.py` |
| Batch interrupted mid-run | Re-run `batch-job-reader.py --manifest path` to skip completed jobs; skip check on `Resumes/` also catches previously generated .docx files |
