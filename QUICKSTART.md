# Quick Start Guide 🚀

Get your X Reply Bot running in 3 steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: First Run (Login)

Run the bot with manual approval to log in:

```bash
python src/main.py --manual-approval
```

**What happens:**
1. Browser opens automatically
2. **You log in to X/Twitter manually** (enter your credentials)
3. Press Enter in terminal when logged in
4. Bot saves your session
5. Bot will ask for approval on each reply (for testing)

## Step 3: Run Automatically

Now you can run without manual approval:

```bash
python src/main.py
```

**That's it!** The bot will:
- ✅ Use your saved session (no login needed)
- ✅ Find posts on your feed
- ✅ Generate positive replies
- ✅ Post them automatically

## Advanced Usage

**Run continuously** (every 30 minutes):
```bash
python src/main.py --continuous
```

**Custom interval** (every 60 minutes):
```bash
python src/main.py --continuous --interval 60
```

**More replies per run**:
```bash
python src/main.py --max-replies 10
```

## Troubleshooting

**"Not logged in" error:**
- Delete the `session/` folder
- Run Step 2 again to re-login

**No posts found:**
- Make sure you're following accounts
- Try scrolling your feed manually first
- Check logs in `logs/` folder

**Need help?**
- Check `README.md` for detailed documentation
- Review logs in `logs/` directory

## Safety Tips

1. **Start small**: Use `--max-replies 2` for testing
2. **Review first**: Use `--manual-approval` initially
3. **Monitor logs**: Check `logs/` folder regularly
4. **Be responsible**: Don't spam, respect rate limits

Happy replying! 🎉

