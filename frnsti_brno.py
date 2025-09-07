import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

base_url = "https://katalog.biskupstvi.cz/farnosti"
page = 1
farnosti_data = []

while True:
    print(f"Zpracovávám stránku {page}...")
    url = f"{base_url}?page={page}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Konec stránek nebo chyba (HTTP {response.status_code}).")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("li.list-group-item.boh-pol")

    if not rows:
        print("Žádná další data. Konec.")
        break

    for row in rows:
        # Název farnosti
        farnost_nazev_tag = row.select_one("span.seznam-podnazev")
        farnost_nazev = farnost_nazev_tag.text.strip() if farnost_nazev_tag else ""
        email_tag = row.select_one("a[href^='mailto:']")
        email = email_tag.text.strip() if email_tag else ""

        farnosti_data.append((farnost_nazev, email))

    page += 1

wb = Workbook()
ws = wb.active
ws.title = "Farnosti"
ws.append(["Název farnosti", "E-mail"])

for farnost, email in farnosti_data:
    ws.append([farnost, email])

wb.save("farnosti_kontakty_brno.xlsx")
print("Hotovo! Data uložena do 'farnosti_kontakty_brno.xlsx'")