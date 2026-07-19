# Desi Cine Bot 🎬

A daily notification bot that tracks local movie schedules, filters for Indian cinema, and alerts you with direct ticket links.

<div style="margin-bottom: 20px;"></div>

<h2>🔄 Process Workflow</h2>

<div style="margin-top: 10px; margin-bottom: 20px;">
    <img src="assets/workflow.png" alt="Process Workflow" width="100%">
</div>

---

## 🛠 Setup & Configuration

To enable automated alerts, add the following environment variables to your GitHub repository secrets:

* `TELEGRAM_BOT_TOKEN`: Your bot's API token obtained from @BotFather.
* `TELEGRAM_CHAT_ID`: The ID of the chat where you want to receive notifications.

## ⚙️ How It Works

1. **Fetch**: The bot runs on a daily schedule and gathers showtimes from your configured theaters.
2. **Filter**: It scans the results for your target languages (default: **Tamil**).
3. **Notify**: If matches are found, it structures the data and sends a formatted message to your Telegram bot.

## 🤖 Technical Stack

* **Language**: Python 3.x
* **Telegram Bot API**: Used to deliver daily showtime notifications. To get your bot set up, you will need to register a new bot with **@BotFather** on Telegram to generate your `TELEGRAM_BOT_TOKEN`.
* **Data Parsing**: The project uses custom logic to scrape and transform raw showtime data into a nested structure for clean message formatting.
* **GitHub Actions**: Automates the daily execution of the scraper.

## 🔧 Customizing Languages

You can modify the target language directly in `main.py`. To track additional languages (like Telugu or Hindi), update the filter condition:

```python
# Targeting multiple languages
target_languages = ["Tamil", "Telugu", "Hindi"]
matches = [m for m in raw_showtimes if any(lang in m.get('language', '') for lang in target_languages)]
