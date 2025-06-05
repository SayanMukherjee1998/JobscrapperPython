from config import POSTED_TODAY_COLLECTION, FILTERED_JOBS_COLLECTION
from db.database import db

def insert_filtered_job(job):
    if not db[FILTERED_JOBS_COLLECTION].find_one({"url": job["url"]}):
        db[FILTERED_JOBS_COLLECTION].insert_one(job)

def insert_posted_today(job):
    db[POSTED_TODAY_COLLECTION].insert_one(job)

def clear_posted_today():
    db[POSTED_TODAY_COLLECTION].delete_many({})

def get_recent_jobs():
    return list(db[FILTERED_JOBS_COLLECTION].find())

def get_jobs_posted_today():
    return list(db[POSTED_TODAY_COLLECTION].find())
