from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from openpyxl import Workbook
import time

# Nastavení prohlížeče
options = Options()
#options.add_argument("--headless")  # Skryté okno (nepovinné)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL hlavní tabulky
base_url = "https://katalog.bcb.cz"
main_url = f"{base_url}/Katalog/Farnosti"

# Načti hlavní stránku
driver.get(main_url)
time.sleep(2)

rows = driver.find_elements(By.CSS_SELECTOR, "table.format.w100 tr.trbg[class*='kat_tr_']")

farnosti = []

for i in range(len(rows)):
    try:
        # Pracuj s čerstvým seznamem řádků, kvůli 'stale element' chybě
        row = rows[i]
        strong_tags = row.find_elements(By.TAG_NAME, "strong")
        if not strong_tags:
            continue
        nazev_farnosti = strong_tags[0].text.strip()
        
        odkaz = row.find_element(By.TAG_NAME, "a").get_attribute("href")
        if odkaz.startswith("/"):
            odkaz = base_url + odkaz

        driver.get(odkaz)
        time.sleep(1)

        emaily = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'mailto:')]")
        email_list = [e.text.strip() for e in emaily]

        farnosti.append((nazev_farnosti, email_list))

        # Zpět na hlavní stránku a načti znovu všechny řádky
        driver.get(main_url)
        time.sleep(1)
        rows = driver.find_elements(By.CSS_SELECTOR, "table.format.w100 tr.trbg[class*='kat_tr_']")

    except Exception as e:
        print(f"Chyba u řádku: {e}")
        continue

# Zavři prohlížeč
driver.quit()

# Ulož do Excelu
wb = Workbook()
ws = wb.active
ws.title = "Farnosti budějovice"
ws.append(["Název farnosti", "E-mail 1", "E-mail 2", "E-mail 3", "E-mail 4"])

for nazev, email_list in farnosti:
    ws.append([nazev, *email_list])  # Každý mail do samostatné buňky

wb.save("farnosti_budejovice.xlsx")
print("Hotovo!")