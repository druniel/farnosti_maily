import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import time

BASE_URL = "https://dcza.sk"
MAIN_URL = f"{BASE_URL}/sk/schematizmus/farnosti"
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

main_response = fetch_with_retry(MAIN_URL)
if not main_response:
    print("Nepodařilo se načíst hlavní stránku. Konec.")
    exit(1)

soup = BeautifulSoup(main_response.text, "html.parser")

# Najdi h1 s textem "Farnosti"
h1_tag = soup.find("h1", string="Farnosti")
if not h1_tag:
    print("Nadpis 'Farnosti' nenalezen.")
    exit(1)

# Najdi první <ul> následující po <h1>
ul_tag = h1_tag.find_next_sibling("ul")
if not ul_tag:
    print("Seznam <ul> farností nebyl nalezen.")
    exit(1)

# Vyber všechny <li>, přeskoč první dvě
farnosti_links = ul_tag.find_all("a")[2:]

farnosti_data = []

for a in farnosti_links:
    nazev_farnosti = a.text.strip()
    detail_url = BASE_URL + a["href"]

    detail_response = fetch_with_retry(detail_url)
    if not detail_response:
        print(f"Nepodařilo se načíst detail farnosti: {detail_url}")
        continue

    detail_soup = BeautifulSoup(detail_response.text, "html.parser")
    email_tag = detail_soup.select_one("a[href^='mailto:']")
    email = email_tag.text.strip() if email_tag else ""

    farnosti_data.append((nazev_farnosti, email))
    print(f"Načteno: {nazev_farnosti} - {email}")
    time.sleep(0.5)

# Uložení do Excelu
wb = Workbook()
ws = wb.active
ws.title = "Farnosti žilinská diecéze"
ws.append(["Název farnosti", "E-mail"])

for nazev, email in farnosti_data:
    ws.append([nazev, email])

wb.save("farnosti_zilinska_dieceze.xlsx")
print("Hotovo! Uloženo jako 'farnosti_zilinska_dieceze.xlsx'")