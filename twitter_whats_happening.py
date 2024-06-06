from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import pymongo

load_dotenv()
MONGODB_URL = os.getenv('MongoDB_URL')

    

# Function to fetch IP address
def get_ip_address(driver):
    try:
        driver.get('https://api64.ipify.org/')
        ip_address = driver.find_element(By.XPATH, '//body').text.strip()
        return ip_address
    except Exception as e:
        print(f"Failed to fetch IP address. Exception: {e}")
        return None
    
def store_trending_topics(client, trending_topics, ip_address):
    db = client.get_database('twitter_trending')
    collection = db['trending_topics']

    unique_id = str(uuid.uuid4())
    timestamp = datetime.now()
    result = {
        "unique_id": unique_id,
        "trend1": trending_topics[0],
        "trend2": trending_topics[1],
        "trend3": trending_topics[2],
        "trend4": trending_topics[3],
        "trend5": trending_topics[4],
        "date_time": timestamp,
        "ip_address": ip_address
    }

    collection.insert_one(result)
    return result

def get_top_trends(browser,username, password):

    browser.get("https://x.com")

    # Wait for the login button to be clickable
    wait = WebDriverWait(browser, 10)
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/login')]")))

    # Scroll the login button into view and click it
    browser.execute_script("arguments[0].scrollIntoView(true);", login_button)
    login_button.click()
    
    # Wait for the username field to be present
    fill_username = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    fill_username.send_keys(username)

    # Locate and click the "Next" button
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Next')]]")))
    next_button.click()

    # Wait for the password field to be present
    fill_password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    fill_password.send_keys(password)

    # Locate and click the "Log in" button
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Log in')]]")))
    login_button.click()

    # Wait for the login to complete
    time.sleep(25)
    explore_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/explore/tabs/for-you')]")))
    browser.execute_script("arguments[0].scrollIntoView(true);", explore_button)
    explore_button.click()

    # Wait for the trends to load
    time.sleep(1)

    # Scroll down the page to load more trends
    browser.execute_script("window.scrollBy(0, 500);")
    time.sleep(2)

    trending_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='trend']")))
    # Extract text for top 5 trending topics
    top_trends = []
    for i, trend in enumerate(trending_elements):
        if i >= 5:
            break
        trend_category = trend.find_element(By.XPATH, ".//div[contains(@style, 'color: rgb(113, 118, 123)')]//span").text
        trend_name = trend.find_element(By.XPATH, ".//div[contains(@style, 'color: rgb(231, 233, 234)')]//span").text
        top_trends.append(f"{trend_category} - {trend_name}")

    browser.quit()
    return top_trends

def scrape_twitter(username, password):
    # Chrome configuration    
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    # #Proxy configuration
    # proxy_host = ["us-ca.proxymesh.com:31280","us-wa.proxymesh.com:31280","fr.proxymesh.com:31280","jp.proxymesh.com:31280","au.proxymesh.com:31280","de.proxymesh.com:31280","nl.proxymesh.com:31280","sg.proxymesh.com:31280","us-il.proxymesh.com:31280","us-tx.proxymesh.com:31280","us-dc.proxymesh.com:31280","us-ny.proxymesh.com:31280","uk.proxymesh.com:31280","ch.proxymesh.com:31280","us-fl.proxymesh.com:31280","in.proxymesh.com:31280","open.proxymesh.com:31280","world.proxymesh.com:31280","usisp.proxymesh.com:31280"]
    # proxy = random.choice(proxy_host)
    # chrome_options.add_argument('--proxy-server=%s' % proxy)

    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    ip_address = get_ip_address(browser)
    if not ip_address:
        ip_address = 'unknown'

    trending_topics = get_top_trends(browser, username, password)
    if trending_topics:
        client = pymongo.MongoClient(MONGODB_URL)
        result = store_trending_topics(client, trending_topics, ip_address)
        client.close()
        return result 
    else:
        return None
