import json
from scraper import get_live_showtimes_for_theaters
from notifier import format_movie_message, send_telegram_message
from datetime import datetime

def transform_data(raw_data):
    """Pivots the flat list of dictionaries into a nested {movie: {theater: [times]}} structure."""
    grouped_data = {}
    for entry in raw_data:
        movie = entry["movie"]
        theater = entry["theater"]
        times = entry["showtimes"]
        lang = entry.get("language", "Unknown")
        
        if movie not in grouped_data:
            grouped_data[movie] = {"language": lang, "theaters": {}}
        
        grouped_data[movie]["theaters"][theater] = times
    return grouped_data

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    raw_showtimes, errors = get_live_showtimes_for_theaters(config["tracked_theaters"])

    # Alert yourself about scraper failures, even if some theaters worked
    if errors:
        error_message = "⚠️ Desi Cine Bot scraper errors:\n" + "\n".join(errors)
        print(error_message)
        send_telegram_message(error_message)

    tamil_movies = [m for m in raw_showtimes if "Tamil" in m.get("language", "")]

    if not tamil_movies:
        print("No Tamil movies found for today. Skipping notification.")
    else:
        grouped_data = transform_data(tamil_movies)
        final_message = format_movie_message(grouped_data)
        send_telegram_message(final_message)

    # Make the workflow badge go red if anything failed
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
