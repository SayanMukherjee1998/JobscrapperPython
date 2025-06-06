# Path: main.py

from parser.resume_parser import extract_resume_skills
from scraper.company_scraper import scrape_all_companies
from utils.filters import is_relevant_job
from utils.filters import filter_recent_jobs
from db.models import insert_filtered_job, insert_posted_today, clear_posted_today
from utils.logger import logger
import time
import concurrent.futures

if __name__ == "__main__":
    start = time.time()

    print("📄 Extracting skills from resume...")
    resume_skills = extract_resume_skills()
    print(f"✅ Extracted resume skills: {resume_skills}")

    print("🚀 Launching company scraper...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        company_future = executor.submit(scrape_all_companies, resume_skills)

        while not company_future.done():
            print(f"⏳ Progress: Company scraping in progress...")
            time.sleep(1)

        company_jobs = company_future.result()

    print(f"🏢 Company jobs: {len(company_jobs)}")
    print(f"📦 Total jobs scraped: {len(company_jobs)}")

    print("🧠 Filtering jobs based on resume keywords and experience...")
    final_jobs = [job for job in company_jobs if is_relevant_job(job, resume_skills)]
    print(f"✅ Jobs after filtering: {len(final_jobs)}")

    for i, job in enumerate(final_jobs, start=1):
        insert_filtered_job(job)
        if i % 10 == 0 or i == len(final_jobs):
            print(f"💾 Progress: Inserted {i}/{len(final_jobs)} jobs to FilteredJobs")

    print("🕒 Detecting jobs posted today...")
    today_jobs = filter_recent_jobs(final_jobs, days=1)
    clear_posted_today()
    for i, job in enumerate(today_jobs, start=1):
        insert_posted_today(job)
        if i % 5 == 0 or i == len(today_jobs):
            print(f"📬 Progress: Marked {i}/{len(today_jobs)} jobs as posted today")

    print(f"🏁 Done in {(time.time() - start):.2f} seconds!")
