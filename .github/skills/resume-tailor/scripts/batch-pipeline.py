#!/usr/bin/env python3
"""
batch-pipeline.py — Autonomous batch resume tailoring pipeline.

Reads a manifest JSON (from batch-job-reader.py), processes each job
deterministically via tailor-resume.py, logs results to resumes_created.xlsx.

Usage:
    python batch-pipeline.py \
        --manifest Pravin/JobSearch/batch_manifest_20260413_122745.json \
        [--min-fit 50] \
        [--max-bullets 15] \
        [--llm-polish-above 75] \
        [--dry-run]

Requirements:
    pip install python-docx openpyxl
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import date
from pathlib import Path


def load_manifest(manifest_path: str) -> dict:
    return json.loads(Path(manifest_path).read_text(encoding='utf-8'))


def job_already_done(job: dict) -> bool:
    """Check if .docx already exists for this job."""
    docx_path = Path(job.get('output_docx', ''))
    return docx_path.exists()


def run_tailor(job: dict, master_path: str, author: str, max_bullets: int,
               max_older_bullets: int = 4, max_projects: int = 2) -> dict:
    """Run tailor-resume.py for a single job entry. Returns report dict."""
    # Import directly for speed (avoid subprocess overhead)
    script_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(script_dir))

    from importlib import import_module
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        'tailor_resume', script_dir / 'tailor-resume.py'
    )
    tailor_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tailor_mod)

    return tailor_mod.tailor_job(
        job=job,
        master_path=master_path,
        author=author,
        max_bullets=max_bullets,
        max_older_bullets=max_older_bullets,
        max_projects=max_projects,
    )


def run_log(user: str, job: dict, report: dict):
    """Call log-application.py to append row to resumes_created.xlsx."""
    script_dir = Path(__file__).resolve().parent
    log_script = script_dir / 'log-application.py'
    python = sys.executable

    cmd = [
        python, str(log_script),
        '--user', user,
        '--company', job['company'],
        '--title', job['title'],
        '--location', job.get('location', ''),
        '--link', job.get('link', ''),
        '--resume-file', report.get('output_docx', ''),
        '--fit', str(job.get('fit_pct', 0)),
    ]
    subprocess.run(cmd, check=False, capture_output=True)


def print_summary_table(results: list):
    """Print a compact summary table."""
    print('\n' + '=' * 80)
    print(f"{'#':<4} {'Company':<28} {'Title':<25} {'Fit':<5} {'Match':<6} {'Status'}")
    print('-' * 80)
    for r in results:
        status_icon = '✓' if r['status'] == 'completed' else '✗' if r['status'] == 'failed' else '⊘'
        print(
            f"{r['index']:<4} {r['company'][:27]:<28} {r['title'][:24]:<25} "
            f"{r['fit']:<5} {r.get('match_pct', '-'):<6} {status_icon} {r['status']}"
        )
    print('=' * 80)

    completed = sum(1 for r in results if r['status'] == 'completed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    needs_review = sum(1 for r in results if r.get('needs_review'))
    print(f"\nCompleted: {completed}  Failed: {failed}  Skipped: {skipped}  Needs LLM review: {needs_review}")


def main():
    parser = argparse.ArgumentParser(description='Autonomous batch resume pipeline')
    parser.add_argument('--manifest', required=True, help='Path to manifest JSON')
    parser.add_argument('--min-fit', type=int, default=0,
                        help='Skip jobs below this fit %% (default: process all)')
    parser.add_argument('--max-bullets', type=int, default=10,
                        help='Max current-role bullets per resume (default: 10)')
    parser.add_argument('--max-older-bullets', type=int, default=4,
                        help='Max bullets for older roles (default: 4)')
    parser.add_argument('--max-projects', type=int, default=2,
                        help='Max projects to include if JD-relevant (default: 2)')
    parser.add_argument('--llm-polish-above', type=int, default=75,
                        help='Flag jobs >= this fit %% for LLM review (default: 75)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print plan without generating any files')
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    jobs = manifest.get('jobs', [])
    user = manifest.get('user', 'Unknown')
    author = manifest.get('user_full_name', '')
    master_path = manifest.get('master_resume', '')

    if not Path(master_path).exists():
        print(f"ERROR: Master resume not found: {master_path}")
        sys.exit(1)

    # Filter by min fit
    if args.min_fit > 0:
        jobs = [j for j in jobs if j.get('fit_pct', 0) >= args.min_fit]

    total = len(jobs)
    print(f"Batch pipeline: {total} jobs to process (user={user}, min_fit={args.min_fit}%)")
    print(f"Master: {master_path}")
    print(f"LLM polish threshold: >={args.llm_polish_above}%")
    print()

    if args.dry_run:
        print("DRY RUN — no files will be generated:\n")
        for j in jobs:
            exists = '(exists)' if job_already_done(j) else '(new)'
            print(f"  [{j.get('index', '?')}] {j['company']} — {j['title']} (Fit: {j.get('fit_pct')}%) {exists}")
        print(f"\nTotal: {total} jobs")
        return

    results = []
    start_time = time.time()

    for i, job in enumerate(jobs, 1):
        idx = job.get('index', i)
        company = job.get('company', '?')
        title = job.get('title', '?')
        fit = job.get('fit_pct', 0)

        result_entry = {
            'index': idx, 'company': company, 'title': title,
            'fit': f"{fit}%", 'status': 'pending',
        }

        # Skip if already done
        if job_already_done(job):
            print(f"[{i}/{total}] SKIP (exists): {company} — {title}")
            result_entry['status'] = 'skipped'
            results.append(result_entry)
            continue

        # Skip if below min fit
        if fit < args.min_fit:
            result_entry['status'] = 'skipped'
            results.append(result_entry)
            continue

        print(f"[{i}/{total}] Processing: {company} — {title} (Fit: {fit}%)")

        try:
            report = run_tailor(job, master_path, author, args.max_bullets,
                                args.max_older_bullets, args.max_projects)
            result_entry['status'] = 'completed'
            result_entry['match_pct'] = f"{report.get('match_pct', 0)}%"
            result_entry['gaps'] = report.get('gaps', [])

            # Flag for LLM polish
            if fit >= args.llm_polish_above:
                result_entry['needs_review'] = True
                print(f"         → Flagged for LLM review (fit={fit}%)")

            # Log to xlsx
            run_log(user, job, report)
            print(f"         → Done (match: {report.get('match_pct', 0)}%)")

        except Exception as e:
            result_entry['status'] = 'failed'
            result_entry['error'] = str(e)
            print(f"         → FAILED: {e}")

        results.append(result_entry)

    elapsed = time.time() - start_time
    print_summary_table(results)
    print(f"\nElapsed: {elapsed:.1f}s")

    # Save results JSON alongside manifest
    results_path = Path(args.manifest).parent / 'batch_results.json'
    results_path.write_text(json.dumps({
        'manifest': args.manifest,
        'processed_at': date.today().isoformat(),
        'elapsed_seconds': round(elapsed, 1),
        'results': results,
    }, indent=2), encoding='utf-8')
    print(f"Results: {results_path}")


if __name__ == '__main__':
    main()
