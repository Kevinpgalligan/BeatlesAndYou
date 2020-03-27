import matplotlib.pyplot as plt

word_to_pctg = {
    "you": 88.0,
    "i": 92.6,
    "love": 61.7,
    "road": 2.3,
    "mustard": 0.02,
    "guitar": 1.3,
    "beatle": 0.2,
    "life": 15.2,
    "day": 27.0,
    "friend": 8.2
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
plt.title("Word frequency in chart song lyrics")

plt.show()
