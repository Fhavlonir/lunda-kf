import re
import os
import pandas as pd
from PyPDF2 import PdfReader

for filename in os.listdir("protokoll"):
    reader = PdfReader("protokoll/" + filename)

    alltext = ""

    for p in reader.pages:
        t = (
            p.extract_text()
            .replace("\n", " ")
            .replace("a å ", "å")
            .replace("a ä ", "ä")
            .replace("a ö ", "ä")
            .replace("o ö ", "ö")
            .replace("A Å ", "Å")
            .replace("A Ä ", "Ä")
            .replace("A Ö ", "Ä")
            .replace("O Ö ", "Ö")
            .replace("aå", "å")
            .replace("aä", "ä")
            .replace("aö", "ä")
            .replace("oö", "ö")
            .replace("AÅ", "Å")
            .replace("AÄ", "Ä")
            .replace("AÖ", "Ä")
            .replace("OÖ", "Ö")
        )
        alltext += t

    # print(alltext)
    alltext = re.compile(
        r"\d+\s+(?:\s*(?:[\w-]+\s+){1,4}\(\w+\)\s*){1,2}\s+\w+\s*\w*\s+(?:Ja|Nej|Avstår) "
    ).findall(alltext, re.MULTILINE)

    pattern = re.compile(
        r"^(\d+)\s+([\w\s-]+)\s+\(([A-Z]+)\)\s+(?:[\w\s-]+\(\w+\))?\s+(\w+\s*\w*)\s+(Ja|Nej|Avstår)"
    )
    data = []
    for line in alltext:
        # print(line)
        match = pattern.match(str(line))
        if match:
            nr, namn, parti_kort, parti_lang, rost = match.groups()
            data.append(
                {"stol": int(nr), "namn": namn, "parti": parti_kort, "röst": rost}
            )

    df = pd.DataFrame(data)
    df.to_csv(str("data/" + filename[:-4] + ".csv"), index=False)
    print(df)
