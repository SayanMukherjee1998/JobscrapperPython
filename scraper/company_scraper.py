# scraper/company_scraper.py

import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import COMPANY_LIST_PATH, MAX_COMPANY_JOBS
from utils.logger import logger
from utils.filters import is_relevant_job
import os
import zipfile
import shutil

# Configure Chrome Options
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
    MAX_RETRIES = 3
    
    try:
        logger.info(f"🔄 Scraping company: {company['name']}")
        
        # Retry logic for page loading
        for attempt in range(MAX_RETRIES):
            try:
                driver.get(company["career_url"])
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "job") or contains(text(), "career")]'))
                )
                break
            except (WebDriverException, TimeoutException) as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(2 ** attempt)
                logger.warning(f"🔄 Retry {attempt+1} for {company['name']}")

        # Smart job card detection
        job_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, 
                '//div[contains(@class,"job")] | '
                '//li[contains(@class,"position")] | '
                '//a[contains(@href,"job")][not(contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "career"))]'
            ))
        )
        logger.info(f"🔍 Found {len(job_cards)} potential job elements for {company['name']}")

        for idx, card in enumerate(job_cards[:MAX_COMPANY_JOBS], 1):
            try:
                # Extract job details with multiple fallbacks
                title = card.find_element(By.XPATH,
                    './/h2[contains(@class,"title")] | '
                    './/h3 | '
                    './/div[contains(@class,"position-title")] | '
                    './/*[contains(@class,"job-title")]'
                ).text.strip()
                
                url = card.find_element(By.XPATH,
                    './/a[contains(@href,"job")]/@href | '
                    './/a[contains(@class,"apply")]/@href | '
                    './/a[contains(@href,"careers")]/@href'
                ).get_attribute("href")
                
                # Description extraction with smart truncation
                try:
                    description = card.find_element(By.XPATH,
                        './/div[contains(@class,"description")] | '
                        './/div[contains(@class,"summary")] | '
                        './/p[contains(@class,"brief")]'
                    ).text.strip()[:300] + "..."  # Limit to 300 chars for efficiency
                except:
                    description = title  # Fallback to title if no description

                job = {
                    "source": "company",
                    "title": title,
                    "company": company["name"],
                    "location": "Unknown",
                    "url": url,
                    "posted_date": datetime.now(),
                    "description": description
                }

                # Relevance check with detailed logging
                is_relevant = is_relevant_job(job, resume_keywords)
                logger.debug(f"""
                📝 Job {idx} Check:
                Title: {title}
                Description: {description[:50]}...
                Relevant: {is_relevant}
                """)

                if is_relevant:
                    jobs.append(job)
                    logger.info(f"✅ Added relevant job: {title}")
                else:
                    logger.info(f"⏭️  Skipped non-relevant job: {title}")

            except Exception as e:
                logger.warning(f"⚠️ Partial failure processing job {idx}: {str(e)}")
                continue

        logger.info(f"📊 {company['name']} Results: {len(jobs)} relevant jobs found")

    except Exception as e:
        logger.error(f"❌ Critical error processing {company['name']}: {str(e)}")
    
    finally:
        driver.quit()
    
    return jobs

def scrape_all_companies(resume_keywords):
    """Main company scraping entry point with progress tracking"""
    companies = pd.read_csv(COMPANY_LIST_PATH)
    if not {'name', 'career_url'}.issubset(companies.columns):
        raise ValueError("CSV must contain 'name' and 'career_url' headers")

    all_jobs = []
    total_companies = len(companies)
    
    for idx, company in enumerate(companies.to_dict("records"), 1):
        try:
            logger.info(f"🏢 Processing company {idx}/{total_companies}: {company['name']}")
            jobs = scrape_company_page_dynamic(company, resume_keywords)
            all_jobs.extend(jobs)
            logger.info(f"📦 Current total: {len(all_jobs)} jobs")
        except Exception as e:
            logger.error(f"🚨 Failed processing {company['name']}: {str(e)}")
            continue
    
    logger.info(f"🏁 Completed company scraping. Total jobs: {len(all_jobs)}")
    print(f"🏢 Printing all jobs in scrape_all_companies: {all_jobs}")
    return all_jobs
