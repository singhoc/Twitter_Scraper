from flask import Flask, render_template, redirect, url_for, request
import threading
from twitter_whats_happening import scrape_twitter
import os
from dotenv import load_dotenv
import pymongo
import time
from bson.json_util import dumps, loads

load_dotenv()

# Twitter credentials
username = os.getenv('twitter_username')
password = os.getenv('twitter_password')

# MongoDB connection details
MONGODB_URL = os.getenv('MongoDB_URL')
client = pymongo.MongoClient(MONGODB_URL)
db = client.get_database('twitter_trending')
collection = db['trending_topics']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch_trends', methods=['POST'])
def fetch_trends():
    def run_script():
        nonlocal unique_id
        result = scrape_twitter(username, password)
        unique_id = result.get('unique_id') if result else None
        print("Scraped data unique ID:", unique_id)

    unique_id = None
    thread = threading.Thread(target=run_script)
    thread.start()

    # Wait for the thread to finish (or set a reasonable timeout)
    timeout = 60  # seconds
    start_time = time.time()
    while unique_id is None and time.time() - start_time < timeout:
        time.sleep(1)

    if unique_id:
        return redirect(url_for('display_result', unique_id=unique_id))
    else:
        return redirect(url_for('home'))

@app.route('/result/<unique_id>')
def display_result(unique_id):
    result = collection.find_one({"unique_id": unique_id})
    if result:
        result['_id'] = str(result['_id']) 
        return render_template('result.html', result=result)
    else:
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
