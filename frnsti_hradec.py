import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import time
import string

BASE_URL = "https://www.bihk.cz"
MAX_RETRIES = 3
RETRY_DELAY = 2

def fetch_with_retry(url, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response
            else:
                print(f"[{attempt+1}] Chyba {response.status_code} při načítání {url}")
        except Exception as e:
            print(f"[{attempt+1}] Výjimka při načítání {url}: {e}")
        time.sleep(delay)
    return None

farnosti_data = []

# Prochází všechna písmena A–Z
for letter in string.ascii_uppercase:
    print(f"Zpracovávám písmeno: {letter}")
    list_url = f"{BASE_URL}/dieceze/diecezni-katalog/farnosti-filter/{letter}"
    list_response = fetch_with_retry(list_url)

    if not list_response:
        print(f"Písmeno {letter} přeskočeno (chyba při načítání).")
        continue

    list_soup = BeautifulSoup(list_response.text, "html.parser")
    farnost_links = list_soup.select("div.result-items li a")

    for a_tag in farnost_links:
        nazev_farnosti = a_tag.text.strip()
        detail_url = BASE_URL + a_tag["href"]

        detail_response = fetch_with_retry(detail_url)
        if detail_response:
            detail_soup = BeautifulSoup(detail_response.text, "html.parser")

            # Získání názvu farnosti (z nadpisu detailu)
            nazev_tag = detail_soup.select_one("div.region-page-title h1")
            nazev = nazev_tag.get_text(strip=True) if nazev_tag else nazev_farnosti

            # Najde všechny e-maily
            email_tags = detail_soup.select("a[href^='mailto:']")
            emails = [tag.get_text(strip=True) for tag in email_tags]
            emaily_spojene = ", ".join(emails)
        else:
            nazev = nazev_farnosti
            emaily_spojene = ""
            print(f"Nepodařilo se načíst detail farnosti: {detail_url}")

        farnosti_data.append((nazev, emaily_spojene))
        time.sleep(0.5)

# Uložení do Excelu
wb = Workbook()
ws = wb.active
ws.title = "Farnosti Hradec"
ws.append(["Název farnosti", "E-mail(y)"])

for farnost, email in farnosti_data:
    ws.append([farnost, email])

wb.save("farnosti_kontakty_hradec.xlsx")
print("Hotovo!")