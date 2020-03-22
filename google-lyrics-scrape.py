"""Attempt to scrape lyrics from Google search.
Note: the scraping code is likely to be very fragile.
A slight change in the HTML generation on Google's side
will break it. It works as of March 21st 2020, anyway."""

from scraping import GoogleLyricsScraper
from storage import LyricsDatabase
import progressbar

def main():
    db = LyricsDatabase("./lyrics/charts/")
    s = GoogleLyricsScraper()
    songs = [song for song in db]
    for song in progressbar.progressbar(songs):
        name = song["name"]
        artist = song["artist"]
        description = "'{}' by {}".format(name, artist)
        if "lyrics" in song:
            print("Already have lyrics for {}".format(description))
            continue
        if "attempted-fetches" not in song:
            song["attempted-fetches"] = []
        if "google" in song["attempted-fetches"]:
            print("Already tried to fetch lyrics from Google for {}".format(description))
            continue
        try:
            song["lyrics"] = s.scrape_lyrics(artist, name)
            print("Got lyrics for {}".format(description))
        except Exception as e:
            print("Failed to fetch lyrics from Google for {}".format(description))
        song["attempted-fetches"].append("google")
        db.write(song)

if __name__ == "__main__":
    main()
