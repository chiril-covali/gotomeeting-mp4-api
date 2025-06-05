from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import os
import logging
import threading
from queue import Queue
import gevent
from gevent import monkey
monkey.patch_all()

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
    # Performance optimizations
    chrome_options.add_argument('--disable-javascript')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-breakpad')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
    chrome_options.add_argument('--force-color-profile=srgb')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--mute-audio')
    
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

def extract_download_link(url, max_retries=2):
    driver = None
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            driver = get_chrome_driver()
            logger.info(f"Accessing URL: {url} (Attempt {retry_count + 1}/{max_retries + 1})")
            
            # First try to access the page
            driver.get(url)
            gevent.sleep(5)  # Reduced from 10 to 5 seconds
            
            # Try to find the video element
            logger.info("Waiting for video element...")
            wait = WebDriverWait(driver, 30)  # Reduced from 60 to 30 seconds
            
            try:
                # Try multiple selectors in sequence
                selectors = [
                    (By.ID, "videoPlayer_html5_api"),
                    (By.TAG_NAME, "video"),
                    (By.CSS_SELECTOR, "video[src]"),
                    (By.CSS_SELECTOR, "video source[src]")
                ]
                
                for by, selector in selectors:
                    try:
                        element = wait.until(EC.presence_of_element_located((by, selector)))
                        video_src = element.get_attribute("src")
                        if video_src:
                            logger.info(f"Found video source using {selector}: {video_src}")
                            return video_src
                    except:
                        continue
                
                # If no video found, try to get it from page source
                page_source = driver.page_source
                if "videoPlayer_html5_api" in page_source:
                    # Try to extract src from page source
                    import re
                    src_match = re.search(r'src="([^"]+)"', page_source)
                    if src_match:
                        video_src = src_match.group(1)
                        logger.info(f"Found video source from page source: {video_src}")
                        return video_src
                
                logger.error("No video source found")
                if retry_count < max_retries:
                    logger.info(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                    retry_count += 1
                    continue
                return None
                
            except TimeoutException:
                logger.error("Timeout waiting for video element")
                if retry_count < max_retries:
                    logger.info(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                    retry_count += 1
                    continue
                return None
                
        except WebDriverException as e:
            logger.error(f"WebDriver error: {str(e)}")
            if retry_count < max_retries:
                logger.info(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                retry_count += 1
                continue
            return None
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}")
            if retry_count < max_retries:
                logger.info(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                retry_count += 1
                continue
            return None
        finally:
            if driver:
                return_chrome_driver(driver)
    
    return None

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
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 