import requests
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

url = "https://linkedin-bulk-data-scraper.p.rapidapi.com/search_posts"

payload = {
	"page": 1,
	"query": "Top 10",
	"filters": [
		{
			"key": "datePosted",
			"values": "past-week"
		}
	]
}
headers = {
	"x-rapidapi-key": "42685e9056msha4b57589359c255p1c5e02jsndb4f99ff28b0",
	"x-rapidapi-host": "linkedin-bulk-data-scraper.p.rapidapi.com",
	"Content-Type": "application/json"
}
try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
    response_json = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
    raise
except ValueError as e:  # Catches JSON decode errors
    print(f"Error decoding JSON response: {e}")
    raise


print(response_json)
# Function to extract post details
def extract_post_details(response_data):
    extracted_posts = []
    for post in response_data['posts']:
        extracted_post = {
            "share_url": post.get('share_url'),
            "actor_name": post['actor'].get('actor_name'),
            "actor_description": post['actor'].get('actor_description'),
            "commentary": post.get('commentary'),
            "numLikes": post['social_details'].get('numLikes'),
            "numComments": post['social_details'].get('numComments'),
            "numShares": post['social_details'].get('numShares'),
            "postedAt": post.get('postedAt'),
            "article_title": post['articleComponent'].get('title') if post.get('articleComponent') else None,
            "article_description": post['articleComponent'].get('description') if post.get('articleComponent') else None,
            "article_url": post['articleComponent'].get('navigationContext') if post.get('articleComponent') else None
        }
        extracted_posts.append(extracted_post)
    return extracted_posts

extracted_posts = extract_post_details(response_json)
 
for post in extracted_posts:
        post_data = [
            {
                "url": post['share_url'],
                "post_date": post['postedAt'],
                "user_name": post['actor_name'],
                "post_title": post['article_title'],
                "post_content": post['commentary'],
                "likes": post['numLikes'],
                "comments": post['numComments'],
                "shares": post['numShares'],
            }
        ]
        supabase.table("social-media-posts").insert(post_data).execute()
        print("Post inserted successfully")
        user_data=[
            {
                "user_name": post['actor_name'],
                "user_description": post['actor_description']
            }
        ]
        supabase.table("social-media-users").insert(user_data).execute()


print("Post inserted successfully:", response)
print("reponse:", response_json)