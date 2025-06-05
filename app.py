from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import logging
import threading
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global queue for Chrome instances
chrome_queue = Queue()
MAX_CHROME_INSTANCES = 1

def init_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    return webdriver.Chrome(options=chrome_options)

def get_chrome_driver():
    try:
        return chrome_queue.get_nowait()
    except:
        return init_chrome_driver()

def return_chrome_driver(driver):
    try:
        chrome_queue.put_nowait(driver)
    except:
        driver.quit()

def extract_download_link(url):
    driver = None
    try:
        driver = get_chrome_driver()
        logger.info(f"Accessing URL: {url}")
        driver.get(url)
        
        # Wait for the page to load completely
        time.sleep(10)
        
        # Wait for the video element to be visible
        logger.info("Waiting for video element...")
        wait = WebDriverWait(driver, 30)
        video_element = wait.until(
            EC.presence_of_element_located((By.ID, "videoPlayer_html5_api"))
        )
        
        # Extract the link from the src attribute
        video_src = video_element.get_attribute("src")
        logger.info(f"Found video source: {video_src}")
        
        return video_src
        
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        return None
        
    finally:
        if driver:
            return_chrome_driver(driver)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        logger.info(f"Received request to extract video from: {url}")
        video_link = extract_download_link(url)
        
        if video_link:
            return jsonify({'video_link': video_link})
        else:
            return jsonify({'error': 'Could not extract video link'}), 400
            
    except Exception as e:
        logger.error(f"Error in extract endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/api/extract', methods=['GET'])
def api_extract():
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        logger.info(f"Received API request to extract video from: {url}")
        video_link = extract_download_link(url)
        
        if video_link:
            return jsonify({
                'status': 'success',
                'video_link': video_link
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Could not extract video link'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in API extract endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request'
        }), 500

# Add favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    # Initialize Chrome driver pool
    for _ in range(MAX_CHROME_INSTANCES):
        chrome_queue.put(init_chrome_driver())
    
    app.run(debug=True, host='0.0.0.0', port=5000) 