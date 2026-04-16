# ExampleUser — Template User Folder

This folder shows the expected structure for a user's master resume files.

## Setup for a New User

The fastest way to onboard a new user is `setup-users.py`:

1. Place `{YourName}_Resume.docx` in the **project root**
2. Run:
   ```bash
   resume_assistant/Scripts/python setup-users.py {YourName}
   ```
   This creates `.github/Users/{YourName}/`, `.claude/Users/{YourName}/`, and all output dirs automatically.

3. Create your career profile (gitignored — fill in locally):
   ```
   .github/instructions/career-profile-{YourName}.instructions.md
   .claude/instructions/career-profile-{YourName}.instructions.md
   ```
   Copy from `career-profile-template.instructions.md` and fill in your details.

> Note: All files in `.github/Users/{YourName}/` are gitignored — they contain personal data.
> This README.md file is the only committed file in ExampleUser.

## Manual alternative (single file extract)

```bash
resume_assistant/Scripts/python .github/skills/resume-tailor/scripts/extract-resume.py \
  "path/to/Resume.docx" -o ".github/Users/{YourName}/{YourName}_Resume.md"
```

Mirror the output to `.claude/Users/{YourName}/{YourName}_Resume.md` as well.
