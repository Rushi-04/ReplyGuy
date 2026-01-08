"""
Main entry point for X Reply Bot
Run this file to start the bot
"""
from bot import XReplyBot
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="X Reply Bot - Automated positive replies on X/Twitter")
    parser.add_argument(
        "--continuous", 
        action="store_true", 
        help="Run continuously with intervals (default: run once)"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=30, 
        help="Interval in minutes between runs (for continuous mode, default: 30)"
    )
    parser.add_argument(
        "--headless", 
        action="store_true", 
        help="Run browser in headless mode (no visible window)"
    )
    parser.add_argument(
        "--manual-approval", 
        action="store_true", 
        help="Require manual approval for each reply before posting"
    )
    parser.add_argument(
        "--max-replies", 
        type=int, 
        default=20, 
        help="Maximum replies per run (default: 20)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("X Reply Bot - Starting...")
    print("=" * 60)
    print(f"Mode: {'Continuous' if args.continuous else 'Single Run'}")
    if args.continuous:
        print(f"Interval: {args.interval} minutes")
    print(f"Max replies per run: {args.max_replies}")
    print(f"Manual approval: {'Yes' if args.manual_approval else 'No'}")
    print("=" * 60)
    print()
    
    bot = XReplyBot(headless=args.headless, manual_approval=args.manual_approval)
    bot.max_replies_per_run = args.max_replies
    bot.start(continuous=args.continuous, interval_minutes=args.interval)
