import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import csv
import time

# ---------------- CONFIGURACIÓN ----------------
BASE_URL = "https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CSV_FILE = "movies.csv"

# ---------------- SCRAPING ----------------
def obtener_urls_lista():
    r = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    anchors = soup.select("a.article_movie_title")
    return [a['href'] for a in anchors[:300]]  # Hasta 300 películas

def extraer_dato(soup, etiqueta):
    for li in soup.select("li.meta-row"):
        if etiqueta in li.text:
            return li.text.split(":", 1)[1].strip()
    return "N/A"

def parsear_pelicula(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    data = {
        "title": soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else "N/A",
        "synopsis": soup.select_one("div.movie_synopsis").get_text(strip=True) if soup.select_one("div.movie_synopsis") else "N/A",
        "director": extraer_dato(soup, "Director"),
        "genre": extraer_dato(soup, "Genre"),
        "original_language": extraer_dato(soup, "Original Language"),
        "release_date": extraer_dato(soup, "Release Date"),
        "box_office": extraer_dato(soup, "Box Office (Gross USA)"),
        "runtime": extraer_dato(soup, "Runtime")
    }
    return data

def ejecutar_scraping():
    urls = obtener_urls_lista()
    with open(CSV_FILE, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "title", "synopsis", "director", "genre", "original_language",
            "release_date", "box_office", "runtime"
        ])
        writer.writeheader()
        for i, url in enumerate(urls, 1):
            try:
                st.info(f"[{i}/{len(urls)}] Scraping {url}")
                data = parsear_pelicula(url)
                writer.writerow(data)
                time.sleep(2)
            except Exception as e:
                st.error(f"Error en {url}: {e}")

# ---------------- STREAMLIT ----------------
st.title("🎬 Web Scraper de Películas - Rotten Tomatoes")

if not os.path.exists(CSV_FILE):
    if st.button("Iniciar Scraping"):
        st.warning("Obteniendo datos... esto puede tardar unos minutos.")
        ejecutar_scraping()
        st.success("¡Scraping completado!")

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.subheader("Vista general de películas")
    st.dataframe(df)

    st.subheader("Películas por idioma original")
    idioma_count = df["original_language"].value_counts()
    st.bar_chart(idioma_count)

    st.subheader("Duración promedio por género (si disponible)")
    df['runtime_num'] = df['runtime'].str.extract(r'(\d+)').astype(float)
    st.bar_chart(df.groupby("genre")["runtime_num"].mean().dropna())
