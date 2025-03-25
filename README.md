# Social Media Scraper API

A FastAPI application that scrapes trending posts from various social media platforms (LinkedIn, Twitter, Instagram, TikTok) and stores them in Supabase.

## Features

- Scrape trending posts from multiple social media platforms
- Store posts and user data in Supabase
- RESTful API endpoints
- Modular and extensible architecture

## Prerequisites

- Python 3.8+
- Supabase account
- RapidAPI account with access to social media scraping APIs

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd social-brand-AI
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the environment variables template:
```bash
cp .env.example .env
```

5. Update the `.env` file with your credentials:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase project API key
- `RAPIDAPI_KEY`: Your RapidAPI key

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /scrape
Scrape posts from a specified social media platform.

Request body:
```json
{
    "platform": "linkedin",  // Options: linkedin, twitter, instagram, tiktok
    "query": "optional search query",
    "limit": 10  // Optional, defaults to 10
}
```

### GET /health
Health check endpoint.

## Database Schema

The application creates two tables per platform in Supabase:

1. `{platform}-posts`:
   - url
   - post_date
   - user_name
   - post_title
   - post_content
   - likes
   - comments
   - shares
   - platform

2. `{platform}-users`:
   - user_name
   - user_description
   - platform

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
