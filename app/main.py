from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import hashlib
import requests
from datetime import datetime
from .scrapers.linkedin_scraper import LinkedInScraper
from .scrapers.twitter_scraper import TwitterScraper
from .scrapers.instagram_scraper import InstagramScraper
from .scrapers.tiktok_scraper import TikTokScraper
from .database.supabase_client import get_supabase_client

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Social Media Scraper API",
    description="API for scraping trending posts from various social media platforms",
    version="1.0.0"
)

class ScrapeRequest(BaseModel):
    platform: str
    query: Optional[str] = None
    limit: Optional[int] = 20

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[List[dict]] = None

def generate_user_id(platform: str, username: str, timestamp: datetime) -> str:
    """Generate a unique user ID based on platform and username."""
    timestamp_str = timestamp.isoformat()
    combined = f"{platform}:{username}:{timestamp_str}".encode('utf-8')
    return hashlib.sha256(combined).hexdigest()[:32]  # Using first 32 chars of SHA-256 hash

def generate_post_id(url: str, username: str, timestamp: datetime) -> str:
    """Generate a unique post ID based on URL, username, and timestamp."""
    timestamp_str = timestamp.isoformat()
    combined = f"{url}:{username}:{timestamp_str}".encode('utf-8')
    return hashlib.sha256(combined).hexdigest()[:32]  # Using first 32 chars of SHA-256 hash

def calculate_engagement_score(engagement: dict) -> float:
    """Calculate engagement score based on likes, comments, and shares."""
    likes = engagement.get("numLikes", 0)
    comments = engagement.get("numComments", 0)
    shares = engagement.get("numShares", 0)

    engagement_score = likes*1 + comments*3 + shares*3
    return engagement_score

def fetch_user_details(profile_url: str) -> dict:
    """Fetch user details from profile URL using RapidAPI."""
    url = "https://linkedin-bulk-data-scraper.p.rapidapi.com/profiles"

    payload= {
        "links": [profile_url],
    }
    headers={
        "x-rapidapi-key": "42685e9056msha4b57589359c255p1c5e02jsndb4f99ff28b0",
        "x-rapidapi-host": "linkedin-bulk-data-scraper.p.rapidapi.com",
        "Content-Type": "application/json",
        "x-rapidapi-user": "usama"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_social_media(request: ScrapeRequest):
    try:
        platform = request.platform.lower()
        supabase = get_supabase_client()
        
        # Get current timestamp
        current_timestamp = datetime.utcnow()
        
        # Initialize appropriate scraper based on platform
        scraper = None
        if platform == "linkedin":
            scraper = LinkedInScraper()
        elif platform == "twitter":
            scraper = TwitterScraper()
        elif platform == "instagram":
            scraper = InstagramScraper()
        elif platform == "tiktok":
            scraper = TikTokScraper()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

        # Scrape posts
        posts = await scraper.scrape_posts(
            query=request.query,
            limit=request.limit
        )
        # Store posts and user data in Supabase
        for post in posts:
            #1. Pushing Post data 
            # Store post data with user reference
            metadata = {
                "share_url": post["share_url"],
                "user": {
                    "user_name": post["actor_name"],
                    "user_description": post["actor_description"],
                    "user_profile_url": post["actor_navigationContext"]
                },
                "commentary": post["commentary"],
                "postedAt": post["postedAt"],
                "media": post.get("linkedInVideoComponent", {}).get("thumbnail"),
                "media_duration": post.get("linkedInVideoComponent", {}).get("duration"),
                "engagement": {
                    "numLikes": post.get("numLikes", 0),
                    "numComments": post.get("numComments", 0),
                    "numShares": post.get("numShares", 0),
                    "reactionTypeCounts": post.get("reactionTypeCounts", [])
                }
            }

            engagement_score = calculate_engagement_score(metadata['engagement'])
            
            post_id = generate_post_id(post['share_url'], post['actor_name'], current_timestamp)
            user_id = generate_user_id(platform, post['actor_name'], current_timestamp)


            post_data = {
                "post_id": post_id,
                "platform": platform,
                "user_id": user_id, 
                "metadata": metadata,
                "engagement_score": engagement_score,
                "scraped_at": current_timestamp.isoformat()  # Add scraping timestamp
            }

            #print(post_data)
            supabase.table("social_media_posts").insert(post_data).execute()

            # fetching user details from Profile url with other RapidAPI
            user_details = fetch_user_details(post['actor_navigationContext'])

            # Store user data first
            user_data = {
                "user_id": user_id,
                "platform": platform,
                "user_name": post['actor_name'],
                "profile_url": post['actor_navigationContext'],
                "bio": post['actor_description'],
                "last_scraped_at": current_timestamp.isoformat()  # Add last scraping timestamp
            }
            
            # Upsert user data (insert if not exists, update if exists)
            supabase.table("social_media_users").insert(user_data).execute()

        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped {len(posts)} posts from {platform}",
            data=posts
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 