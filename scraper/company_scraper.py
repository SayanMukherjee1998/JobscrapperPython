import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from config import CHROME_DRIVER_PATH, COMPANY_LIST_PATH, MAX_COMPANY_JOBS
from utils.logger import logger

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])



def scrape_company_page_dynamic(company):
    jobs = []
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)
    try:
        print(f"🔄 Scraping company: {company['name']}")
        logger.info(f"🔄 Scraping company: {company['name']}")
        driver.get(company["career_url"])
        cards = driver.find_elements(By.XPATH, '//a[contains(@href,"job") or contains(@href,"careers")]')
        for card in cards[:MAX_COMPANY_JOBS]:
            try:
                job = {
                    "source": "company",
                    "title": card.text.strip() or "Unknown Title",
                    "company": company["name"],
                    "location": "Unknown",
                    "url": card.get_attribute("href"),
                    "posted_date": datetime.now(),
                    "description": card.text.strip()
                }
                jobs.append(job)
            except Exception as e:
                logger.warning(f"⚠️ Card parse error on {company['name']}: {e}")
        logger.info(f"✅ Found {len(jobs)} jobs at {company['name']}")
        print(f"✅ Found {len(jobs)} jobs at {company['name']}")
    except Exception as e:
        logger.error(f"❌ Company scrape failed for {company.get('name', 'unknown')}: {e}")
    finally:
        driver.quit()
    return jobs


def scrape_all_companies():
    companies = pd.read_csv(COMPANY_LIST_PATH)
    if not {'name', 'career_url'}.issubset(companies.columns):
        raise ValueError("CSV must contain 'name' and 'career_url' headers.")
    companies = companies.to_dict("records")
    all_jobs = []
    for comp in companies:
        jobs = scrape_company_page_dynamic(comp)
        all_jobs.extend(jobs)
    return all_jobs
