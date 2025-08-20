import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    return driver

def scroll_page(driver, pause=2, max_scroll=15):
    """Scroll until page stops loading new jobs or limit reached."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scroll):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_jobs(keyword, max_pages=2):
    driver = get_driver()
    all_jobs = []

    for page in range(max_pages):
        start = page * 10
        url = f"https://www.indeed.com/jobs?q={keyword}&start={start}"
        print(f"\n🔎 Scraping {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
            )
            time.sleep(2)

            # scroll to load more jobs
            scroll_page(driver)

            jobs = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
            print(f"✅ Found {len(jobs)} jobs on this page after scrolling")

            for job in jobs:
                try:
                    title = job.find_element(By.CSS_SELECTOR, "h2.jobTitle span").text.strip()
                    link = job.find_element(By.CSS_SELECTOR, "h2.jobTitle a").get_attribute("href")
                    try:
                        company = job.find_element(By.CSS_SELECTOR, "span.companyName").text.strip()
                    except:
                        company = ""
                    try:
                        location = job.find_element(By.CSS_SELECTOR, "div.companyLocation").text.strip()
                    except:
                        location = ""

                    all_jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "link": link
                    })
                except:
                    continue

        except Exception as e:
            print("⚠️ Job listings did not load (blocked?)")

    driver.quit()
    return all_jobs

if __name__ == "__main__":
    jobs = scrape_jobs("Data Engineer", max_pages=2)
    print(f"\n✅ Scraped {len(jobs)} jobs total")
    if jobs:
        df = pd.DataFrame(jobs)
        df.to_csv("indeed_jobs.csv", index=False, encoding="utf-8-sig")
        print("💾 Saved results to indeed_jobs.csv")
