import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

URL = "https://www.biskupstvo-nitra.sk/?page_id=78"

response = requests.get(URL)
if response.status_code != 200:
    raise SystemExit(f"Chyba při načítání stránky: HTTP {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

farnosti_data = []

table = soup.find("table")
if not table:
    raise SystemExit("Tabulka s farnostmi nebyla nalezena.")

for row in table.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) >= 3:
        nazev = cols[0].get_text(strip=True)
        email = cols[2].get_text(strip=True)
        farnosti_data.append((nazev, email))

# Uložení do Excelu
wb = Workbook()
ws = wb.active
ws.title = "Farnosti"
ws.append(["Název farnosti", "E-mail"])

for nazev, email in farnosti_data:
    ws.append([nazev, email])

wb.save("farnosti_nrb.xlsx")
ws.append(["Název farnosti", "E-mail"])

for nazev, email in farnosti_data:
    ws.append([nazev, email])

wb.save("farnosti_nitra.xlsx")
print("Hotovo!")