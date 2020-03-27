from scraping import GenericLyricsScraper
from storage import LyricsDatabase
import progressbar

def main():
    db = LyricsDatabase("./lyrics/charts/")
    s = GenericLyricsScraper()
    songs = [song for song in db]
    for song in songs:
        name = song["name"]
        artist = song["artist"]
        description = "'{}' by {}".format(name, artist)
        if "lyrics" in song:
            print("Already have lyrics for {}".format(description))
            continue
        if "attempted-fetches" not in song:
            song["attempted-fetches"] = []
        if "generic" in song["attempted-fetches"]:
            print("Already tried to fetch lyrics generically for {}".format(description))
            continue
        try:
            song["lyrics"] = s.scrape_lyrics(artist, name)
            print("Got lyrics for {}".format(description))
        except Exception as e:
            print("Failed to fetch lyrics for {}".format(description))
        song["attempted-fetches"].append("generic")
        db.write(song)

if __name__ == "__main__":
    main()
