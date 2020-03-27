from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from storage import LyricsDatabase
import sys

WORD_FORMS = {
    "you": ["you", "your", "yours", "yourself"],
    "i": ["i", "me", "mine", "myself"],
    "love": ["love"],
    "road": ["road"],
    "mustard": ["mustard"],
    "guitar": ["guitar"],
    "beatle": ["beatle"],
    "life": ["life"],
    "day": ["day"],
    "friend": ["friend"]
}
WORDS = [word for word in WORD_FORMS]
STEMMER = PorterStemmer()

def lowercase_stems(s):
    return [STEMMER.stem(token).lower() for token in word_tokenize(s)]

def you_in_first_line(lyrics):
    return any(STEMMER.stem(word) in lowercase_stems(lyrics.strip("\n").split("\n")[0])
               for word in WORD_FORMS["you"])

def update_word_counts(word_counts, lyrics):
    stems = lowercase_stems(lyrics)
    for word in word_counts:
        if any(STEMMER.stem(form) in stems for form in WORD_FORMS[word]):
            word_counts[word] += 1

def main():
    if len(sys.argv) < 2:
        print("missing program arg.")
        sys.exit(1)
    if sys.argv[1] == "beatles":
        songs = [song for song in LyricsDatabase("./lyrics/beatles/") if "lyrics" in song]
    elif sys.argv[1] == "charts":
        songs = [song for song in LyricsDatabase("./lyrics/charts/") if "lyrics" in song]
        # Remove Beatles songs...
        songs = [song for song in songs if "beatles" not in song["artist"].lower()]
    else:
        print("invalid program arg.")
        sys.exit(1)

    first_line_yous = 0
    word_counts = {word: 0 for word in WORDS}
    for song in songs:
        lyrics = song["lyrics"]
        if you_in_first_line(lyrics):
            first_line_yous += 1
        update_word_counts(word_counts, lyrics)

    print(f"songs processed: {len(songs)}")
    print(f"percentage with 'you' in first line: {first_line_yous/len(songs)*100.}%")
    for word, count in word_counts.items():
        print("percentage with '{}' somewhere in the song: {}%".format(word, count/len(songs)*100.))

if __name__ == "__main__":
    main()
