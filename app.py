from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_download_link(url):
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Access the URL
        driver.get(url)
        
        # Wait for the page to load completely
        time.sleep(5)
        
        # Wait for the video element to be visible
        wait = WebDriverWait(driver, 10)
        video_element = wait.until(
            EC.visibility_of_element_located((By.ID, "videoPlayer_html5_api"))
        )
        
        # Extract the link from the src attribute
        video_src = video_element.get_attribute("src")
        
        # Close the browser
        driver.quit()
        
        return video_src
    
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    video_link = extract_download_link(url)
    if video_link:
        return jsonify({'video_link': video_link})
    else:
        return jsonify({'error': 'Could not extract video link'}), 400

# New endpoint for Google Apps Script
@app.route('/api/extract', methods=['GET'])
def api_extract():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 