# Path: scraper/company_scraper.py

import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import COMPANY_LIST_PATH, MAX_COMPANY_JOBS
from utils.logger import logger
from utils.filters import is_relevant_job
import os
import zipfile
import shutil

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


def scrape_company_page_dynamic(company, resume_keywords):
    jobs = []
    driver = get_chrome_driver()
    try:
        logger.info(f"🔄 Scraping company: {company['name']}")
        driver.get(company["career_url"])
        cards = driver.find_elements(By.XPATH, '//a[contains(@href,"job") or contains(@href,"careers")]')
        for card in cards[:MAX_COMPANY_JOBS]:
            try:
                title = card.text.strip() or "Unknown Title"
                job = {
                    "source": "company",
                    "title": title,
                    "company": company["name"],
                    "location": "Unknown",
                    "url": card.get_attribute("href"),
                    "posted_date": datetime.now(),
                    "description": title
                }
                if is_relevant_job(job, resume_keywords):
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"⚠️ Parse failed on {company['name']}: {e}")
        logger.info(f"✅ {company['name']}: {len(jobs)} relevant out of {len(cards)} total")
    except Exception as e:
        logger.error(f"❌ Failed {company.get('name', 'unknown')}: {e}")
    finally:
        driver.quit()
    return jobs


def scrape_all_companies(resume_keywords):
    companies = pd.read_csv(COMPANY_LIST_PATH)
    if not {'name', 'career_url'}.issubset(companies.columns):
        raise ValueError("CSV must contain 'name' and 'career_url' headers.")

    companies = companies.to_dict("records")
    results = []
    for comp in companies:
        results.extend(scrape_company_page_dynamic(comp, resume_keywords))
    return results
