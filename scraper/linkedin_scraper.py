# Path: scraper/linkedin_scraper.py

import time
import concurrent.futures
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from config import JOB_TITLES, LOCATIONS, MAX_LINKEDIN_PAGES
from utils.logger import logger
from utils.filters import is_relevant_job
import zipfile
import shutil
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])


def get_chrome_driver():
    try:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except zipfile.BadZipFile:
        logger.warning("❌ Corrupt ChromeDriver zip detected. Clearing cache...")
        shutil.rmtree(os.path.expanduser("~/.wdm"), ignore_errors=True)
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def extract_job_details(card):
    try:
        title = card.find_element(By.CSS_SELECTOR, "h3").text.strip()
        company = card.find_element(By.CSS_SELECTOR, "h4").text.strip()
        location = card.find_element(By.CSS_SELECTOR, ".job-search-card__location").text.strip()
        url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        date_elem = card.find_element(By.CSS_SELECTOR, "time")
        posted_date = datetime.fromisoformat(date_elem.get_attribute("datetime"))
        description = f"{title} at {company}"
        return {
            "source": "linkedin",
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "posted_date": posted_date,
            "description": description
        }
    except Exception as e:
        logger.warning(f"LinkedIn card extraction failed: {e}")
        return None


def scrape_linkedin_title_location(title, location, resume_keywords):
    driver = get_chrome_driver()
    jobs = []
    try:
        for page in range(MAX_LINKEDIN_PAGES):
            start = page * 25
            url = f"https://www.linkedin.com/jobs/search/?keywords={title}&location={location}&start={start}"
            logger.info(f"🔄 Scraping LinkedIn: {title} | {location} | Page {page+1}")
            driver.get(url)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list")))
            cards = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")
            print(f"Found {len(cards)} LinkedIn job cards")
            for card in cards:
                job = extract_job_details(card)
                # if job and is_relevant_job(job, resume_keywords):
                jobs.append(job)
            logger.info(f"✅ Page {page+1} complete: {len(cards)} total | {len(jobs)} relevant")
    except TimeoutException:
        logger.warning(f"⚠️ Timeout for {title} @ {location}")
    except Exception as e:
        logger.error(f"❌ LinkedIn error: {e}")
    finally:
        driver.quit()
    return jobs


def scrape_all_linkedin_jobs(resume_keywords):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(scrape_linkedin_title_location, title, location, resume_keywords)
            for title in JOB_TITLES for location in LOCATIONS
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                logger.error(f"LinkedIn thread failed: {e}")
    return results
