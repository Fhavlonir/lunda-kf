# Lundapolitikens block

![](agreement.svg)

Denna kod är avsedd att köras på Unix-iga operativsystem (Linux, MacOS). Jag har ingen aning om huruvida den fungerar på t.ex. Windows.

1. Installera Python, samt paketen `pandas`, `seaborn`, och `pypdf2`.
2. `mkdir protokoll`, stoppa in de protokoll du är intresserad av att analysera.
3. `mkdir data`
4. `python extract_protocols.py`
5. Kontrollera innehållet i `/data`, det borde stämma överens med protkollen.
6. `python summarize.py`
7. `python who-agrees.py`
