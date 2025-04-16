# Vad gör koden?

![](https://imgs.xkcd.com/comics/regular_expressions.png)

Jag har redigerat koden lite grann, tagit bort import-rader och felhantering, som inte är del av den egenltiga lösningen.

Till att börja med låter vi PdfReader från PyPDF2 läsa in PDF-filerna och göra sitt bästa för att översätta till vanliga textrader.

```python extract_protocols.py
    alltext = ""

    for p in reader.pages:
        t = (
            p.extract_text()
            .replace("\n", " ")
            .replace("a å ", "å")
            .replace("a ä ", "ä")
            .replace("o ö ", "ö")
        )
        alltext += t
```

Eftersom PyPDF2-biblioteket inte egentligen är gjort för svensk text, gör den ibland lite konstiga misstag, så de rättade vi till manuellt. Sen lägger vi till alla pdf-sidor i en enda lång textsträng, eftersom tabeller inte sällan börjar på en sida och fortsätter på nästa. Dessutom ersätta vi radbryt med blanksteg, långa namn gör att en tabellrad delas upp på två textrader, och den lättaste lösningen på det är att helt enkelt låta hela texten vara på en och samma textrad.

```python extract_protocols.py
    rows = re.compile(
        r"\d{1,2}\s+(?:\s*(?:[\w-]+\s+){1,4}\(\w+\)\s*){1,2}\s+(?:\w+\s+)+(?:Ja|Nej|Avstår) "
    ).findall(alltext, re.MULTILINE)

    pattern = re.compile(
        r"^(\d{1,2})\s+([\w\s-]+)\s+\(([A-Z]+)\)\s+(?:[\w\s-]+\(\w+\))?\s+(\w+\s+)+(Ja|Nej|Avstår)"
    )
```

Här ovan har vi den läskigaste delen av hela programmet: De reguljära uttrycken. Kort sagt är de ett sätt att försöka känna igen mönster i text, för att först identifiera rader av en tabell, och sedan identifiera värdena per rad man fått fram. Att förklara allt om regex-formattering är långt utanför den här postens avsikt, men så intresserade läsare hänvisas till: [Wikipedia](https://sv.wikipedia.org/wiki/Regulj%C3%A4ra_uttryck), [högskolekurser, förslagsvis på LTH](https://kurser.lth.se/lot/course/EDAN65), och [regexr.com](https://regexr.com/) som automatiskt förklarar och testar regex-uttryck.

För att förklara just dessa i ord, så letar de efter teckensekvenser på formen:
- 1-2 siffror (stolsnummer)
- Ett eller fler mellanrum
- Någon kombination av bokstäver, mellanrum och bindestreck.
- Ett eller flera stora bokstäver inom parantes (partibeteckning)
- Eventuellt de två förra grejerna igen. Om en ersättare har hoppat in finns nämligen ordinarie namgiven precis efter.
- En kombination av bokstäver och mellanrum (partinamnet)
- Texten ("Ja", "Nej" eller "Avstår")

Den exakta formuleringen på dessa uttryck fick jag mer eller mindre testa mig fram till, till en början tyckte den till exempel att rader från innehållsförteckning, m.m. t.ex. "[§ ]66 Motion från Börje Hed (FNL) och Ja[n Annerstedt]" passade in på beskrivningen. Vilket de ju i och för sig gjorde, även om det inte var det jag hade tänkt.

```python extract_protocols.py
    data = []
    for row in rows:
        match = pattern.match(str(row))
        if match:
            nr, namn, parti_kort, parti_lang, rost = match.groups()
            data.append(
                {"stol": int(nr), "namn": namn, "parti": parti_kort, "röst": rost}
            )
    df = pd.DataFrame(data)
    df.to_csv(str("data/" + filename[:-4] + ".csv"), index=False)
    print(filename)
    print(df)
```
Till sist lägger skapar jag en tabell, ger namn åt kolumnerna (en kolumn med stolsnumret, en med ledamotens namn, två för partiet: både namnet och förkortningen, och till sist en kolumn med hur de röstade Ja/Nej/Avstår), det sparas sedan ut i en fil med samma filnamn som protokollet, fast i en annan sökväg, och med ändelsen ".csv" i stället för ".pdf"

De filerna tas sedan om hand av nästa skript:

```python extract_protocols.py
dataframes = []
for filename in os.listdir("data"):
   new_df = pd.read_csv("data/" + filename)
   ses = re.compile(r"\d\d\d\d-\d\d-\d\d").search(filename)
   new_df["session"] = ses.group()
   new_df["vote"] = (new_df["stol"] == 1).cumsum()
   new_df["omröstning"] = new_df["session"] + "_" + new_df["vote"].astype(str)
   dataframes += [new_df]

df = pd.concat(dataframes)

tabell = df.groupby(["parti", "omröstning"])["röst"].first()

tabell.unstack(level="parti").to_csv("summary.csv")
```
Denna betydligt kortare fil går igenom de nyskapade csv-filerna, tar datumet ur filnamnet, och tillsammans med en liten räknare av hur många gånger stol nummer 1 varit med i tabellen, kan den skapa en kolonn av typen datum-omröstning, t.ex. "2023-06-21_02" för den andra omröstningen på fullmäktigemötet den 21:a juni 2023. (Det var f.ö. en motion angående lokala ordningsföreskrifter avseende fyverkerier).

Sedan grupperas dessa efter omröstning och parti, så att varje grupp av rader motsvarar en omröstning, och varje parti representeras av den ledamot som är först, d.v.s. har lägst stolsnummer.

Varje radgrupp (alltså omröstning) slås sedan ihop till en rad vardera i en ny tabell, där med en kolumn per parti.

Vår tidigare nämnda exempelomröstning blir alltså:


|omröstning  |C |FNL|KD|L  |M |MP |S |SD|V  |
|------------|--|---|--|---|--|---|--|--|---|
|2023-06-21_2|Ja|Ja |Ja|Nej|Ja|Nej|Ja|Ja|Nej|

Men vänta lite, om man kollar upp den omröstningen i protokollet fanns det ju en del oenighet inom Liberalerna, det var ju framför allt KF:s 2:a vice ordförande Camilla Neptune som hade en stark åsikt, men Philip Sandberg, lundaliberalernas superstar #1 avstod omröstningen. Därför lägger vi också till en rad i koden som skippar de tre första namnen i listan, (d.v.s. fullmäktiges ordförande och de två vice). Då får vi istället listettornas röster. Alltså:

|omröstning  |C |FNL|KD|L     |M |MP |S |SD|V  |
|------------|--|---|--|------|--|---|--|--|---|
|2023-06-21_2|Ja|Ja |Ja|Avstår|Ja|Nej|Ja|Ja|Nej|

Detta exempel upprepas för samtliga omröstningar, och det samlas i ett kalkylark som heter "summary.csv".

Vid detta laget kan vi lika gärna kunna använda ett kalkylarksprogram, men jag är mer av en kod-person oavsett, så det sista lilla steget för att göra ett fint diagram:

```python who-agrees.py
pairings = pd.DataFrame(columns=df.columns[1:], index=df.columns[1:])

for p in itertools.permutations(df.columns[1:], 2):
    votes = df[list(p)].dropna()
    agreement = sum(votes[p[0]] == votes[p[1]]) / len(votes)
    pairings.loc[p[0], p[1]] = agreement * 100
```
Bortsett från lite input/output-krafs om bibliotek, filnamn, färgläggning och sånt är det detta jag gör för att framställa själva diagrammet. Skapa en tabell med partierna på x- och y-axeln, gå igenom de parvisa [permutationerna](https://www.youtube.com/watch?v=5sbc-sWiSO8) av partierna i listan, och för varje partipar:

- Skapa en tabellkopia med bara de två partiernas röster
- Stryk raderna där någon röstat "Avstår" (omdöpt till `na`-variabeln, "Not Available")
- Summera antalet rader där de två partierna röstat lika, delat på det totala antalet omröstningar.
- Omvandla till procent genom att gånga med hundra, och sedan lägg in på rätt plats i tabellen.
- Smaka av och njut!

Hoppas det var lärorikt, och om ni upptäcker något som ser dumt ut, får ni gärna låta mig veta!
