from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseScraper(ABC):
    @abstractmethod
    async def scrape_posts(self, query: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Scrape posts from the platform
        
        Args:
            query: Optional search query
            limit: Maximum number of posts to scrape
            
        Returns:
            List of dictionaries containing post data
        """
        pass 