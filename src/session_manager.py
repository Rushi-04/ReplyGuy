"""
Session Manager - Handles cookie and session persistence
Saves and loads browser cookies to avoid re-login
"""
import pickle
import json
import os
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver
import logging

logger = logging.getLogger(__name__)

SESSION_DIR = Path(__file__).parent.parent / "session"
COOKIES_FILE = SESSION_DIR / "cookies.pkl"
LOCAL_STORAGE_FILE = SESSION_DIR / "local_storage.json"
PROFILE_DIR = SESSION_DIR / "profile"

# Ensure session directory exists
SESSION_DIR.mkdir(exist_ok=True)
PROFILE_DIR.mkdir(exist_ok=True)


def save_cookies(driver: WebDriver) -> bool:
    """Save browser cookies to file"""
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, 'wb') as f:
            pickle.dump(cookies, f)
        logger.info(f"Saved {len(cookies)} cookies to {COOKIES_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to save cookies: {e}")
        return False


def load_cookies(driver: WebDriver) -> bool:
    """Load cookies from file and add to browser"""
    try:
        if not COOKIES_FILE.exists():
            logger.info("No saved cookies found")
            return False
        
        with open(COOKIES_FILE, 'rb') as f:
            cookies = pickle.load(f)
        
        # Navigate to domain first (required for adding cookies)
        driver.get("https://x.com")
        
        for cookie in cookies:
            try:
                # Remove 'expiry' if it's causing issues (some cookies have invalid expiry)
                cookie_dict = {k: v for k, v in cookie.items() if k != 'expiry' or v is not None}
                driver.add_cookie(cookie_dict)
            except Exception as e:
                logger.warning(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}")
                continue
        
        logger.info(f"Loaded {len(cookies)} cookies")
        return True
    except Exception as e:
        logger.error(f"Failed to load cookies: {e}")
        return False


def save_local_storage(driver: WebDriver) -> bool:
    """Save local storage data (if needed)"""
    try:
        local_storage = driver.execute_script("return window.localStorage;")
        with open(LOCAL_STORAGE_FILE, 'w') as f:
            json.dump(local_storage, f, indent=2)
        logger.info("Saved local storage")
        return True
    except Exception as e:
        logger.warning(f"Failed to save local storage: {e}")
        return False


def load_local_storage(driver: WebDriver) -> bool:
    """Load local storage data"""
    try:
        if not LOCAL_STORAGE_FILE.exists():
            return False
        
        with open(LOCAL_STORAGE_FILE, 'r') as f:
            local_storage = json.load(f)
        
        driver.execute_script("window.localStorage.clear();")
        for key, value in local_storage.items():
            driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
        
        logger.info("Loaded local storage")
        return True
    except Exception as e:
        logger.warning(f"Failed to load local storage: {e}")
        return False


def get_profile_dir() -> str:
    """Get the Chrome profile directory path"""
    return str(PROFILE_DIR)


def has_saved_session() -> bool:
    """Check if a saved session exists"""
    return COOKIES_FILE.exists() or PROFILE_DIR.exists()

