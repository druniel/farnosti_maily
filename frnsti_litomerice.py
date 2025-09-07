import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

base_url = "https://katalog.dltm.cz/web/farnosti"
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
    rows = soup.select("div.box-inner.InstitutionParish")

    if not rows:
        print("Žádná další data. Konec.")
        break

    for row in rows:
        # Název farnosti
        farnost_nazev_tag = row.select_one("a > span.title-span > span")
        farnost_nazev = farnost_nazev_tag.get_text(strip=True) if farnost_nazev_tag else ""
        email_tags = row.select("a[href^='mailto:']")
        emaily = ", ".join(tag.get_text(strip=True) for tag in email_tags)

        farnosti_data.append((farnost_nazev, emaily))

    page += 1

wb = Workbook()
ws = wb.active
ws.title = "Farnosti litoměřické arcidiecéze"
ws.append(["Název farnosti", "E-mail"])

for farnost, email in farnosti_data:
    ws.append([farnost, email])

wb.save("farnosti_kontakty_litomerice.xlsx")
print("Hotovo!")