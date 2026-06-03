import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

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

def get_wikipedia_films(language, year):
    """Scrapes Wikipedia film lists dynamically using language and year parameters."""
    # 1. Try the standard public mainspace URL first
    url = f"https://en.wikipedia.org/wiki/List_of_{language.capitalize()}_films_of_{year}"
    headers = {
        'User-Agent': 'DesiCineBot/1.0 (https://github.com/TripleS2307/desi-cine-bot; contact: siddsundar9@gmail.com)',
        'Accept-Encoding': 'gzip'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # 2. FIXED: If the main page returns a 404, automatically look for a Draft page instead
        if response.status_code == 404:
            draft_url = f"https://en.wikipedia.org/wiki/Draft:List_of_{language.capitalize()}_films_of_{year}"
            print(f"Main page for {language} ({year}) not found. Trying draft space...")
            response = requests.get(draft_url, headers=headers, timeout=10)
            
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {language} ({year}): {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find(id="mw-content-text")
    if not content:
        return []

    for nav in content.find_all("table", {"class": "navbox"}):
        nav.decompose()
    for ref in content.find_all(["div", "ol"], {"class": ["reflist", "references"]}):
        ref.decompose()

    try:
        tables = pd.read_html(StringIO(str(content)))
    except ValueError:
        return []

    movies_list = []
    
    for table in tables:
        cols = [str(c).lower() for c in table.columns]
        
        if any('gross' in c or 'box office' in c for c in cols):
            continue
            
        title_idx = next((i for i, c in enumerate(cols) if 'title' in c), None)
        if title_idx is None:
            continue
            
        director_idx = next((i for i, c in enumerate(cols) if 'director' in c), None)
        cast_idx = next((i for i, c in enumerate(cols) if 'cast' in c or 'actor' in c), None)
        prod_idx = next((i for i, c in enumerate(cols) if 'production' in c or 'studio' in c), None)
        
        month_idx = title_idx - 2 if title_idx >= 2 else None
        day_idx = title_idx - 1 if title_idx >= 1 else None

        for _, row in table.iterrows():
            raw_title = str(row.iloc[title_idx]).split('[')[0].strip()
            
            if raw_title.lower() in ['nan', '', 'title', 'movie title', 'film', 'rank'] or 'title' in raw_title.lower():
                continue
                
            raw_director = str(row.iloc[director_idx]).split('[')[0].strip() if director_idx is not None else ""
            raw_cast = str(row.iloc[cast_idx]).split('[')[0].strip() if cast_idx is not None else ""
            raw_production = str(row.iloc[prod_idx]).split('[')[0].strip() if prod_idx is not None else ""
            
            if raw_director.lower() in ['director', 'nan'] and raw_cast.lower() in ['cast', 'nan']:
                continue
                
            raw_month = str(row.iloc[month_idx]).replace(" ", "").split('[')[0].strip() if month_idx is not None else ""
            raw_day = str(row.iloc[day_idx]).split('[')[0].strip() if day_idx is not None else ""
            
            if raw_month.lower() == 'nan' or raw_month.isdigit():
                raw_month = ""
                
            opening_date = clean_date_to_iso(raw_month, raw_day, year)
            
            if raw_cast.lower() not in ['nan', '']:
                cast_array = [actor.strip() for actor in raw_cast.split(',') if actor.strip()]
            else:
                cast_array = []
            
            movies_list.append({
                "title": raw_title,
                "language": language.capitalize(),
                "year": int(year),
                "opening": opening_date,
                "director": raw_director,
                "cast": cast_array,
                "production_company": raw_production
            })

    return movies_list

if __name__ == "__main__":
    languages = ["Tamil", "Hindi", "Telugu", "Malayalam", "Kannada", "Punjabi"]
    year = 2026
    all_movies = []

    print(f"--- Starting Scraper Loop for {year} ---")
    
    for lang in languages:
        print(f"Scraping {lang}...")
        lang_data = get_wikipedia_films(language=lang, year=year)
        print(f"-> Found {len(lang_data)} films.")
        all_movies.extend(lang_data)

    output_filename = f"all_desi_films_{year}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_movies, f, indent=4, ensure_ascii=False)
        
    print(f"\nSuccess! Saved a total of {len(all_movies)} films to {output_filename}")