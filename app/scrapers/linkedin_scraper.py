import os
import requests
from typing import List, Dict, Optional
from .base_scraper import BaseScraper

class LinkedInScraper(BaseScraper):
    def __init__(self):
        self.url = "https://linkedin-bulk-data-scraper.p.rapidapi.com/search_posts"
        self.headers = {
            "x-rapidapi-key": "42685e9056msha4b57589359c255p1c5e02jsndb4f99ff28b0",
            "x-rapidapi-host": "linkedin-bulk-data-scraper.p.rapidapi.com",
            "Content-Type": "application/json"
        }

    async def scrape_posts(self, query: Optional[str] = None, limit: int = 20) -> List[Dict]:
        payload = {
            "page": 1,
            "query": query or "Top 1",
            "filters": [
                {
                    "key": "datePosted",
                    "values": "past-week"
                }
            ]
        }

        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            
            # Extract and format post details
            posts = []
            for post in response_json.get('posts', [])[:limit]:
                extracted_post = {
                    "share_url": post.get('share_url'),
                    "actor_name": post['actor'].get('actor_name'),
                    "actor_description": post['actor'].get('actor_description'),
                    "actor_image": post['actor'].get('actor_image'),
                    "actor_navigationContext": post['actor'].get('actor_navigationContext'),
                    "commentary": post.get('commentary'),
                    "numLikes": post['social_details'].get('numLikes'),
                    "numComments": post['social_details'].get('numComments'),
                    "numShares": post['social_details'].get('numShares'),
                    "postedAt": post.get('postedAt'),
                    "article_title": post['articleComponent'].get('title') if post.get('articleComponent') else None,
                    "article_description": post['articleComponent'].get('description') if post.get('articleComponent') else None,
                    "article_url": post['articleComponent'].get('navigationContext') if post.get('articleComponent') else None
                }
                posts.append(extracted_post)
            
            return posts

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making LinkedIn API request: {str(e)}")
        except ValueError as e:
            raise Exception(f"Error parsing LinkedIn API response: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error in LinkedIn scraper: {str(e)}") 