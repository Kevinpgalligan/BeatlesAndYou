import matplotlib.pyplot as plt

word_to_pctg = {
    "you": 81.9,
    "i": 86.2,
    "love": 44.2,
    "road": 5.1,
    "mustard": 0.7,
    "guitar": 0.7,
    "beatle": 0.0,
    "life": 7.2,
    "day": 23.9,
    "friend": 8.7
}
word_pctg_pairs = sorted(word_to_pctg.items(), key=lambda pair: pair[1])
words = [word for word, _ in word_pctg_pairs]
pctgs = [pctg for _, pctg in word_pctg_pairs]
positions = list(range(len(words)))

fig, ax = plt.subplots()
ax.barh(positions, pctgs, align="center", alpha=0.5)
ax.set_yticks(positions)
ax.set_yticklabels(words)
for i, pctg in enumerate(pctgs):
    ax.text(0.5 + pctg, i, str(pctg) + "%", va="center", color="black")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
plt.xlabel("% of songs")
plt.title("Word frequency in Lennon-McCartney lyrics")

plt.show()
