# Desi Cine Bot 🎬

[![Run Daily Movie Notifier](https://github.com/Triples2307/desi-cine-bot/actions/workflows/movie-notifier.yml/badge.svg)](https://github.com/Triples2307/desi-cine-bot/actions/workflows/movie-notifier.yml)

A daily notification bot that tracks local movie schedules, pre-configured for Tamil cinema with support for other languages, and alerts you with showtimes.

## 🛠 Setup & Configuration

To enable automated alerts, add the following environment variables to your GitHub repository secrets:

* `TELEGRAM_BOT_TOKEN`: Your bot's API token obtained from @BotFather.
* `TELEGRAM_CHAT_ID`: The ID of the chat where you want to receive notifications.
* `PARSE_API_KEY`: The API key required to authenticate requests to the movie data scraping service.

## ⚙️ How It Works

1. **Fetch**: The bot runs on a daily schedule and queries the Parse Bot scraper API to gather local movie schedules for your configured theaters.
2. **Filter**: It scans the results for your target languages (default: **Tamil**).
3. **Notify**: If matches are found, it structures the data and sends a formatted message to your Telegram bot.

## 🤖 Technical Stack

*   **Language**: [Python 3.x](https://www.python.org/)
*   **Telegram Bot API**: Used to deliver daily showtime notifications. For more details on the API, refer to the [official Telegram Bot API documentation](https://core.telegram.org/bots/api). To get your bot set up, you will need to register a new bot with **@BotFather** on Telegram to generate your `TELEGRAM_BOT_TOKEN`.
*   **Data Retrieval**: The project integrates with [Parse Bot](https://parse.bot/) to fetch raw showtime data, which is then processed through custom logic to format the alerts sent to your Telegram bot.
*   **GitHub Actions**: Automates the daily execution of the scraper.

## 🔧 Customizing Languages

You can modify the target language directly in `main.py`. To track additional languages (like Telugu or Hindi), update the filter condition:

```python
# Targeting multiple languages
target_languages = ["Tamil", "Telugu", "Hindi"]
matches = [m for m in raw_showtimes if any(lang in m.get('language', '') for lang in target_languages)]
