# Path: utils/filters.py

import re
from config import EXPERIENCE
from datetime import datetime, timedelta

# Enhanced relevance checker with experience threshold filtering

def is_relevant_job(job, resume_keywords):
    if isinstance(resume_keywords, dict):
        skills = list(resume_keywords.keys())
    else:
        skills = list(resume_keywords)

    skills = [s.strip().lower() for s in skills if s and isinstance(s, str)]

    title = (job.get("title") or "").lower().strip()
    description = (job.get("description") or "").lower().strip()

    matched = []
    for skill in skills:
        if skill in title or skill in description:
            matched.append(skill)

    if not skills:
        return False  

    match_ratio = len(matched) / len(skills)
    print(f"[DEBUG] Job: '{title[:30]}...' matched {len(matched)}/{len(skills)} ({match_ratio:.0%}) skills: {matched}")

    return match_ratio >= 0.7


def filter_recent_jobs(jobs, days=1):
    cutoff = datetime.now() - timedelta(days=days)
    return [j for j in jobs if j.get("posted_date") and j["posted_date"] >= cutoff]