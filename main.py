import json
from scraper import get_live_showtimes_for_theaters
from notifier import format_movie_message, send_telegram_message
from datetime import datetime
import sys

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

    tamil_movies = [m for m in raw_showtimes if "Tamil" in m.get("language", "")]

    if not tamil_movies:
        print("No Tamil movies found for today. Skipping notification.")
    else:
        grouped_data = transform_data(tamil_movies)
        final_message = format_movie_message(grouped_data)
        send_telegram_message(final_message)

    # Filter out empty movie warnings so they don't trigger a build failure
    real_errors = [e for e in errors if "Scraper returned 0 movies" not in e]
    
    if real_errors:
        print(f"Workflow failing due to {len(real_errors)} real errors.")
        sys.exit(1)
    else:
        print("All checks passed cleanly (ignoring empty theater schedules).")
        sys.exit(0)


if __name__ == "__main__":
    main()
