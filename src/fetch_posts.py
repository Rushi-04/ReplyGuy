"""
Post Fetcher - Extracts tweets/posts from X (Twitter) feed
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class PostFetcher:
    def __init__(self, driver: WebDriver, wait_timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
    
    def scroll_feed(self, scrolls: int = 3, delay: float = 2.0):
        """Scroll the feed to load more posts"""
        for i in range(scrolls):
            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(delay)
            logger.debug(f"Scrolled {i+1}/{scrolls}")
    
    def extract_tweet_id(self, article_element) -> Optional[str]:
        """Extract tweet ID from article element"""
        try:
            # Try to get tweet ID from data-testid or href
            links = article_element.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "/status/" in href:
                    # Extract tweet ID from URL like https://x.com/user/status/1234567890
                    match = re.search(r'/status/(\d+)', href)
                    if match:
                        return match.group(1)
        except Exception as e:
            logger.debug(f"Failed to extract tweet ID: {e}")
        return None
    
    def extract_username(self, article_element) -> Optional[str]:
        """Extract username from tweet"""
        try:
            # Look for username in various possible locations
            # X/Twitter structure: @username is usually in a link or span
            username_elements = article_element.find_elements(
                By.CSS_SELECTOR, 
                "a[href*='/'] span, [data-testid='User-Name'] a"
            )
            for elem in username_elements:
                text = elem.text.strip()
                if text.startswith('@'):
                    return text[1:] if text.startswith('@') else text
                # Sometimes username is in href
                href = elem.get_attribute("href")
                if href and "/" in href:
                    parts = href.split("/")
                    if len(parts) > 1 and not parts[-1].startswith("status"):
                        return parts[-1]
        except Exception as e:
            logger.debug(f"Failed to extract username: {e}")
        return None
    
    def extract_tweet_text(self, article_element) -> Optional[str]:
        """Extract tweet text content"""
        try:
            # Multiple selectors to try for tweet text
            selectors = [
                "[data-testid='tweetText']",
                "[data-testid='tweetText'] span",
                "div[lang] span",
                "div[data-testid='tweetText']"
            ]
            
            for selector in selectors:
                try:
                    text_elem = article_element.find_element(By.CSS_SELECTOR, selector)
                    text = text_elem.text.strip()
                    if text:
                        return text
                except NoSuchElementException:
                    continue
            
            # Fallback: get all text from article
            text = article_element.text
            # Clean up - remove usernames, timestamps, etc.
            lines = text.split('\n')
            # Filter out common non-content lines
            content_lines = [line for line in lines if line and 
                           not line.startswith('@') and 
                           '·' not in line and
                           len(line) > 10]  # Filter very short lines
            return ' '.join(content_lines[:3])  # Take first few meaningful lines
        except Exception as e:
            logger.debug(f"Failed to extract tweet text: {e}")
        return None
    
    def check_already_replied(self, article_element) -> bool:
        """
        Check if we've already replied to this tweet (by looking for reply button state)
        NOTE: This is unreliable - database check is the primary method
        Returns False to be conservative and let database handle duplicate detection
        """
        # UI-based detection is unreliable due to X/Twitter's dynamic structure
        # We rely on database tracking instead for accurate duplicate detection
        # Returning False here means "not sure, let database decide"
        return False
    
    def get_visible_tweet_elements(self) -> List:
        """Get all currently visible tweet articles"""
        return self.driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")

    def extract_post_data(self, article_element) -> Optional[Dict]:
        """
        Extract data from a single article element
        Returns dict with keys: tweet_id, username, text, element
        """
        try:
            # Extract tweet ID
            tweet_id = self.extract_tweet_id(article_element)
            if not tweet_id:
                return None
            
            # Extract username
            username = self.extract_username(article_element)
            
            # Extract text
            text = self.extract_tweet_text(article_element)
            if not text or len(text) < 10:  # Skip very short tweets
                return None
            
            # Check if already replied (UI check)
            already_replied = self.check_already_replied(article_element)
            
            return {
                'tweet_id': tweet_id,
                'username': username or 'unknown',
                'text': text,
                'element': article_element,
                'already_replied': already_replied
            }
        except Exception as e:
            logger.debug(f"Error extraction post data: {e}")
            return None

    def fetch_posts(self, max_posts: int = 10, scroll_first: bool = True) -> List[Dict]:
        """
        Legacy method kept for compatibility, but updated to use new helpers
        """
        posts = []
        
        try:
            # Wait for feed to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='tweet']"))
            )
            
            if scroll_first:
                self.scroll_feed(scrolls=2, delay=1.5)
            
            seen_ids = set()
            
            # Get visible elements
            articles = self.get_visible_tweet_elements()
            
            for article in articles:
                if len(posts) >= max_posts:
                    break
                    
                post_data = self.extract_post_data(article)
                if post_data and post_data['tweet_id'] not in seen_ids:
                    seen_ids.add(post_data['tweet_id'])
                    posts.append(post_data)
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return []

