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
import json

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = pymongo.MongoClient(MONGO_URI)
db = client["twitter_scraper"]
collection = db["trending_topics"]

# ProxyMesh Configuration
PROXY = os.getenv("PROXY_HOST")  # e.g., "us-dc.proxymesh.com:10001"
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")

options = Options()
options.add_argument("--start-maximized")

# Configure ProxyMesh Proxy with Authentication
options.add_argument(f"--proxy-server=http://{PROXY}")
options.add_argument(f"--proxy-auth={PROXY_USERNAME}:{PROXY_PASSWORD}")

# Use the path to your chromedriver.exe for Windows
service = Service("C:/Users/Pravin Kshirsagar/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")  # Replace with the actual path to chromedriver.exe

driver = webdriver.Chrome(service=service, options=options)

def open_login_page():
    driver.get("https://x.com/i/flow/login?lang=en")
    print("Login page opened. Please log in manually.")

def wait_for_login():
    try:
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '//*[text()="Home"]'))
        )
        print("Login successful!")
    except TimeoutException:
        print("Login timeout. Please try again.")
        driver.quit()
        exit()

def fetch_trending():
    driver.get("https://x.com/explore/tabs/for_you")

    try:
        WebDriverWait(driver, 300).until(
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
    ip_address = PROXY.split("@")[-1].split(":")[0] if PROXY else "N/A"
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
        "ip_address": ip_address if ip_address != "N/A" else driver.execute_script("return window.location.host;"),
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
