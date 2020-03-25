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

class GeniusScraper:
    def scrape(self, link):
        pg = get_page(link)
        soup = BeautifulSoup(pg.content, 'html.parser')
        for div in soup.select("div.lyrics"):
            return div.get_text()

class Top40dbScraper:
    def scrape(self, link):
        pg = get_page(link)
        soup = BeautifulSoup(pg.content, 'html.parser')
        for e in soup.find_all(["small", "script"]):
            e.decompose() # remove the log-in message and ad shit
        for div in soup.select("div#divTOP40DB_LYRICS"):
            return div.get_text()

class LyricsFreakScraper:
    def scrape(self, link):
        pg = get_page(link)
        soup = BeautifulSoup(pg.content, 'html.parser')
        for div in soup.select("div#content"):
            return div.get_text()

class GenericLyricsScraper:
    def __init__(self):
        """Unlike the Google scraper, doesn't scrape directly from
        the lyrics displayed by Google. Looks through search results
        and matches them with the appropriate scraper. Eg if there's
        a link for genius.com, passes that to the genius.com scraper."""
        self._scrapers = [
            ("genius.com", GeniusScraper()),
            ("top40db.net", Top40dbScraper()),
            ("lyricsfreak.com", LyricsFreakScraper())
        ]

    @sleep_and_retry
    @limits(calls=1, period=REQUEST_WAIT_SECONDS)
    def scrape_lyrics(self, artist, name):
        pg = get_page("https://www.google.com/search?q="
            + urllib.parse.quote(" ".join((artist, name, "lyrics"))))
        soup = BeautifulSoup(pg.content, 'html.parser')
        for element in soup.select("a"):
            print("========TRYING LINK=========")
            link = element.get("href")
            try:
                print("Processing link:", link)
                # The parent div should contain the title of the page -- which, for
                # all of the sites we're using, should in turn contain the name of
                # the song.
                if not fuzzy_matches(name, element.parent.get_text()):
                    # skip this link to ensure that we're not just getting the lyrics of
                    # a random song by the same artist. Don't bother to check that the
                    # artist is the same; in all likelihood, if the artist is
                    # different, it's a different version of the same song.
                    print("song name does not match:", element.parent.get_text())
                    continue
                for site_name, scraper in self._scrapers:
                    if site_name in link:
                        print("Matches with scraper for", site_name)
                        if link.startswith("/"):
                            link = "https://www.google.com" + link
                        print("Trying to scrape from link", link)
                        return scraper.scrape(link)
            except Exception as e:
                continue # try the next link
        raise LyricsNotFoundError("Could not scrape lyrics from any website in first page of results.")

def fuzzy_matches(important_s, s):
    important_tokens = set([token.lower() for token in important_s.strip().split()])
    tokens = set([token.lower() for token in s.strip().split()])
    # threshold chosen arbitrarily, pretty much
    return len(important_tokens.intersection(tokens)) / len(important_tokens) >= 0.49

class LyricsNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class PageDoesNotExistError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
