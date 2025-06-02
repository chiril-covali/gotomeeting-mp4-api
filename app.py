from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "GoToMeeting MP4 Extractor API - online!"

@app.route('/extract_mp4', methods=['POST'])
def extract_mp4():
    data = request.get_json()
    gtm_url = data.get("url")
    if not gtm_url:
        return jsonify({'error': 'No url provided'}), 400

    # TODO: Înlocuiește cu logica reală de extragere a linkului .mp4
    fake_mp4 = "https://example.com/dummy.mp4"
    return jsonify({'mp4_url': fake_mp4})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)