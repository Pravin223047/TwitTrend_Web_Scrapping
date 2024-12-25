import os
import pymongo
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from dotenv import load_dotenv
import json  # To output JSON

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = pymongo.MongoClient(MONGO_URI)
db = client["twitter_scraper"]
collection = db["trending_topics"]

options = Options()
options.add_argument("--start-maximized")
service = Service(
    "chromedriver.exe"
)

driver = webdriver.Chrome(service=service, options=options)


def open_login_page():
    driver.get("https://x.com/i/flow/login?lang=en")
    print("Login page opened. Please log in manually.")


def wait_for_login():
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Home"]'))
        )
        print("Login successful!")
    except TimeoutException:
        print("Login timeout. Please try again.")
        driver.quit()
        exit()


def fetch_trending():
    driver.get("https://x.com/explore/tabs/for_you")
    wait = WebDriverWait(driver, 30)

    try:
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@aria-label="Timeline: Explore"]')
            )
        )
        trend_elements = driver.find_elements(
            By.XPATH, '//div[@aria-label="Timeline: Explore"]//div[@dir="ltr"]'
        )

        trending_topics = []

        for trend in trend_elements:
            topic_text = trend.text.split("\n")
            for item in topic_text:
                if "#" in item and item.strip() != "":
                    trending_topics.append({"name": item.strip()})

        return trending_topics

    except Exception as e:
        print("Error fetching trending topics:", e)
        return []


def save_trending_to_mongo(trending_topics):
    if not trending_topics:
        print("No trending topics to save.")
        return

    unique_id = str(uuid.uuid4())
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create record to insert into MongoDB
    record = {
        "_id": unique_id,
        "trend1": trending_topics[0]["name"] if len(trending_topics) > 0 else None,
        "trend2": trending_topics[1]["name"] if len(trending_topics) > 1 else None,
        "trend3": trending_topics[2]["name"] if len(trending_topics) > 2 else None,
        "trend4": trending_topics[3]["name"] if len(trending_topics) > 3 else None,
        "trend5": trending_topics[4]["name"] if len(trending_topics) > 4 else None,
        "end_time": end_time,
        "ip_address": driver.execute_script("return window.location.host;"),
    }

    # Insert data into MongoDB
    collection.insert_one(record)
    print("Data inserted into MongoDB:", record)

    # Return the data as JSON so Node.js can process it
    return record


try:
    open_login_page()
    wait_for_login()
    trending_topics = fetch_trending()
    record = save_trending_to_mongo(trending_topics)

    # Print the JSON data as the final output
    print(json.dumps(record))  # This will be used by Node.js
finally:
    driver.quit() 
