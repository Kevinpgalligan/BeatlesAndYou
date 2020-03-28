### Description
Write-up: [https://kevingal.com/blog/beatles-and-you.html](https://kevingal.com/blog/beatles-and-you.html).

Here you'll find:

* Scraping code for the Billboard music charts and various lyrics websites (requests + BeautifulSoup4).
* A sort of database for song lyrics that keeps each song as a JSON file (see `storage.py`).
* A GUI for manually entering song lyrics / viewing the songs in the database (PySimpleGUI).
* And various snippets of code for doing text analysis / data visualisation based on the lyrics (nltk + matplotlib).

I haven't bothered to clean it up, but you might find something useful.

### Setup
Requires python3. The dependencies are contained in `requirements.txt`, and you can install them like so:

```
pip3 install requirements.txt
```

### Overview of files
* `beatles_lyrics_scraper.py`: scrapes a list of Beatles songs from azlyrics.com and downloads the lyrics.
* `chart_lyrics_scrape.py`: an early attempt to scrape lyrics for Billboard Hot 100 songs using an AzLyrics scraper. Not sure if this script even works anymore.
* `chart_scrape.py`: scrape the weekly Billboard Hot 100 charts.
* `cleaning.ipynb`: remove Beatles songs / instrumental songs / etc from the Hot 100 dataset.
* `dbgui.py`: PySimpleGUI-based GUI for displaying the songs in the dataset + whether their lyrics have been downloaded, allows manual entry of lyrics.
* `general_lyrics_scrape.py`: for all songs that don't have lyrics in the charts dataset, do a Google search for those lyrics and try to scrape them from any recognised site (lyricsfreak.com, top40db.net, genius.com, azlyrics.com).
* `google_lyrics_scrape.py`: for all songs that don't have lyrics in the charts dataset, try to scrape the lyrics from Google's lyrics widget, which is basically a proxy to LyricFind (?) and MusixMatch.
* `lyrics/`: folder containing the Beatles and Hot 100 datasets, zipped.
* `lyrics_analysis.py`: what it says on the tin.
* `scraping.py`: shared scraping code.
* `storage.py`: interface for accessing the datasets, each song stored as a separate JSON file.
* `visualisation.ipynb`: visualisation of chart songs in a Jupyter notebook.
* `wordsplot.py`: bar plots of word frequency.
