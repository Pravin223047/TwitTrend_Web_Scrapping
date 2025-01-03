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
import socket
import platform

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = pymongo.MongoClient(MONGO_URI)
db = client["twitter_scraper"]
collection = db["trending_topics"]

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

if platform.system() == "Windows":
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "C:/Users/Pravin Kshirsagar/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
elif platform.system() == "Linux":
    chromedriver_path = "/usr/bin/chromedriver"
else:
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")

service = Service(chromedriver_path)

try:
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

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        record = {
            "_id": unique_id,
            "trend1": trending_topics[0]["name"] if len(trending_topics) > 0 else None,
            "trend2": trending_topics[1]["name"] if len(trending_topics) > 1 else None,
            "trend3": trending_topics[2]["name"] if len(trending_topics) > 2 else None,
            "trend4": trending_topics[3]["name"] if len(trending_topics) > 3 else None,
            "trend5": trending_topics[4]["name"] if len(trending_topics) > 4 else None,
            "end_time": end_time,
            "ip_address": ip_address,
        }

        try:
            collection.insert_one(record)
            print("Data inserted into MongoDB:", record)
        except Exception as e:
            print("Error saving to MongoDB:", e)

        return record

    # Script Execution
    open_login_page()
    wait_for_login()
    trending_topics = fetch_trending()
    record = save_trending_to_mongo(trending_topics)

    print(json.dumps(record))

except WebDriverException as e:
    print("WebDriver Error:", e)

finally:
    if 'driver' in locals():
        driver.quit()
