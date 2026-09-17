# Free Fire Update Notifier

Automatically checks for new Free Fire updates/news/events and sends you a
Telegram message when something new appears. Runs for free on GitHub Actions
— no server needed.

## How it works
- `checker.py` visits the sources listed in `config.json`
- It compares what it finds against `state.json` (what it saw last time)
- Anything new gets sent to you on Telegram
- GitHub Actions runs this automatically every 3 hours (edit the schedule in
  `.github/workflows/check.yml` if you want it more/less frequent)

## One-time setup (about 10 minutes)

### 1. Create a Telegram bot
1. Open Telegram, search for **@BotFather**, start a chat.
2. Send `/newbot`, give it a name and a username (must end in "bot").
3. BotFather will give you a **bot token** — looks like `123456:ABC-defGhIjk...`. Save it.
4. Send your new bot any message (e.g. "hi") so it knows about you.
5. Get your **chat ID**: open this URL in your browser (replace `<TOKEN>`):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
   Look for `"chat":{"id":123456789,...}` — that number is your chat ID.

### 2. Put the code on GitHub
1. Create a new **private** GitHub repository (e.g. `ff-update-notifier`).
2. Upload all the files in this folder to that repo (drag-and-drop on
   github.com works, or use `git push` if you're comfortable with git).

### 3. Add your secrets
1. In your repo: **Settings → Secrets and variables → Actions → New repository secret**
2. Add two secrets:
   - `TELEGRAM_BOT_TOKEN` = the token from BotFather
   - `TELEGRAM_CHAT_ID` = your chat ID

### 4. Turn it on
1. Go to the **Actions** tab of your repo → you should see "Free Fire Update Check".
2. Click **Run workflow** to trigger it manually the first time (this
   "baselines" it — it won't message you yet, it just learns what's
   currently there).
3. After that, it runs automatically every 3 hours and will message you
   only when something NEW shows up.

## Customizing sources
Edit `config.json` to add/remove/change sources. Each source needs:
- `name`: label shown in your alert
- `url`: the page to check
- `item_selector`: a CSS selector picking out the headline/link elements on
  that page (this may need small tweaks if a site changes its layout —
  just tell me the page and I'll help you find the right selector)

## Future improvements we can add
- More sources (Instagram/X via a scraping-friendly proxy, YouTube uploads via RSS)
- Smarter filtering (only alert on "new character", "new event", "OB update" etc.)
- Daily digest option instead of instant alerts
- Multiple recipients / a Discord version
