from bs4 import BeautifulSoup
from scraping import get_page
from datetime import date, timedelta
import progressbar
from storage import LyricsDatabase
import re
import os.path
import json

START_DATE = date.fromisoformat("1962-01-06")
END_DATE = date.fromisoformat("1970-01-01")

DATES_PROCESSED_PATH = "./chart-dates-processed.tmp"

INVALID_CHARS_REGEX = re.compile("[^A-Za-z0-9]")

def normalise(s):
    return INVALID_CHARS_REGEX.sub("", s).lower()

def get_top100_chart(d):
    pg = get_page(f"https://www.billboard.com/charts/hot-100/{d}")
    soup = BeautifulSoup(pg.content, "html.parser")
    names = [e.text for e in soup.find_all("span", class_="chart-element__information__song text--truncate color--primary")]
    artists = [e.text for e in soup.find_all("span", class_="chart-element__information__artist text--truncate color--secondary")]
    if len(names) != 100 or len(artists) != 100:
        print(f"Uh oh, chart took unexpected format. Only found {len(names)} songs and {len(artists)} artists.")
        return None
    songs = []
    for i, (name, artist) in enumerate(zip(names, artists)):
        songs.append({
            "name": name,
            "artist": artist,
            # 1st gets 100 points, 2nd gets 99 points, and so on.
            # Not a perfect metric, but it'll have to do.
            "success-score": 100-i,
            "id": normalise(artist) + "-" + normalise(name)
        })
    return songs

def main():
    db = LyricsDatabase("./lyrics/charts/")

    dates = []
    d = START_DATE
    while d < END_DATE:
        dates.append(d.isoformat())
        d += timedelta(days=7)

    if not os.path.exists(DATES_PROCESSED_PATH):
        with open(DATES_PROCESSED_PATH, "w") as f:
            json.dump([], f)
    with open(DATES_PROCESSED_PATH, "r") as f:
        dates_processed = json.load(f)
        print(f"{len(dates_processed)} chart dates of {len(dates)} already processed.")
        dates = [d for d in dates if d not in dates_processed]
        print(f"Processing remaining {len(dates)}.")

    n = 0
    for d in progressbar.progressbar(dates):
        try:
            songs = get_top100_chart(d)
            for song in songs:
                if db.contains(song):
                    db_song = db.load(song)
                    if song["success-score"] > db_song["success-score"]:
                        # Update the DB version of the song, rather than
                        # overwriting it. Prevents loss of attributes such
                        # as lyrics that are added at a later point.
                        db_song["success-score"] = song["success-score"]
                        db.write(db_song)
                else:
                    db.write(song)
        except Exception as e:
            print("Couldn't download chart for date {}, exception: {}".format(d, e))
            continue
        with open(DATES_PROCESSED_PATH, "r") as f:
            processed = json.load(f)
        processed.append(d)
        with open(DATES_PROCESSED_PATH, "w") as f:
            json.dump(processed, f)

if __name__ == "__main__":
    main()
