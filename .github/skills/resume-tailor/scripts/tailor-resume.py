#!/usr/bin/env python3
"""
tailor-resume.py — Deterministic resume tailoring → .docx (no .md intermediate).

Parses the master resume, extracts JD keywords from a manifest job entry,
scores/selects bullets by keyword overlap, reorders skills, and writes
.docx directly via md-to-docx formatting engine.

Usage:
    python tailor-resume.py \
        --manifest-entry job_entry.json \
        --master .github/Users/Pravin/Pravin_Resume.md \
        --output Pravin/Resumes/AcmeCorp/Pravin_Resume_AcmeCorp.docx \
        --author "Pravin Kumar Durairaj" \
        [--context-file .github/Users/Pravin/companies/AcmeCorp.md] \
        [--max-bullets 15]

Requirements:
    pip install python-docx
"""

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path


# ── Stop words ────────────────────────────────────────────────────────────────

STOP_WORDS = frozenset({
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'shall', 'can',
    'this', 'that', 'these', 'those', 'it', 'its', 'we', 'our', 'you',
    'your', 'they', 'them', 'their', 'he', 'she', 'him', 'her', 'who',
    'which', 'what', 'when', 'where', 'how', 'all', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'because',
    'as', 'if', 'then', 'else', 'while', 'also', 'well', 'back', 'much',
    'any', 'new', 'us', 'me', 'my', 'etc', 'vs', 'via',
    'able', 'across', 'along', 'among', 'around', 'between', 'like',
    'over', 'including', 'within', 'without', 'using', 'based', 'related',
    'role', 'work', 'working', 'experience', 'strong', 'good', 'knowledge',
    'skills', 'ability', 'understanding', 'ensure', 'provide', 'support',
    'team', 'teams', 'business', 'company', 'years', 'year', 'minimum',
    'required', 'preferred', 'ideal', 'candidate', 'responsibilities',
    'requirements', 'qualifications', 'benefits', 'opportunity',
    'looking', 'seeking', 'join', 'part', 'time', 'full', 'must',
})


# ── Keyword extraction ────────────────────────────────────────────────────────

def extract_keywords(text: str) -> Counter:
    """Extract meaningful keywords from text, return frequency counter."""
    text = text.lower()
    tokens = re.findall(r'[a-z][a-z0-9.+#\-]*(?:/[a-z0-9.+#\-]+)*', text)
    keywords = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]
    return Counter(keywords)


# ── Resume parser ─────────────────────────────────────────────────────────────

