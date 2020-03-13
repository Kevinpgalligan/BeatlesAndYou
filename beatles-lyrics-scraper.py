from bs4 import BeautifulSoup
import progressbar
import re
import sys
from scraping import AzLyricsScraper, get_page
from storage import LyricsDatabase

# Core catalogue.
ALBUMS = [
    "Please Please Me",
    "With The Beatles",
    "A Hard Day's Night",
    "Beatles For Sale",
    "Help!",
    "Rubber Soul",
    "Revolver",
    "Sgt. Pepper's Lonely Hearts Club Band",
    "Magical Mystery Tour",
    "The Beatles (The White Album)",
    "Yellow Submarine",
    "Abbey Road",
    "Let It Be"
]

SONG_ID_REGEX = re.compile(r"/([a-zA-Z0-9-]+)\.html")

def main():
    beatles_songs_page = get_page("https://www.azlyrics.com/b/beatles.html")
    if beatles_songs_page is None:
        print("Failed to get list of songs.")
        sys.exit(1)
    soup = BeautifulSoup(beatles_songs_page.content, 'html.parser')
    album_headers = [header for header in soup.find_all("div", class_="album")
                     if any(album.lower() in header.text.lower() for album in ALBUMS)]
    if len(album_headers) != len(ALBUMS):
        print("Failed to find all album headers.")
        sys.exit(1)

    song_links = []
    for header in album_headers:
        for e in header.next_siblings:
            if isinstance(e, str):
                continue
            if e.name == "div" and "listalbum-item" in e["class"]:
                ref = e.find("a").get("href")
                if "lyrics/beatles" in ref:
                    song_links.append(ref.replace("..", "https://www.azlyrics.com"))
            if e.name == "div" and "album" in e["class"]:
                # Have hit the next album, stop.
                break
    print(f"Num songs: {len(song_links)}")

    db = LyricsDatabase("./lyrics/beatles/")
    scraper = AzLyricsScraper()

    for song_link in progressbar.progressbar(song_links):
        song_id_match = SONG_ID_REGEX.search(song_link)
        if song_id_match is None:
            print("Failed to find ID of a song from its link:", song_link)
            sys.exit(1)
        song_data = {
            "id": song_id_match.group(1)
        }
        if db.contains(song_data):
            continue # already downloaded
        song_data["lyrics"] = scraper.scrape_lyrics(song_link)
        db.write(song_data)

if __name__ == "__main__":
    main()
