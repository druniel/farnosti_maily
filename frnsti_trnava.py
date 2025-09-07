import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

URL = "https://www.abu.sk/schematizmy/schematizmus-trnavskej-arcidiecezy-podla-nazvu-farnosti"

response = requests.get(URL)
if response.status_code != 200:
    raise SystemExit(f"Chyba při načítání stránky: HTTP {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

farnosti_data = []

# Najdi všechny kontaktní bloky
for item in soup.select("div.contacts-item"):
    # 1) Název farnosti je v <h4>
    h4 = item.find("h4")
    if not h4:
        continue
    nazev = h4.get_text(separator=" ").strip()
    
    # 2) E-mail najdeme v <address> obsahujícím "e‑mail:"
    email = ""
    for addr in item.find_all("address"):
        txt = addr.get_text()
        if "e‑mail:" in txt or "e-mail:" in txt:
            # třeba formát farnost.baka(at)abu.sk
            email = txt.split(":", 1)[1].strip()
            email = email.replace("(at)", "@").strip()
            break
    
    farnosti_data.append((nazev, email))

# Uložení do Excelu
wb = Workbook()
ws = wb.active
ws.title = "Trnavská arcidiecéza"
ws.append(["Název farnosti", "E-mail"])

for nazev, email in farnosti_data:
    ws.append([nazev, email])

wb.save("farnosti_trnava.xlsx")
print("Hotovo! Výstup uložen jako 'farnosti_trnava.xlsx'")