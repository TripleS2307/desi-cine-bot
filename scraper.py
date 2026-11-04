import requests
import os
from dotenv import load_dotenv
from collections import defaultdict, Counter
from datetime import datetime

load_dotenv()  # once, at the top of the file

SCRAPERS = {
    "Cinemark": {
        "url": "https://api.parse.bot/scraper/419c732a-574b-40b8-a153-54dce7810331/get_showtimes",
        "param": "theater_name",
    },
    "AMC": {
        "url": "https://api.parse.bot/scraper/52c31c90-81d2-412e-ab12-c18bfddf9da8/get_showtimes",
        "param": "theatre",
    },
}


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
    languages = ["Hindi", "Telugu", "Tamil", "Kannada", "Malayalam", "English", "Spanish"]
    for lang in languages:
        if lang in language_string:
            return lang
    return "English"  # Default if nothing else is found


def extract_language_from_text(text):
    text = text.lower()
    if "spanish" in text: return "Spanish"
    if "hindi" in text: return "Hindi"
    if "telugu" in text: return "Telugu"
    if "tamil" in text: return "Tamil"
    if "japanese" in text: return "Japanese"
    if "korean" in text: return "Korean"
    return "English"  # Default


def fetch_json(url, params):
    response = requests.get(
        url,
        headers={"X-API-Key": os.getenv("PARSE_API_KEY")},
        params=params,
        timeout=30,
    )
    print(f"{response.status_code} {response.headers.get('Content-Type')} <- {params}")
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
    try:
        return response.json()
    except ValueError:
        raise RuntimeError(f"Non-JSON body: {response.text[:300]}")


def parse_cinemark(data, theater):
    grouped = defaultdict(list)
    for entry in data.get("data", {}).get("showtimes", []):
        dt = datetime.fromisoformat(entry["sessionDateTime"])
        grouped[entry["movieName"]].append(dt.strftime("%I:%M %p"))
    return [
        {
            "theater": theater["name"],
            "movie": title,
            "language": extract_language_from_text(title),
            "showtimes": sorted(set(times)),
        }
        for title, times in grouped.items()
    ]


def parse_amc(data, theater):
    results = []
    for movie in data.get("data", {}).get("movies", []):
        times, language = [], "English"
        for group in movie.get("showtime_groups", []):
            if group.get("language"):
                language = extract_language(group["language"])
            times += [
                st["time"]
                for st in group.get("showtimes", [])
                if st.get("availability") == "Available"
            ]
        if times:
            results.append({
                "theater": theater["name"],
                "movie": movie["title"],
                "language": language,
                "showtimes": sorted(set(times)),
            })
    return results


PARSERS = {"Cinemark": parse_cinemark, "AMC": parse_amc}


def get_live_showtimes_for_theaters(tracked_theaters):
    results, errors = [], []
    for theater in tracked_theaters:
        company = theater["company"]
        try:
            scraper = SCRAPERS[company]
            data = fetch_json(scraper["url"], {scraper["param"]: theater["name"]})
            theater_results = PARSERS[company](data, theater)
            if not theater_results:
                raise RuntimeError("Scraper returned 0 movies (empty data or name mismatch)")
            results += theater_results
        except Exception as e:
            errors.append(f"{theater['name']} ({company}): {e}")

    # --- Temporary debug output: delete once you've confirmed detection works ---
    print(f"Total entries: {len(results)}")
    for theater in tracked_theaters:
        n = [r for r in results if r["theater"] == theater["name"]]
        print(f"  {theater['name']}: {len(n)} movies")
    print("Languages detected:", Counter(r["language"] for r in results))
    for r in results:
        print(f"  [{r['language']}] {r['movie']} @ {r['theater']}")
    # ---------------------------------------------------------------------------

    return results, errors
