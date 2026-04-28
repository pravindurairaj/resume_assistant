#!/usr/bin/env python3
"""
run-pipeline.py - One-command end-to-end pipeline.

Chains: scrape-linkedin-jobs.py -> batch-job-reader.py -> batch-pipeline.py.
Resolves --user from CLI / RESUME_USER env / .resume-assistant.toml / "Pravin".

    python run-pipeline.py
    python run-pipeline.py --user Navya --min-fit 60 --skip-scrape
    python run-pipeline.py --skip-scrape --min-fit 90
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

REPO = Path(__file__).resolve().parent
CONFIG_PATH = REPO / ".resume-assistant.toml"

SCRAPER = REPO / ".github/skills/job-scraper/scripts/scrape-linkedin-jobs.py"
READER = REPO / ".github/skills/resume-tailor/scripts/batch-job-reader.py"
PIPELINE = REPO / ".github/skills/resume-tailor/scripts/batch-pipeline.py"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def resolve_default(cli_val, env_key, cfg, cfg_key, fallback):
    if cli_val is not None:
        return cli_val
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]
    if cfg_key in cfg:
        return cfg[cfg_key]
    return fallback


def run_step(name: str, cmd: list[str]) -> None:
    print(f"\n>>> {name}")
    print(f"    {' '.join(cmd)}\n", flush=True)
    rc = subprocess.call(cmd)
    if rc != 0:
        print(f"\nERROR: {name} failed (exit {rc}). Aborting pipeline.")
        sys.exit(rc)


def newest_manifest(user: str) -> Path | None:
    search = REPO / user / "JobSearch"
    candidates = sorted(search.glob("batch_manifest_*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def main():
    cfg = load_config()

    ap = argparse.ArgumentParser(description="One-command resume pipeline")
    ap.add_argument("--user", help="User name (default: env RESUME_USER / config / Pravin)")
    ap.add_argument("--min-fit", type=int, help="Skip jobs below this fit %% (default: config / 50)")
    ap.add_argument("--llm-polish-above", type=int,
                    help="Flag jobs >= this fit %% for LLM review (default: config / 75)")
    ap.add_argument("--skip-scrape", action="store_true",
                    help="Skip scraping; use latest existing JobSearch Excel")
    ap.add_argument("--skip-jd-scrape", action="store_true",
                    help="Pass-through to scraper: title-only scan, fit %% capped at 40")
    ap.add_argument("--dry-run", action="store_true",
                    help="Pass-through to batch-pipeline: print plan, generate nothing")
    args = ap.parse_args()

    user = resolve_default(args.user, "RESUME_USER", cfg, "default_user", "Pravin")
    min_fit = int(resolve_default(args.min_fit, None, cfg, "default_min_fit", 50))
    polish = int(resolve_default(args.llm_polish_above, None, cfg, "default_llm_polish_above", 75))

    print(f"Pipeline: user={user}  min_fit={min_fit}%  llm_polish_above={polish}%")

    py = sys.executable

    if not args.skip_scrape:
        cmd = [py, str(SCRAPER), "--user", user]
        if args.skip_jd_scrape:
            cmd.append("--skip-jd-scrape")
        run_step("Step 1/3: Scrape LinkedIn jobs", cmd)
    else:
        print("\n(Skipping scrape — using existing JobSearch Excel)")

    run_step("Step 2/3: Build manifest",
             [py, str(READER), "--user", user, "--min-fit", str(min_fit)])

    manifest = newest_manifest(user)
    if not manifest:
        print(f"ERROR: no batch_manifest_*.json found in {user}/JobSearch/ after reader step.")
        sys.exit(1)
    print(f"\nManifest: {manifest}")

    cmd = [py, str(PIPELINE), "--manifest", str(manifest),
           "--min-fit", str(min_fit), "--llm-polish-above", str(polish)]
    if args.dry_run:
        cmd.append("--dry-run")
    run_step("Step 3/3: Tailor resumes", cmd)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
