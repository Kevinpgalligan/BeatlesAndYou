import re
import progressbar
from storage import LyricsDatabase
from scraping import AzLyricsScraper, PageDoesNotExistError

INVALID_CHARS_REGEX = "[^A-Za-z0-9]"

def main():
    db = LyricsDatabase("./lyrics/charts/")
    scraper = AzLyricsScraper()

    songs = [song for song in db]
    for song in progressbar.progressbar(songs):
        if "attempted-lyrics" in song:
            # already tried to get lyrics for this one, skip.
            continue
        # this is just a guess.
        song_link = to_az_lyrics_link(song["name"], song["artist"])
        try:
            song["lyrics"] = scraper.scrape_lyrics(song_link)
            print("Got lyrics from {}".format(song_link))
        except Exception as e:
            print("Failed to fetch lyrics, because: {}".format(e))
        song["attempted-lyrics"] = True
        db.write(song)

def to_az_lyrics_link(name, artist):
    return "https://www.azlyrics.com/lyrics/{}/{}.html".format(
        re.sub(INVALID_CHARS_REGEX, "", artist.lstrip("The ")).lower(),
        re.sub(INVALID_CHARS_REGEX, "", name).lower())

if __name__ == "__main__":
    main()
