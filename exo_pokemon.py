import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil

headers = {"User-Agent": "Mozilla/5.0"}
base_url = "https://pokemondb.net"

url_list = base_url + "/pokedex/national"

page = requests.get(url_list, headers=headers).content
soup = BeautifulSoup(page, "lxml")

name_links = soup.find_all("a", class_="ent-name")

pokemon_links = [base_url + a.get("href") for a in name_links]

print("Nombre de Pokémon trouvés :", len(pokemon_links))

def get_pokemon_data(url):
    page = requests.get(url, headers=headers).content
    soup = BeautifulSoup(page, "lxml")

    data = {"url": url}

    # =====================
    # Nom
    # =====================
    name = soup.find("h1").text.strip()
    data["name"] = name

    # =====================
    # Image (artwork officiel)
    # =====================
    img = soup.find("img", {"alt": lambda x: x and "artwork" in x.lower()})
    if img:
        img_url = img.get("src")
        data["image_url"] = img_url

        # Téléchargement de l’image
        img_stream = requests.get(img_url, stream=True)
        img_path = f"images/{name}.jpg"
        with open(img_path, "wb") as f:
            shutil.copyfileobj(img_stream.raw, f)

        data["image_path"] = img_path
    else:
        data["image_url"] = None
        data["image_path"] = None

    # =====================
    # Extraction des tableaux
    # =====================
    tables = soup.find_all("table", class_="vitals-table")

    # 1) Pokédex data
    for row in tables[0].find_all("tr"):
        key = row.find("th").text.strip()
        value = row.find("td").text.strip()
        data[f"pokedex_{key}"] = value

    # 2) Training
    for row in tables[1].find_all("tr"):
        key = row.find("th").text.strip()
        value = row.find("td").text.strip()
        data[f"training_{key}"] = value

    # 3) Breeding
    for row in tables[2].find_all("tr"):
        key = row.find("th").text.strip()
        value = row.find("td").text.strip()
        data[f"breeding_{key}"] = value

    # 4) Base stats
    for row in tables[3].find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            key = th.text.strip()
            try:
                value = int(td.text.strip())
            except:
                value = td.text.strip()

            data[f"base_{key}"] = value

    return data

all_pokemons = []

for i, link in enumerate(pokemon_links):
    print(f"Scraping {i+1}/{len(pokemon_links)} : {link}")
    info = get_pokemon_data(link)
    all_pokemons.append(info)

df = pd.DataFrame(all_pokemons)

df.to_csv("pokemons_complete.csv", index=False)

print("\n=== SCRAPING TERMINÉ ===")
print(df.head())
