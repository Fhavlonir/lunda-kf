import pandas as pd
import itertools
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("summary.csv", na_values="Avstår")

pairings = pd.Series()
manual_name_list = ["M", "S", "KD", "V", "SD", "C", "L", "FNL", "MP"]
pairings2d = pd.DataFrame(columns=df.columns[1:], index=df.columns[1:])


for p in itertools.permutations(df.columns[1:], 2):
    votes = df[list(p)].dropna()
    plist = list(p)
    plist.sort()
    agreement = 100 * sum(votes[p[0]] == votes[p[1]]) / len(votes)
    pairings2d[p[0]][p[1]] = agreement
    pairings[plist[0] + "/" + plist[1]] = agreement

pairings.sort_values(inplace=True, ascending=False)
pairings.to_csv("pairings.csv")
print(pairings)
print(pairings2d)
ax = sns.heatmap(
    pairings2d.sort_values("M").T.sort_values("M").fillna(100), annot=True, fmt=".1f"
)
plt.savefig("agreement.svg")
