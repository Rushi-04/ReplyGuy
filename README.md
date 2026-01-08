# X Reply Bot 

An automated X (Twitter) reply bot that generates positive, encouraging, and supportive replies to tweets. Built with Python and Selenium.

## Features 

- **AI-Powered Replies**: Uses Google Gemini AI to generate human-like, enthusiastic replies
- **Session Persistence**: Login once, reuse session forever - no repeated logins needed
- **Smart Post Fetching**: Automatically finds and extracts tweets from your feed
- **Human-like Replies**: AI generates authentic, enthusiastic replies like a real software engineer
- **Duplicate Prevention**: Tracks replied tweets to avoid duplicates
- **Human-like Behavior**: Random delays, typing speed variations, natural scrolling
- **Rate Limiting**: Built-in safety to avoid spam detection
- **Manual Approval Mode**: Review replies before posting (optional)
- **Comprehensive Logging**: All actions logged for monitoring

## Installation 

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
```

3. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage 

### First Time Setup

1. **Run the bot** (it will open a browser):
```bash
python src/main.py --manual-approval
```

2. **Log in manually** when the browser opens:
   - The bot will wait for you to log in to X/Twitter
   - After logging in, press Enter in the terminal
   - Your session will be saved automatically

3. **Subsequent runs** will use the saved session - no login needed!

### Running the Bot

**Single run** (recommended for testing):
```bash
python src/main.py
```

**Continuous mode** (runs every 30 minutes):
```bash
python src/main.py --continuous --interval 30
```

**With manual approval** (review each reply before posting):
```bash
python src/main.py --manual-approval
```

**Headless mode** (no visible browser):
```bash
python src/main.py --headless
```

**Custom max replies per run**:
```bash
python src/main.py --max-replies 10
```

### Command Line Options

- `--continuous`: Run continuously with intervals
- `--interval N`: Minutes between runs (default: 30)
- `--headless`: Run browser in background
- `--manual-approval`: Require approval for each reply
- `--max-replies N`: Maximum replies per run (default: 5)

## How It Works 

1. **Session Management**: 
   - Uses Chrome user profile directory to persist login
   - Saves cookies for additional session persistence
   - No credentials stored - you log in once manually

2. **Post Fetching**:
   - Navigates to X.com home feed
   - Scrolls to load posts
   - Extracts tweet ID, username, and text

3. **Reply Generation**:
   - Uses template-based system for natural variety
   - Generates positive, encouraging messages
   - Filters inappropriate content

4. **Action Execution**:
   - Human-like delays and typing speed
   - Natural scrolling and clicking
   - Tracks all replies in SQLite database

5. **Safety Features**:
   - Rate limiting (minimum delay between replies)
   - Duplicate detection
   - Content filtering
   - Maximum replies per run

## Project Structure 

```
ReplyGuy/
├── src/
│   ├── main.py              # Entry point
│   ├── bot.py               # Main bot orchestrator
│   ├── session_manager.py   # Cookie/session persistence
│   ├── fetch_posts.py      # Tweet extraction
│   ├── reply_engine.py     # Reply generation
│   ├── action.py           # Human-like actions
│   └── database.py         # Reply tracking
├── session/                # Saved sessions (cookies, profile)
├── logs/                   # Log files
└── requirements.txt        # Dependencies
```

## Configuration 

### Rate Limiting

Edit `src/bot.py` to adjust:
- `max_replies_per_run`: Maximum replies per execution (default: 5)
- `min_delay_between_replies`: Minimum seconds between replies (default: 30)

### AI Reply Generation

Edit `src/reply_engine.py` to customize:
- AI prompt/system instructions
- Temperature and generation parameters
- Reply style and tone
- The bot uses Google Gemini API for generating replies

### Content Filtering

Edit `src/reply_engine.py` in `is_appropriate_tweet()` to:
- Add blocklisted words
- Customize filtering logic

## Safety & Best Practices 

1. **Start with manual approval mode** to review replies
2. **Use conservative rate limits** (5-10 replies per run)
3. **Monitor logs** regularly
4. **Respect X/Twitter's terms of service**
5. **Don't spam** - the bot includes rate limiting, but use responsibly
6. **Test thoroughly** before running continuously

## Troubleshooting 

**Bot can't find tweets:**
- X/Twitter may have changed their HTML structure
- Check logs for errors
- Try scrolling manually first

**Session not persisting:**
- Check `session/` directory exists
- Delete `session/` folder and re-login
- Ensure browser closes properly (don't force quit)

**Replies not posting:**
- X/Twitter may have changed button selectors
- Check logs for specific errors
- Try manual approval mode to see what's happening

**Browser detection:**
- The bot uses `undetected-chromedriver` to avoid detection
- If issues persist, try running in non-headless mode

## Logs 

Logs are saved in `logs/` directory with format:
- `bot_YYYYMMDD.log` - Daily log files

Check logs for:
- Successful replies
- Errors and warnings
- Tweet extraction details

## Database 

Replied tweets are tracked in:
- `session/replied_tweets.db` - SQLite database

Contains:
- Tweet IDs
- Usernames
- Tweet text
- Reply text
- Timestamp

## License 

This project is for educational purposes. Use responsibly and in accordance with X/Twitter's Terms of Service.

## Disclaimer 

This bot is provided as-is for educational purposes. Automated interactions on social media platforms may violate their terms of service. Use at your own risk and responsibility.

