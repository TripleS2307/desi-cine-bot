import os
import requests
from dotenv import load_dotenv

from datetime import datetime

# Load your .env variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_header():
    date_str = datetime.now().strftime("%A %B %d, %Y")
    return f"🎬 *Showtimes for {date_str}*\n\n"

def format_movie_message(showtime_data):
    message = get_header()
    
    for movie, info in showtime_data.items():
            # Print movie and its language
            message += f"*{movie}* ({info['language']})\n"
            
            for theater, times in info['theaters'].items():
                time_str = ", ".join(times)
                message += f"• *{theater}*: {time_str}\n"
            message += "\n"
            
    return message

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status() # Raises an error for bad HTTP codes
        print("Message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")