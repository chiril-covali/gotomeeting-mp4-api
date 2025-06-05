# GoToMeeting MP4 API

A Flask-based API for extracting direct MP4 video links from GoToMeeting recordings.

## Features

- Extracts direct MP4 video links from GoToMeeting URLs
- RESTful API endpoint for easy integration
- CORS enabled for cross-origin requests
- Docker support for easy deployment

## API Usage

### Extract Video Link

```http
GET /api/extract?url=YOUR_GOTOMEETING_URL
```

#### Response

Success:
```json
{
    "status": "success",
    "video_link": "https://example.com/video.mp4"
}
```

Error:
```json
{
    "status": "error",
    "message": "Error message here"
}
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t gotomeeting-mp4-api .
```

2. Run the container:
```bash
docker run -p 10000:10000 gotomeeting-mp4-api
```

## Requirements

- Python 3.9+
- Chrome/Chromium browser
- ChromeDriver

## License

MIT 