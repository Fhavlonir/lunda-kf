import pandas as pd
import itertools
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("summary.csv", na_values="Avstår")

pairings = pd.DataFrame(columns=df.columns[1:], index=df.columns[1:])

for p in itertools.permutations(df.columns[1:], 2):
    votes = df[list(p)].dropna()
    agreement = 100 * sum(votes[p[0]] == votes[p[1]]) / len(votes)
    pairings.loc[p[0], p[1]] = agreement

pairings.fillna(100, inplace=True)

ordning: list[str] = list(
    pd.Series(pairings["M"] - pairings["L"]).dropna().sort_values().index
)

pairings.loc[ordning, ordning].to_csv("lundapolitik-tabell.csv")
ax = sns.heatmap(
    pairings.loc[ordning, ordning],
    annot=True,
    fmt=".1f",
    cbar=False,
    cmap="viridis",
)
plt.tight_layout()
plt.savefig("agreement.svg", transparent=True)
