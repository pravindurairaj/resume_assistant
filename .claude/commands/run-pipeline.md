# Run Pipeline

End-to-end pipeline: scrape LinkedIn jobs → build manifest → tailor resumes for every matching job. Wraps `run-pipeline.py`; defaults come from `.resume-assistant.toml` (`default_user`, `default_min_fit`, `default_llm_polish_above`).

## Arguments

All optional. With no arguments, runs the full pipeline for the default user from config.

- `--user Pravin|Navya` — override default user (also reads `RESUME_USER` env var)
- `--min-fit N` — skip jobs below this fit %% (default from config, typically 50)
- `--llm-polish-above N` — flag jobs ≥ this fit %% for LLM review (default from config, typically 75)
- `--skip-scrape` — reuse the latest existing JobSearch Excel instead of re-scraping
- `--skip-jd-scrape` — pass-through to scraper: fast title-only scan (fit capped at 40%%, no JD fetch)
- `--dry-run` — pass-through to batch-pipeline: print plan, generate no files

## Examples

```
/run-pipeline
/run-pipeline --skip-scrape --min-fit 75
/run-pipeline --user Navya --min-fit 60
/run-pipeline --skip-scrape --dry-run
/run-pipeline --skip-jd-scrape
```

## Execution

Run the wrapper via Bash and stream output to chat:

```bash
resume_assistant/Scripts/python run-pipeline.py $ARGUMENTS
```

The wrapper chains three steps and aborts on the first non-zero exit:

1. **Scrape** — `.github/skills/job-scraper/scripts/scrape-linkedin-jobs.py` (skipped with `--skip-scrape`)
2. **Manifest** — `.github/skills/resume-tailor/scripts/batch-job-reader.py` builds `{User}/JobSearch/batch_manifest_{ts}.json`
3. **Tailor** — `.github/skills/resume-tailor/scripts/batch-pipeline.py` deterministically generates one `.docx` per job under `{User}/Resumes/{Co}/` and appends rows to `{User}/History/resumes_created.xlsx`

If any step fails, the wrapper exits non-zero with `ERROR: Step X/3 failed`. Surface that to the user verbatim.

## Output

- `.docx` files: `{User}/Resumes/{Company}/{User}_Resume_{Company}.docx`
- Application log: `{User}/History/resumes_created.xlsx`
- Batch summary: `{User}/JobSearch/batch_results.json`

## Notes

- Use `/job-scraper` if you only want to scrape (no tailoring).
- Use `/resume-tailor Pravin <paste JD>` for one-off single-job tailoring with full agent control.
- This command is for the autonomous batch happy path — minimal hand-holding, ~95%% fewer tokens than the agent-driven `/resume-tailor batch` flow.
