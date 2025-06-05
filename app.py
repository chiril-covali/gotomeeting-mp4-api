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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_download_link(url):
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # Initialize Chrome driver
        logger.info("Initializing Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Access the URL
            logger.info(f"Accessing URL: {url}")
            driver.get(url)
            
            # Wait for the page to load completely
            time.sleep(5)
            
            # Wait for the video element to be visible
            logger.info("Waiting for video element...")
            wait = WebDriverWait(driver, 20)  # Increased timeout
            video_element = wait.until(
                EC.visibility_of_element_located((By.ID, "videoPlayer_html5_api"))
            )
            
            # Extract the link from the src attribute
            video_src = video_element.get_attribute("src")
            logger.info(f"Found video source: {video_src}")
            
            return video_src
            
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}")
            return None
            
        finally:
            # Always close the browser
            driver.quit()
    
    except Exception as e:
        logger.error(f"Error initializing Chrome: {str(e)}")
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
    app.run(debug=True, host='0.0.0.0', port=5000) 