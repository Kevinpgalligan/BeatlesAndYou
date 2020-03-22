import requests
from ratelimit import limits, sleep_and_retry
from bs4 import BeautifulSoup
from retry import retry
import urllib.parse
        
REQUEST_WAIT_SECONDS = 10

@retry(requests.exceptions.RequestException, tries=3) # robustness
def get_page(link):
    """Get HTML page at given link.
    Raises PageDoesNotExistError if it doesn't exist.
    Raises generic Exception if unexpected HTTP codes are encountered."""
    response = requests.get(link)
    if response.status_code == 200:
        return response
    if response.status_code == 404:
        raise PageDoesNotExistError("{} does not exist".format(link))
    raise Exception(f"Failed to get page {link}, got HTTP status code {response.status_code}.")

class AzLyricsScraper:

    # Rate-limiting to prevent blacklisting by. 10 seconds is probably overly
    # conservative, but for ~400 songs it still took only ~1 hour to download all of the
    # lyrics.
    @sleep_and_retry
    @limits(calls=1, period=REQUEST_WAIT_SECONDS)
    def scrape_lyrics(self, song_link):
        """Get lyrics from azlyrics.com at the given link.

        Raises PageDoesNotExist exception if the page doesn't exist.
        """
        lyrics_page = get_page(song_link)
        soup = BeautifulSoup(lyrics_page.content, 'html.parser')
        lyrics_div = soup.find("div", class_="ringtone").find_next_sibling("div")
        return lyrics_div.text.strip()

class GoogleLyricsScraper:
    @sleep_and_retry
    @limits(calls=1, period=REQUEST_WAIT_SECONDS)
    def scrape_lyrics(self, artist, name):
        pg = get_page("https://www.google.com/search?q="
            + urllib.parse.quote(" ".join((artist, name, "lyrics"))))
        soup = BeautifulSoup(pg.content, 'html.parser')
        lyric_blocks = []
        is_first = True
        for e in soup.select("div.BNeawe.tAd8D.AP7Wnd"):
            # Lyrics appear to be nested in 2 layers of divs with
            # these class tags. And they're repeated, for some reason.
            for lyric_e in e.select("div.BNeawe.tAd8D.AP7Wnd"):
                if is_first:
                    is_first = False
                else:
                    lyric_blocks.append(lyric_e.get_text())
        if not lyric_blocks:
            raise LyricsNotFoundError("Couldn't find lyrics for song {}, by {}".format(name, artist))
        return "\n".join(lyric_blocks)

class LyricsNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class PageDoesNotExistError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
