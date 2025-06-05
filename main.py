# Path: main.py

from parser.resume_parser import extract_resume_skills
from scraper.linkedin_scraper import scrape_all_linkedin_jobs
from scraper.company_scraper import scrape_all_companies
from utils.filters import filter_and_score_jobs, filter_recent_jobs
from db.models import insert_filtered_job, insert_posted_today, clear_posted_today
from utils.logger import logger
import time
import concurrent.futures

if __name__ == "__main__":
    start = time.time()

    print("📄 Extracting skills from resume...")
    logger.info("📄 Extracting skills from resume")
    resume_skills = extract_resume_skills()
    print(f"✅ Extracted skills: {resume_skills}")
    logger.info(f"✅ Skills extracted: {resume_skills}")

    print("🔍 Scraping LinkedIn and Company jobs concurrently...")
    logger.info("🔍 Starting LinkedIn and Company scraping concurrently...")

    # Run LinkedIn and Company scraping concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_linkedin = executor.submit(scrape_all_linkedin_jobs)
        future_companies = executor.submit(scrape_all_companies)

        linkedin_jobs = future_linkedin.result()
        company_jobs = future_companies.result()

    print(f"✅ LinkedIn jobs scraped: {len(linkedin_jobs)}")
    print(f"✅ Company jobs scraped: {len(company_jobs)}")

    all_jobs = linkedin_jobs + company_jobs
    print(f"📦 Total jobs scraped: {len(all_jobs)}")
    logger.info(f"🔎 Total jobs scraped: {len(all_jobs)}")

    print("🧠 Scoring and filtering jobs...")
    logger.info("🧠 Filtering and scoring all jobs...")
    final_jobs = filter_and_score_jobs(all_jobs, resume_skills)
    print(f"✅ Jobs after filtering & scoring: {len(final_jobs)}")

    for job in final_jobs:
        insert_filtered_job(job)
    print(f"💾 Inserted {len(final_jobs)} jobs to FilteredJobs")
    logger.info(f"💾 Inserted {len(final_jobs)} jobs to FilteredJobs")

    print("🕒 Detecting jobs posted today...")
    logger.info("🕒 Identifying today's jobs...")
    today_jobs = filter_recent_jobs(final_jobs, days=1)
    clear_posted_today()
    for job in today_jobs:
        insert_posted_today(job)
    print(f"✅ Jobs posted today: {len(today_jobs)}")
    logger.info(f"✅ Jobs posted today: {len(today_jobs)}")

    duration = time.time() - start
    print(f"🏁 Done in {duration:.2f} seconds!")
    logger.info(f"🏁 Script completed in {duration:.2f} seconds")
