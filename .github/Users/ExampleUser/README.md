# ExampleUser — Template User Folder

This folder shows the expected structure for a user's master resume files.

## Setup for a New User

1. Copy this directory:
   ```
   .github/Users/ExampleUser/ → .github/Users/{YourName}/
   .claude/Users/ExampleUser/ → .claude/Users/{YourName}/
   ```

2. Create your master resume at `.github/Users/{YourName}/{YourName}_Resume.md`

   Option A — extract from an existing .docx or .pdf:
   ```bash
   python .github/skills/resume-tailor/scripts/extract-resume.py \
     "path/to/Resume.docx" -o ".github/Users/{YourName}/{YourName}_Resume.md"
   ```

   Option B — use the template:
   ```
   .github/skills/resume-tailor/assets/template-markdown.md
   ```

3. Mirror to `.claude/Users/{YourName}/{YourName}_Resume.md`

4. Create your career profile:
   ```
   .github/instructions/career-profile-{YourName}.instructions.md
   .claude/instructions/career-profile-{YourName}.instructions.md
   ```
   (copy from `career-profile-template.instructions.md` and fill in your details)

5. Create output directories:
   ```
   {YourName}/Resumes/
   {YourName}/JobSearch/archive/
   {YourName}/History/
   ```

> Note: All files in `.github/Users/{YourName}/` are gitignored — they contain personal data.
> This README.md file is the only committed file in ExampleUser.
