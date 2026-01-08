"""
Action Performer - Handles human-like interactions with X/Twitter
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import logging

logger = logging.getLogger(__name__)


class ActionPerformer:
    """Performs human-like actions on X/Twitter"""
    
    def __init__(self, driver: WebDriver, wait_timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
    
    def human_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def human_type(self, element, text: str, typing_speed: float = 0.1):
        """Type text character by character like a human"""
        element.clear()
        for char in text:
            element.send_keys(char)
            # Random typing speed variation
            time.sleep(random.uniform(typing_speed * 0.7, typing_speed * 1.5))
    
    def scroll_to_element(self, element):
        """Scroll element into view"""
        try:
            # Use javascript to scroll into view with offset to avoid sticky headers
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                element
            )
            self.human_delay(0.5, 1.0)
        except Exception as e:
            logger.warning(f"Error scrolling to element: {e}")

    def random_scroll_feed(self) -> bool:
        """
        Scroll randomly to simulate human browsing
        Returns True if scrolled effectively
        """
        try:
            # Random scroll distance between 200 and 800 pixels
            scroll_amount = random.randint(300, 900)
            
            # 20% chance to scroll UP a little (like checking something you missed)
            if random.random() < 0.2:
                scroll_amount = -random.randint(200, 400)
                
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # Variable delay after scroll (reading time)
            self.human_delay(1.0, 3.5)
            
            return True
        except Exception as e:
            logger.error(f"Error scrolling feed: {e}")
            return False
    
    def click_reply_button(self, article_element) -> bool:
        """
        Click the reply button on a tweet
        
        Args:
            article_element: The article element containing the tweet
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Multiple selectors to try for reply button
            reply_selectors = [
                "[data-testid='reply']",
                "button[aria-label*='Reply']",
                "button[aria-label*='reply']",
                "div[role='button'][aria-label*='Reply']",
            ]
            
            reply_button = None
            for selector in reply_selectors:
                try:
                    reply_button = article_element.find_element(By.CSS_SELECTOR, selector)
                    if reply_button.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not reply_button:
                logger.warning("Reply button not found")
                return False
            
            # Scroll to button
            self.scroll_to_element(reply_button)
            
            # Click with human delay
            self.human_delay(0.3, 0.8)
            reply_button.click()
            logger.info("Clicked reply button")
            
            # Wait for reply box to appear
            self.human_delay(1.0, 2.0)
            return True
            
        except Exception as e:
            logger.error(f"Failed to click reply button: {e}")
            return False
    
    def type_reply(self, reply_text: str) -> bool:
        """
        Type the reply text into the reply box
        
        Args:
            reply_text: The text to reply with
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Wait for reply text box to appear
            reply_box_selectors = [
                "div[data-testid='tweetTextarea_0']",
                "div[role='textbox']",
                "div[contenteditable='true'][data-testid='tweetTextarea_0']",
                "div[contenteditable='true']",
            ]
            
            reply_box = None
            for selector in reply_box_selectors:
                try:
                    reply_box = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if reply_box.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if not reply_box:
                logger.error("Reply text box not found")
                return False
            
            # Click on the text box first
            self.scroll_to_element(reply_box)
            self.human_delay(0.3, 0.7)
            reply_box.click()
            self.human_delay(0.5, 1.0)
            
            # Type the reply
            time.sleep(3)
            self.human_type(reply_box, reply_text, typing_speed=0.08)
            logger.info(f"Typed reply: {reply_text[:50]}...")
            
            # Wait a bit before posting
            self.human_delay(1.0, 2.5)
            return True
            
        except Exception as e:
            logger.error(f"Failed to type reply: {e}")
            return False
    
    def post_reply(self) -> bool:
        """
        Click the post/tweet button to submit the reply
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # # Multiple selectors for the post button
            # post_button_selectors = [
            #     "button[data-testid='tweetButton']",
            #     "button[data-testid='tweetButtonInline']",
            #     "button[type='button']:has-text('Post')", 
            # ]

            # Multiple selectors for the post button (UPDATED)
            post_button_selectors = [
                # Original stable selectors
                "button[data-testid='tweetButton']",
                "button[data-testid='tweetButtonInline']",
                "button[type='button']:has-text('Post')",

                # ---- NEW ADDED BY YOU ----

                # Fallback using full CSS path (less stable but works if others fail)
                "#layers button span:has-text('Post')",

                # Exact XPath from layers (most reliable in modal composer)
                "xpath=//*[@id='layers']//button[.//span//span[text()='Post']]",

                # Direct raw XPath you provided (last-resort)
                "xpath=//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div/div/button"
            ]

            
            post_button = None
            for selector in post_button_selectors:
                try:
                    # Try to find button by data-testid first
                    if "data-testid" in selector:
                        post_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    else:
                        # Try to find by text
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            if "post" in btn.text.lower() and btn.is_displayed():
                                post_button = btn
                                break
                    
                    if post_button and post_button.is_displayed() and post_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not post_button:
                logger.error("Post button not found")
                return False
            
            # Scroll to button
            self.scroll_to_element(post_button)
            self.human_delay(0.5, 1.0)
            
            # Click post button
            time.sleep(10)
            post_button.click()
            logger.info("Clicked post button")
            
            # Wait for reply to be posted
            self.human_delay(2.0, 3.0)
            
            # Verify reply was posted (check if reply box disappeared)
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[data-testid='tweetTextarea_0']"))
                )
                logger.info("Reply posted successfully")
                return True
            except TimeoutException:
                logger.warning("Reply box still visible, but continuing...")
                return True  # Still return True as it might have posted
            
        except Exception as e:
            logger.error(f"Failed to post reply: {e}")
            return False
    
    def reply_to_tweet(self, article_element, reply_text: str) -> bool:
        """
        Complete flow: click reply, type, and post
        
        Args:
            article_element: The article element containing the tweet
            reply_text: The text to reply with
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step 1: Click reply button
            if not self.click_reply_button(article_element):
                return False
            
            # Step 2: Type reply
            if not self.type_reply(reply_text):
                return False
            
            # Step 3: Post reply
            if not self.post_reply():
                return False
            
            logger.info("Successfully replied to tweet")
            return True
            
        except Exception as e:
            logger.error(f"Error in reply flow: {e}")
            return False

