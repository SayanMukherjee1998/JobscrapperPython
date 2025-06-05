from datetime import datetime, timedelta
from config import EXPERIENCE
from utils.job_matcher import calculate_match_score, extract_salary, extract_experience

def filter_recent_jobs(jobs, days=1):
    cutoff = datetime.now() - timedelta(days=days)
    return [j for j in jobs if j.get("posted_date") and j["posted_date"] >= cutoff]

def filter_and_score_jobs(jobs, resume_skills):
    seen = set()
    filtered = []

    for job in jobs:
        key = (job["title"], job["company"], job["url"])
        if key in seen:
            continue
        seen.add(key)

        job["match_score"] = calculate_match_score(job.get("description", ""), resume_skills)
        job["experience_required"] = extract_experience(job.get("description", ""))

        # if job["experience_required"] >= EXPERIENCE:
        filtered.append(job)

    filtered.sort(key=lambda j: (-j["match_score"], -j.get("experience_required", 0)))
    return filtered