def parse_master_resume(md_path: str) -> dict:
    """Parse master resume .md into structured sections."""
    lines = Path(md_path).read_text(encoding='utf-8').splitlines()

    result = {
        'name': '', 'contact': '', 'summary': '', 'skills': [],
        'experience': [], 'projects': [], 'education': [],
        'certifications': [], 'right_to_work': '',
    }

    current_section = None
    current_entry = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line in ('---', '***', '___'):
            i += 1
            continue

        # H1 → name
        if line.startswith('# ') and not result['name']:
            result['name'] = line[2:].strip()
            i += 1
            continue

        # Contact line
        if result['name'] and not result['contact'] and line.startswith('**') and '|' in line:
            result['contact'] = line
            i += 1
            continue

        # H2 → section
        if line.startswith('## '):
            section_name = line[3:].strip().lower()
            if 'summary' in section_name:
                current_section = 'summary'
            elif 'skill' in section_name:
                current_section = 'skills'
            elif 'experience' in section_name:
                current_section = 'experience'
            elif 'project' in section_name:
                current_section = 'projects'
            elif 'education' in section_name:
                current_section = 'education'
            elif 'certification' in section_name:
                current_section = 'certifications'
            else:
                current_section = section_name
            current_entry = None
            i += 1
            continue

        # H3 → sub-entry
        if line.startswith('### '):
            entry_header = line[4:].strip()

            # Peek for date line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            date_line = ''
            if j < len(lines) and lines[j].strip().startswith('**'):
                date_line = lines[j].strip()
                i = j  # advance past date line

            if current_section == 'experience':
                current_entry = {
                    'header': entry_header, 'date_line': date_line,
                    'bullets': [], 'tech_stack': [],
                }
                result['experience'].append(current_entry)
            elif current_section == 'projects':
                current_entry = {
                    'header': entry_header, 'description': '',
                    'bullets': [], 'tech_stack': [],
                }
                result['projects'].append(current_entry)
            elif current_section == 'education':
                current_entry = {
                    'header': entry_header, 'date_line': date_line, 'modules': '',
                }
                result['education'].append(current_entry)

            i += 1
            continue

        if not line:
            i += 1
            continue

        # Right to work — check FIRST before section routing (it appears after certifications)
        if 'right to work' in line.lower() or 'stamp 4' in line.lower():
            result['right_to_work'] = line
            i += 1
            continue

        # Content routing
        if current_section == 'summary':
            result['summary'] = (result['summary'] + ' ' + line).strip()

        elif current_section == 'skills' and line.startswith('**'):
            result['skills'].append(line)

        elif current_section in ('experience', 'projects') and current_entry:
            if line.startswith('- '):
                current_entry['bullets'].append(line[2:].strip())
            elif line.startswith('*') and line.endswith('*') and 'Tech Stack' in line:
                current_entry['tech_stack'].append(line)
            elif line.startswith('*') and line.endswith('*') and 'Tech Skills' in line:
                pass  # skip broken tech skills line
            elif current_section == 'projects' and not current_entry.get('description'):
                current_entry['description'] = line

        elif current_section == 'education' and current_entry:
            if 'module' in line.lower() and ':' in line:
                current_entry['modules'] = line

        elif current_section == 'certifications':
            if line.startswith('- '):
                result['certifications'].append(line[2:].strip())

        i += 1

    return result


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_text(text: str, jd_keywords: Counter) -> float:
    text_lower = text.lower()
    return sum(freq for kw, freq in jd_keywords.items() if kw in text_lower)


# Terms banned from Professional Summary regardless of JD
SUMMARY_BANNED = frozenset({'kubernetes', 'k8s'})


def select_bullets(bullets: list, jd_keywords: Counter, max_bullets: int,
                   min_score: float = 0) -> list:
    """Select top N bullets by JD keyword overlap, preserving original order for ties.

    Bullets with score < min_score are dropped unless there aren't enough to fill max_bullets.
    """
    scored = [(i, b, score_text(b, jd_keywords)) for i, b in enumerate(bullets)]
    # Filter by min_score first; fall back to all if too few remain
    above = [x for x in scored if x[2] >= min_score]
    pool = above if len(above) >= 3 else scored  # keep at least 3
    pool.sort(key=lambda x: (-x[2], x[0]))
    selected = pool[:max_bullets]
    selected.sort(key=lambda x: x[0])
    return [b for _, b, _ in selected]


def filter_skills(skills: list, jd_keywords: Counter, min_score: float = 0) -> list:
    """Reorder skill categories by JD relevance; drop categories scoring 0.

    Always keeps the top 3 categories so the section isn't empty.
    """
    scored = [(s, score_text(s, jd_keywords)) for s in skills]
    scored.sort(key=lambda x: -x[1])
    # Keep categories with score > 0; always keep at least top 3
    kept = [s for s, sc in scored if sc > 0]
    if len(kept) < 3:
        kept = [s for s, _ in scored[:3]]
    return kept


def select_projects(projects: list, jd_keywords: Counter, max_projects: int = 2) -> list:
    """Select top projects by JD relevance. Returns at most max_projects.

    Returns empty list if no project scores above 0 (no relevance to JD).
    Academic-only projects are deprioritised for non-research roles.
    """
    def project_score(proj):
        text = proj['header'] + ' ' + proj.get('description', '') + ' ' + ' '.join(proj.get('bullets', []))
        return score_text(text, jd_keywords)

    scored = [(proj, project_score(proj)) for proj in projects]
    scored.sort(key=lambda x: -x[1])
    # Only include projects that actually have relevance
    relevant = [(p, sc) for p, sc in scored if sc > 0]
    return [p for p, _ in relevant[:max_projects]]


