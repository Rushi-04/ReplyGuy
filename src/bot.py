"""
Main Bot - Orchestrates the X reply bot
"""
import time
import random
import logging
from pathlib import Path
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc

from session_manager import (
    save_cookies, load_cookies, get_profile_dir, 
    has_saved_session, save_local_storage
)
from fetch_posts import PostFetcher
from reply_engine import ReplyEngine
from action import ActionPerformer
from database import Database

# Setup logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class XReplyBot:
    """Main bot class"""
    
    def __init__(self, headless: bool = False, manual_approval: bool = False):
        self.driver = None
        self.headless = headless
        self.manual_approval = manual_approval
        self.db = Database()
        self.reply_engine = ReplyEngine()
        self.post_fetcher = None
        self.action_performer = None
        
        # Rate limiting
        self.max_replies_per_run = 20  # Max replies per execution
        self.min_delay_between_replies = 30  # seconds
        self.last_reply_time = 0
    
    def setup_driver(self) -> bool:
        """Setup Chrome driver with session persistence"""
        try:
            # Get profile directory for persistent session
            profile_dir = get_profile_dir()
            
            # Initialize undetected_chromedriver with user data dir
            # This maintains session persistence
            self.driver = uc.Chrome(
                user_data_dir=profile_dir,
                headless=self.headless
            )
            self.driver.maximize_window()
            
            logger.info("Driver initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            return False
    
    def login_if_needed(self) -> bool:
        """Check if login is needed and handle it"""
        try:
            logger.info("Navigating to X.com...")
            self.driver.get("https://x.com")
            time.sleep(3)
            
            # Try to load saved cookies
            if has_saved_session():
                logger.info("Loading saved session...")
                if load_cookies(self.driver):
                    # Refresh page to apply cookies
                    self.driver.refresh()
                    time.sleep(5)
            
            # Check if we're logged in by looking for home timeline or login button
            try:
                # Wait a bit for page to load
                time.sleep(3)
                
                # Check for login button (means we're not logged in)
                login_indicators = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "a[href='/i/flow/login'], [data-testid='loginButton']"
                )
                
                if login_indicators:
                    logger.warning("Not logged in. Please log in manually in the browser.")
                    logger.info("Waiting for manual login... (Press Enter in terminal when done)")
                    
                    if not self.manual_approval:
                        input("Please log in manually, then press Enter to continue...")
                    
                    # Wait for user to log in
                    time.sleep(60)
                    print("only 5 seconds remained to refresh")
                    time.sleep(5)
                    
                    # Check again if logged in
                    self.driver.refresh()
                    time.sleep(5)
                
                # Verify we're logged in by checking for timeline
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='tweet']"))
                )
                
                logger.info("Successfully logged in!")
                
                # Save cookies for next time
                save_cookies(self.driver)
                save_local_storage(self.driver)
                
                return True
                
            except TimeoutException:
                logger.error("Could not verify login status")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def run_once(self) -> int:
        """
        Run bot once - iterative approach to avoid stale elements
        Strategy: Scroll random -> Find visible -> Pick one -> Reply -> Repeat
        """
        replies_made = 0
        consecutive_failures = 0
        MAX_FAILURES = 5
        
        try:
            # Navigate to home feed
            logger.info("Navigating to home feed...")
            self.driver.get("https://x.com/home")
            time.sleep(5)
            
            # Initialize fetcher and performer
            self.post_fetcher = PostFetcher(self.driver)
            self.action_performer = ActionPerformer(self.driver)
            
            # Helper to check if we should continue
            while replies_made < self.max_replies_per_run:
                
                # 1. Random Scroll Loop to find a candidate
                # We try to scroll a few times to find a new interesting post
                found_candidate = False
                post_data = None
                
                # Try to find a valid post in current view or after scrolling
                search_attempts = 0
                while not found_candidate and search_attempts < 10:
                    search_attempts += 1
                    
                    # perform random scroll
                    self.action_performer.random_scroll_feed()
                    
                    # Get currently visible elements
                    visible_elements = self.post_fetcher.get_visible_tweet_elements()
                    
                    # Shuffle elements to pick randomly from view
                    random.shuffle(visible_elements)
                    
                    for element in visible_elements:
                        try:
                            # Extract data on the fly
                            p_data = self.post_fetcher.extract_post_data(element)
                            
                            if not p_data:
                                continue
                                
                            tweet_id = p_data['tweet_id']
                            
                            # Checks: 
                            # 1. Already replied?
                            if self.db.has_replied(tweet_id):
                                continue
                                
                            # 2. Appropriate content?
                            if not self.reply_engine.is_appropriate_tweet(p_data['text']):
                                continue
                            
                            # Found a good one!
                            post_data = p_data
                            found_candidate = True
                            logger.info(f"Found candidate tweet: {tweet_id} by @{post_data['username']}")
                            break
                            
                        except Exception as e:
                            # Element might have gone stale during check, ignore
                            continue
                    
                    if not found_candidate:
                        logger.info("No suitable tweets found in current view, scrolling...")
                
                if not found_candidate or not post_data:
                    logger.warning("Could not find any suitable tweets after multiple scrolls")
                    consecutive_failures += 1
                    if consecutive_failures >= MAX_FAILURES:
                        logger.error("Too many failures finding tweets, aborting run")
                        break
                    continue
                
                # Reset failure counter
                consecutive_failures = 0
                
                # 2. Reply Process
                tweet_id = post_data['tweet_id']
                username = post_data['username']
                tweet_text = post_data['text']
                article_element = post_data['element']
                
                # Generate reply
                reply_text = self.reply_engine.generate_reply(tweet_text, username)
                
                # Manual approval mode
                if self.manual_approval:
                    print(f"\n{'='*60}")
                    print(f"Tweet: {tweet_text[:100]}...")
                    print(f"Reply: {reply_text}")
                    print(f"{'='*60}")
                    # In a real headless/automated run, we can't easily wait for input if it's not interactive
                    # But for now we assume interactive
                    print("Waiting 5 seconds for visual inspection (automated approval in this mode)...")
                    time.sleep(5)
                
                # Rate limiting logic (wait if needed)
                time_since_last = time.time() - self.last_reply_time
                if time_since_last < self.min_delay_between_replies:
                    wait = self.min_delay_between_replies - time_since_last
                    logger.info(f"Waiting {wait:.1f}s for rate limit...")
                    time.sleep(wait)

                # Attempt Reply
                logger.info(f"Replying to @{username}")
                try:
                    success = self.action_performer.reply_to_tweet(article_element, reply_text)
                    
                    if success:
                        self.db.mark_replied(tweet_id, username, tweet_text, reply_text)
                        replies_made += 1
                        self.last_reply_time = time.time()
                        logger.info(f"Reply success! ({replies_made}/{self.max_replies_per_run})")
                        
                        # Long wait after success
                        sleep_time = random.uniform(20, 40)
                        logger.info(f"Sleeping {sleep_time:.1f}s before next search...")
                        time.sleep(sleep_time)
                    else:
                        logger.warning("Reply action failed")
                        
                except Exception as e:
                    logger.error(f"Exception during reply action: {e}")
                    # Likely stale element if we waited too long
            
            logger.info(f"Run complete. Total replies: {replies_made}")
            return replies_made
            
        except Exception as e:
            logger.error(f"Critical error in run_once: {e}")
            return replies_made
    
    def run_continuous(self, interval_minutes: int = 30):
        """Run bot continuously with intervals"""
        logger.info(f"Starting continuous mode (interval: {interval_minutes} minutes)")
        
        try:
            while True:
                replies = self.run_once()
                logger.info(f"Waiting {interval_minutes} minutes until next run...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            logger.info("Stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous mode: {e}")
    
    def start(self, continuous: bool = False, interval_minutes: int = 30):
        """Start the bot"""
        try:
            # Setup driver
            if not self.setup_driver():
                logger.error("Failed to setup driver")
                return
            
            # Login if needed
            if not self.login_if_needed():
                logger.error("Failed to login")
                return
            
            # Run bot
            if continuous:
                self.run_continuous(interval_minutes)
            else:
                self.run_once()
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        if self.driver:
            # Save cookies one more time
            save_cookies(self.driver)
            self.driver.quit()
        if self.db:
            self.db.close()
        logger.info("Cleanup complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="X Reply Bot")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=30, help="Interval in minutes (for continuous mode)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--manual-approval", action="store_true", help="Require manual approval for each reply")
    
    args = parser.parse_args()
    
    bot = XReplyBot(headless=args.headless, manual_approval=args.manual_approval)
    bot.start(continuous=args.continuous, interval_minutes=args.interval)

