import time
import concurrent.futures
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import JOB_TITLES, LOCATIONS, MAX_LINKEDIN_PAGES, CHROME_DRIVER_PATH
from utils.logger import logger

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

def extract_job_details(card):
    try:
        title = card.find_element(By.CSS_SELECTOR, "h3").text.strip()
        company = card.find_element(By.CSS_SELECTOR, "h4").text.strip()
        location = card.find_element(By.CSS_SELECTOR, ".job-search-card__location").text.strip()
        url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        date_elem = card.find_element(By.CSS_SELECTOR, "time")
        posted_date = datetime.fromisoformat(date_elem.get_attribute("datetime"))
        return {
            "source": "linkedin",
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "posted_date": posted_date,
            "description": f"{title} at {company}"
        }
    except Exception as e:
        logger.warning(f"LinkedIn card extraction failed: {e}")
        return None

def scrape_linkedin_title_location(title, location):
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)
    jobs = []
    try:
        for page in range(MAX_LINKEDIN_PAGES):
            start = page * 25
            url = f"https://www.linkedin.com/jobs/search/?keywords={title}&location={location}&start={start}"
            logger.info(f"🔄 Scraping LinkedIn: {title} - {location} - Page {page+1}")
            print(f"🔄 Scraping LinkedIn: {title} | {location} | Page {page+1}")
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list")))
            cards = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")
            for card in cards:
                job = extract_job_details(card)
                if job:
                    jobs.append(job)
            logger.info(f"✅ Found {len(cards)} jobs on page {page+1} for {title} - {location}")
            print(f"✅ Found {len(cards)} jobs on page {page+1} for {title} | {location}")
    except TimeoutException:
        logger.warning(f"⚠️ Timeout on LinkedIn page for title={title}, location={location}")
    except Exception as e:
        logger.error(f"❌ Error scraping LinkedIn ({title}, {location}): {e}")
    finally:
        driver.quit()
    return jobs

def scrape_all_linkedin_jobs():
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for title in JOB_TITLES:
            for location in LOCATIONS:
                futures.append(executor.submit(scrape_linkedin_title_location, title, location))
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.extend(result)
            except Exception as e:
                logger.error(f"LinkedIn future failed: {e}")
    return results
