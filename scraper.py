import requests
import os
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

def clean_date_to_iso(raw_month, raw_day, year):
    """Converts rough Wikipedia month/day data into standard YYYY-MM-DD."""
    month_map = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }
    
    month_key = str(raw_month).lower().strip()[:3]
    mm = month_map.get(month_key)
    
    day_digits = ''.join(filter(str.isdigit, str(raw_day)))
    
    if mm and day_digits:
        return f"{year}-{mm}-{day_digits.zfill(2)}"
    
    return f"{raw_month} {raw_day}, {year}".strip()


def extract_language(language_string):
    # Mapping for easy cleaning
    languages = ["Hindi", "Telugu", "Tamil", "Kannada", "Malayalam", "English", "Spanish"]
    for lang in languages:
        if lang in language_string:
            return lang
    return "English" # Default if nothing else is found

def extract_language_from_text(text):
    text = text.lower()
    if "spanish" in text: return "Spanish"
    if "hindi" in text: return "Hindi"
    if "telugu" in text: return "Telugu"
    if "tamil" in text: return "Tamil"
    if "japanese" in text: return "Japanese"
    if "korean" in text: return "Korean"
    return "English" # Default

def get_live_showtimes_for_theaters(tracked_theaters):
    results = []    
    
    for theater in tracked_theaters:
        load_dotenv()
        
        if theater['company'] == 'Cinemark':
            response = requests.get(
                "https://api.parse.bot/scraper/419c732a-574b-40b8-a153-54dce7810331/get_showtimes",
                headers={"X-API-Key": os.getenv("PARSE_API_KEY")},
                params={
                    "theater_name": theater['name']
                },
            )
            data = response.json()
            raw_showtimes = data.get('data', {}).get('showtimes', [])
            
            grouped_movies = defaultdict(list)
            for entry in raw_showtimes:
                movie_name = entry['movieName']
                dt = datetime.fromisoformat(entry['sessionDateTime'])
                time_str = dt.strftime("%I:%M %p")
                
                grouped_movies[movie_name].append(time_str)

            for movie_title, all_times in grouped_movies.items():

                results.append({
                    "theater": theater['name'],
                    "movie": movie_title,
                    "language": extract_language_from_text(movie_title),
                    "showtimes": sorted(list(set(all_times)))
                })
                    
    
        if theater['company'] == 'AMC':
            response = requests.get(
                "https://api.parse.bot/scraper/52c31c90-81d2-412e-ab12-c18bfddf9da8/get_showtimes",
                headers={"X-API-Key": os.getenv("PARSE_API_KEY")},
                params={
                    "theatre": theater['name']
                },
            )

            all_movies = response.json().get('data', {}).get('movies', [])
            for movie in all_movies:
                all_times = []
                detected_language = "English"
                
                for group in movie['showtime_groups']:
                    if 'language' in group and group['language']:
                        detected_language = extract_language(group['language'])
                    
                    for st in group['showtimes']:
                        if st['availability'] == 'Available':
                            all_times.append(st['time'])
                
                
                if all_times:
                    results.append({
                        "theater": theater['name'],
                        "movie": movie['title'],
                        "language": detected_language,
                        "showtimes": sorted(list(set(all_times)))
                    })    
    return results