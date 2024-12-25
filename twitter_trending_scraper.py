import os
import pymongo
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Setup
client = pymongo.MongoClient(MONGO_URI)
db = client["twitter_scraper"]
collection = db["trending_topics"]

# Selenium WebDriver Setup
def init_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    
    try:
        service = Service("/usr/bin/chromedriver")  # Update path if needed
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except WebDriverException as e:
        print("Error initializing WebDriver:", e)
        exit(1)

# Open Login Page
def open_login_page(driver):
    try:
        driver.get("https://x.com/i/flow/login?lang=en")
        print("Login page opened. Please log in manually.")
    except WebDriverException as e:
        print("Failed to open login page:", e)
        driver.quit()
        exit(1)

# Wait for Login Completion
def wait_for_login(driver):
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Home"]'))
        )
        print("Login successful!")
    except TimeoutException:
        print("Login timeout. Please try again.")
        driver.quit()
        exit(1)

# Fetch Trending Topics
def fetch_trending(driver):
    try:
        driver.get("https://x.com/explore/tabs/for_you")
        wait = WebDriverWait(driver, 30)
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@aria-label="Timeline: Explore"]')
            )
        )
        
        trend_elements = driver.find_elements(
            By.XPATH, '//div[@aria-label="Timeline: Explore"]//div[@dir="ltr"]'
        )

        trending_topics = [
            {"name": item.strip()} 
            for trend in trend_elements 
            for item in trend.text.split("\n") 
            if "#" in item and item.strip() != ""
        ]

        return trending_topics[:5]  # Limit to top 5 trends

    except Exception as e:
        print("Error fetching trending topics:", e)
        return []

# Save Data to MongoDB
def save_trending_to_mongo(driver, trending_topics):
    if not trending_topics:
        print("No trending topics to save.")
        return

    unique_id = str(uuid.uuid4())
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "_id": unique_id,
        **{f"trend{i+1}": topic["name"] for i, topic in enumerate(trending_topics)},
        "end_time": end_time,
        "ip_address": driver.execute_script("return window.location.host;"),
    }

    collection.insert_one(record)
    print("Data inserted into MongoDB:", record)
    return record


# Main Script Execution
if __name__ == "__main__":
    driver = init_driver()
    try:
        open_login_page(driver)
        wait_for_login(driver)
        trending_topics = fetch_trending(driver)
        record = save_trending_to_mongo(driver, trending_topics)
        print(json.dumps(record))  # Output JSON for Node.js
    finally:
        driver.quit()
