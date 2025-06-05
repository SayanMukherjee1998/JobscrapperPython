# Path: utils/filters.py

import re
from config import EXPERIENCE
from datetime import datetime, timedelta

# Enhanced relevance checker with experience threshold filtering

def is_relevant_job(job, resume_keywords):
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    experience_text = job.get("experience", "") or description

    # Match at least one resume keyword in title/description
    if not any(re.search(rf"\b{re.escape(k.lower())}\b", title + description) for k in resume_keywords):
        return False

    # Extract numeric experience mentions from text (e.g., "3 years", "5+ years")
    experience_matches = re.findall(r"(\d+)[+\s]*years?", experience_text, re.IGNORECASE)
    if experience_matches:
        max_required = max(int(year) for year in experience_matches)
        if max_required > EXPERIENCE:
            return False

    return True

def filter_recent_jobs(jobs, days=1):
    cutoff = datetime.now() - timedelta(days=days)
    return [j for j in jobs if j.get("posted_date") and j["posted_date"] >= cutoff]