# ── Page budget enforcement ───────────────────────────────────────────────

def estimate_lines(md_content: str) -> int:
    """Estimate effective lines in markdown accounting for wrapping at 80 chars.

    Returns approximate line count for a 2-column page layout (80-char width).
    Wrapping factor ~1.3x for Calibri Light 11pt with margins.
    """
    non_empty_lines = [l for l in md_content.split('\n') if l.strip()]
    # Long lines wrap; apply conservative wrapping factor
    total_chars = sum(len(l) for l in non_empty_lines)
    effective_lines = len(non_empty_lines) + (total_chars // 80)
    return int(effective_lines * 1.3)  # Account for line height


def trim_to_budget(
    md_content: str,
    resume: dict,
    jd_keywords: Counter,
    max_bullets: int = 10,
    max_older_bullets: int = 4,
    max_projects: int = 2,
) -> str:
    """Iteratively trim resume content to fit ~2-page budget (~100 effective lines).

    Trim priority: 1. Projects  2. Older role bullets  3. Current role bullets
    """
    budget_lines = 100
    current_lines = estimate_lines(md_content)

    if current_lines <= budget_lines:
        return md_content

    # Start trimming: projects first
    working_max_projects = max_projects
    working_max_older = max_older_bullets
    working_max_bullets = max_bullets

    attempts = 0
    max_attempts = 15  # Prevent infinite loops

    while current_lines > budget_lines and attempts < max_attempts:
        if working_max_projects > 0:
            working_max_projects -= 1
        elif working_max_older > 1:
            working_max_older -= 1
        elif working_max_bullets > 6:  # Floor at 6 bullets for current role
            working_max_bullets -= 1
        else:
            break  # Stop trimming to avoid gutting the resume

        md_content = build_tailored_md(
            resume, jd_keywords, '',
            max_murex_bullets=working_max_bullets,
            max_older_bullets=working_max_older,
            max_projects=working_max_projects,
        )
        current_lines = estimate_lines(md_content)
        attempts += 1

    if current_lines > budget_lines:
        print(f"⚠ Resume estimate: ~{estimate_lines(md_content) // 50 + 1} pages (target: 2). "
              f"Consider reviewing and manually trimming sections.")

    return md_content


def clean_summary(summary: str) -> str:
    """Strip banned words from summary text."""
    words = summary.split()
    cleaned = [w for w in words if w.lower().strip('.,;:()') not in SUMMARY_BANNED]
    return ' '.join(cleaned)


def modules_match_jd(modules_line: str, jd_keywords: Counter) -> bool:
    """Return True only if education modules contain JD-relevant keywords."""
    if not modules_line:
        return False
    return score_text(modules_line, jd_keywords) > 0


# ── Match report ──────────────────────────────────────────────────────────────

def generate_match_report(jd_keywords: Counter, resume_text: str) -> dict:
    resume_lower = resume_text.lower()
    matched, gaps = [], []
    for kw, _ in jd_keywords.most_common(30):
        (matched if kw in resume_lower else gaps).append(kw)
    total = len(matched) + len(gaps)
    return {
        'total_checked': total,
        'matched': matched,
        'matched_count': len(matched),
        'gaps': gaps,
        'gap_count': len(gaps),
        'match_pct': round(len(matched) / max(total, 1) * 100),
    }


# ── Tailored markdown builder ────────────────────────────────────────────────

def build_tailored_md(
    resume: dict,
    jd_keywords: Counter,
    matching_role: str,
    max_murex_bullets: int = 10,
    max_older_bullets: int = 4,
    max_projects: int = 2,
) -> str:
    """Build a tailored resume markdown string in memory."""
    lines = []

    # Name + contact
    lines.append(f"# {resume['name']}")
    lines.append('')
    lines.append(resume['contact'])
    lines.append('')
    lines.append('---')
    lines.append('')

    # Summary — clean banned words (e.g. kubernetes)
    lines.append('## Professional Summary')
    lines.append('')
    lines.append(clean_summary(resume['summary']))
    lines.append('')
    lines.append('---')
    lines.append('')

    # Skills — filter to relevant categories only
    relevant_skills = filter_skills(resume['skills'], jd_keywords)
    lines.append('## Skills')
    lines.append('')
    for s in relevant_skills:
        lines.append(s)
    lines.append('')
    lines.append('---')
    lines.append('')

    # Work Experience
    lines.append('## Work Experience')
    lines.append('')
    for idx, exp in enumerate(resume['experience']):
        if idx == 0:
            # Current role: select top N by JD relevance with min score filter
            selected = select_bullets(exp['bullets'], jd_keywords, max_murex_bullets, min_score=1)
        else:
            # Older roles: max 4 bullets, only JD-relevant ones
            selected = select_bullets(exp['bullets'], jd_keywords, max_older_bullets, min_score=1)
            if not selected:
                # If nothing is relevant, skip this role entirely
                continue

        lines.append(f"### {exp['header']}")
        if exp['date_line']:
            lines.append(exp['date_line'])
        lines.append('')
        for b in selected:
            lines.append(f"- {b}")
        lines.append('')
        for ts in exp['tech_stack']:
            lines.append(ts)
        lines.append('')

    lines.append('---')
    lines.append('')

    # Education — modules only if JD-relevant keywords found
    if resume['education']:
        lines.append('## Education')
        lines.append('')
        for edu in resume['education']:
            lines.append(f"### {edu['header']}")
            if edu['date_line']:
                lines.append(edu['date_line'])
            lines.append('')
            if edu.get('modules') and modules_match_jd(edu['modules'], jd_keywords):
                lines.append(edu['modules'])
            lines.append('')
        lines.append('---')
        lines.append('')

    # Projects — max 2, only if JD-relevant, AFTER Education (space permitting)
    relevant_projects = select_projects(resume['projects'], jd_keywords, max_projects)
    if relevant_projects:
        lines.append('## Projects')
        lines.append('')
        for proj in relevant_projects:
            lines.append(f"### {proj['header']}")
            if proj['description']:
                lines.append(proj['description'])
            lines.append('')
            for b in proj['bullets']:
                lines.append(f"- {b}")
            lines.append('')
            for ts in proj['tech_stack']:
                lines.append(ts)
            lines.append('')
        lines.append('---')
        lines.append('')

    # Certifications
    if resume['certifications']:
        lines.append('## Certifications')
        lines.append('')
        for c in resume['certifications']:
            lines.append(f"- {c}")
        lines.append('')
        lines.append('---')
        lines.append('')

    # Right to work
    if resume['right_to_work']:
        lines.append(resume['right_to_work'])
        lines.append('')

    return '\n'.join(lines)


# ── Context file generator ────────────────────────────────────────────────────

def generate_context_md(job: dict, match_report: dict) -> str:
    lines = [
        f"# Company Context — {job['company']}",
        '',
        '## Job Details',
        f"- **Company:** {job['company']}",
        f"- **Title:** {job['title']}",
        f"- **Location:** {job['location']}",
        f"- **Link:** [{job['link']}]({job['link']})",
        f"- **Fit:** {job['fit_pct']}%",
        f"- **Matching Role:** {job.get('matching_role', 'N/A')}",
        '',
        '## Match Report',
        f"- **Keywords checked:** {match_report['total_checked']}",
        f"- **Matched:** {match_report['matched_count']} ({match_report['match_pct']}%)",
        f"- **Gaps:** {match_report['gap_count']}",
        f"- **Top matches:** {', '.join(match_report['matched'][:10])}",
        f"- **Key gaps:** {', '.join(match_report['gaps'][:10])}",
        '',
        '## Job Description',
        '',
        job.get('jd_text', 'N/A'),
        '',
    ]
    return '\n'.join(lines)


# ── Core function (importable) ────────────────────────────────────────────────

def tailor_job(
    job: dict,
    master_path: str,
    author: str = None,
    max_bullets: int = 10,
    max_older_bullets: int = 4,
    max_projects: int = 2,
    resume_cache: dict = None,
) -> dict:
    """
    Tailor a resume for one job entry and generate .docx + context.

    Args:
        job: manifest job entry dict (must have jd_text, output_docx, context_file, etc.)
        master_path: path to master resume .md
        author: author name for .docx metadata
        max_bullets: max bullets for current/most-recent role
        max_older_bullets: max bullets for older roles (default 4)
        max_projects: max projects to include (default 2, only if JD-relevant)
        resume_cache: optional pre-parsed resume dict (avoids re-parsing for batch)

    Returns:
        dict with keys: output_docx, context_file, match_pct, matched, total, gaps, status
    """
    # Parse master resume (or reuse cache)
    resume = resume_cache or parse_master_resume(master_path)

    # Extract JD keywords
    jd_text = job.get('jd_text', '')
    jd_keywords = extract_keywords(jd_text)
    matching_role = job.get('matching_role', '')

    # Build tailored markdown in memory
    tailored_md = build_tailored_md(
        resume, jd_keywords, matching_role,
        max_murex_bullets=max_bullets,
        max_older_bullets=max_older_bullets,
        max_projects=max_projects,
    )

    # Apply page budget trim (enforce ~2-page limit)
    tailored_md = trim_to_budget(
        tailored_md, resume, jd_keywords,
        max_bullets, max_older_bullets, max_projects,
    )

    # Generate match report
    match_report = generate_match_report(jd_keywords, tailored_md)

    # Load md-to-docx engine
    script_dir = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('md_to_docx', script_dir / 'md-to-docx.py')
    md_to_docx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(md_to_docx)

    # Generate .docx
    output_docx = job.get('output_docx', '')
    resolved_author = author or resume['name']
    md_to_docx.check_dependency()
    md_to_docx.build_docx_from_string(tailored_md, output_docx, resolved_author)

    # Save context file
    context_file = job.get('context_file', '')
    if context_file:
        ctx_path = Path(context_file)
        ctx_path.parent.mkdir(parents=True, exist_ok=True)
        ctx_path.write_text(generate_context_md(job, match_report), encoding='utf-8')

    return {
        'output_docx': output_docx,
        'context_file': context_file,
        'match_pct': match_report['match_pct'],
        'matched': match_report['matched_count'],
        'total': match_report['total_checked'],
        'gaps': match_report['gaps'],
        'status': 'completed',
    }


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Deterministic resume tailoring → .docx')
    parser.add_argument('--manifest-entry', required=True,
                        help='Path to JSON file with single job entry')
    parser.add_argument('--master', required=True, help='Path to master resume .md')
    parser.add_argument('--output', help='Override output .docx path')
    parser.add_argument('--author', default=None, help='Author name for .docx metadata')
    parser.add_argument('--context-file', default=None, help='Override context .md path')
    parser.add_argument('--max-bullets', type=int, default=10,
                        help='Max bullets to keep for current role (default: 10; ATS rule for Pravin/Murex)')
    args = parser.parse_args()

    # Load job entry
    job = json.loads(Path(args.manifest_entry).read_text(encoding='utf-8'))
    if args.output:
        job['output_docx'] = args.output
    if args.context_file:
        job['context_file'] = args.context_file

    report = tailor_job(job, args.master, args.author, args.max_bullets)

    print(f"Output:  {report['output_docx']}")
    print(f"Matched: {report['matched']}/{report['total']} keywords ({report['match_pct']}%)")
    if report['gaps']:
        print(f"Gaps:    {', '.join(report['gaps'][:8])}")

    # Machine-readable report
    print(f"\n__REPORT_JSON__:{json.dumps(report)}")


if __name__ == '__main__':
    main()
