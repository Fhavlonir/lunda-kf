import re
import os
import pandas as pd

dataframes = []
for filename in os.listdir("data"):
    try:
        new_df = pd.read_csv("data/" + filename)
        ses = re.compile(r"\d\d\d\d-\d\d-\d\d").search(filename)
        if ses:
            new_df["session"] = ses.group()
        else:
            new_df["session"] = ""
        new_df["vote"] = (new_df["stol"] == 1).cumsum()
        new_df["omröstning"] = new_df["session"] + "_" + new_df["vote"].astype(str)
        # new_df = new_df[new_df["stol"] > 3]
        dataframes += [new_df]
    except:
        print(
            filename
            + " har inga kolumner! Inga omröstningar, eller så har något gått snett?"
        )

df = pd.concat(dataframes)

tabell = df.groupby(["parti", "omröstning"])["röst"].first()

tabell.unstack(level="parti").to_csv("summary.csv")
