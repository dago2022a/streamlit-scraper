# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %%
import requests
from bs4 import BeautifulSoup
import time
import csv

BASE = "https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/"
HEADERS = {"User-Agent": "TuProyectoBot/1.0"}

def obtener_urls_lista():
    r = requests.get(BASE, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    # Ajusta el selector a la estructura real
    anchors = soup.select("a.article_movie_title")
    return [a['href'] for a in anchors[:300]]

def parsear_pelicula(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    data = {}
    data['title'] = soup.select_one("h1").get_text(strip=True)
    data['director'] = soup.select_one("li:contains('Director')").get_text().split(':',1)[1].strip()
    data['synopsis'] = soup.select_one("div.movie_synopsis").get_text(strip=True)
    # Agregar otros campos según el DOM
    return data

def main():
    urls = obtener_urls_lista()
    with open("movies.csv", "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['title','director','synopsis'])
        writer.writeheader()
        for i, url in enumerate(urls,1):
            print(f"[{i}/{len(urls)}] Scraping {url}")
            try:
                data = parsear_pelicula(url)
                writer.writerow(data)
            except Exception as e:
                print("Error:", e)
            time.sleep(2)  # para respetar el sitio


# %%
