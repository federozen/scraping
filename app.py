# app.py

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Título de la Aplicación
st.title("📰 Scraper de Titulares de Noticias")

# Descripción
st.markdown("""
Esta aplicación permite scrapear titulares de diferentes fuentes de noticias deportivas. 
Selecciona las fuentes que deseas scrapear y obtén una tabla interactiva con los titulares.
""")

# Definir la función de scraping
def scrape_news(url, headline_selector, title_attribute="text", fallback_attribute="text", limit=15, club_names=None, start_index=0, num_to_fetch=None):
    """
    Scrapea titulares de noticias de una URL dada y los devuelve como una lista.

    Args:
        url (str): URL del sitio web de noticias.
        headline_selector (str): Selector CSS para encontrar elementos de titulares.
        title_attribute (str): Atributo primario para extraer del elemento (por defecto: 'text').
        fallback_attribute (str): Atributo alternativo si el primario falla.
        limit (int): Número máximo de titulares a scrapear (por defecto: 15).
        club_names (list, optional): Lista de nombres de clubes para excluir (específico para TyC Sports).
        start_index (int): Índice inicial para scrapear (por defecto: 0).
        num_to_fetch (int, optional): Número de titulares a obtener.

    Returns:
        list: Lista de titulares scrapeados.
    """
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
        
        if club_names and "tycsports" in url.lower():
            titulos = soup.find_all("img", alt=True)
            headlines = []
            for titulo in titulos[start_index:start_index + num_to_fetch]:
                found = False
                for club_name in club_names:
                    if club_name.lower() in titulo["alt"].lower():
                        found = True
                        break
                if not found:
                    headlines.append(titulo["alt"])
        else:
            elements = soup.select(headline_selector)
            headlines = []
            for element in elements:
                if title_attribute == "text":
                    headline = element.get_text(strip=True)
                else:
                    headline = element.get(title_attribute)
                    if not headline:
                        headline = element.get(fallback_attribute)
                if headline:
                    headlines.append(headline.strip())

        return headlines[:limit]

    except requests.exceptions.RequestException as e:
        st.error(f"Error al scrapear {url}: {e}")
        return []
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al scrapear {url}: {e}")
        return []

# Lista de nombres de clubes para excluir en TyC Sports
club_names = [
    "Argentinos Juniors", "Atlético Tucumán", "Banfield", "Barracas Central", "Belgrano",
    "Boca Juniors", "Central Córdoba (Santiago del Estero)", "Colón", "Defensa y Justicia",
    "Estudiantes (La Plata)", "Gimnasia (La Plata)", "Godoy Cruz", "Huracán", "Independiente",
    "Instituto", "Lanús", "Newell's", "Platense", "Racing Club", "River Plate",
    "Rosario Central", "San Lorenzo", "Sarmiento (J)", "Talleres (Córdoba)", "Tigre",
    "Unión", "Vélez"
]

# Definir las fuentes de noticias
news_sources = {
    "Ole": {"url": "https://www.ole.com.ar/", "selector": "h2.sc-fa18824-3", "limit": 30},
    "TyC Sports": {
        "url": "https://www.tycsports.com/",
        "selector": "img[alt]",
        "club_names": club_names,
        "start_index": 22,
        "num_to_fetch": 21,
        "limit": 15
    },
    "La Nación": {"url": "https://www.lanacion.com.ar/deportes/", "selector": "h2.com-title", "limit": 15},
    "ESPN": {"url": "https://www.espn.com.ar/", "selector": "h2", "limit": 15},
    "Infobae": {"url": "https://www.infobae.com/deportes/", "selector": "h2", "limit": 15},
    "Clarín": {
        "url": "https://www.clarin.com/deportes/",
        "selector": "article.sc-a70022fc-0.gjbWNc a",
        "title_attribute": "aria-label",
        "fallback_attribute": "text",
        "limit": 15
    },
    "Doble Amarilla": {"url": "https://www.dobleamarilla.com.ar/", "selector": ".title span", "limit": 15},
    "UEFA": {"url": "https://es.uefa.com/", "selector": "h2", "limit": 20},
    "La Voz": {"url": "https://www.lavoz.com.ar/deportes/", "selector": "h2", "limit": 15},
    "Cielo Sports": {"url": "https://infocielo.com/deportes", "selector": "h2", "limit": 15},
    "Bola Vip": {"url": "https://bolavip.com/ar", "selector": "h2", "limit": 25},
    "TN Deportivo": {"url": "https://tn.com.ar/deportes/", "selector": "h2.card__headline", "limit": 15},
    "Página Millonaria": {"url": "https://lapaginamillonaria.com/", "selector": "h1, h2", "limit": 15},
    "Racingdealma": {"url": "https://www.racingdealma.com.ar/", "selector": "h3 a", "limit": 12},
    "Infierno Rojo": {"url": "https://www.infiernorojo.com/independiente/", "selector": "h2", "limit": 15},
    "Mundo Azulgrana": {"url": "https://mundoazulgrana.com.ar/sanlorenzo/", "selector": "h1, h2, h3", "limit": 15},
    "As": {"url": "https://argentina.as.com/", "selector": "h2", "limit": 20, "start_index": 1},
    "Marca": {"url": "https://www.marca.com/?intcmp=BOTONPORTADA&s_kw=portada&ue_guest/", "selector": "h2", "limit": 20, "start_index": 1},
    "Mundo Deportivo": {"url": "https://www.mundodeportivo.com/", "selector": "h2", "limit": 20},
    "Sport": {"url": "https://www.sport.es/", "selector": "h2.title", "limit": 15},
    "Relevo": {"url": "https://www.relevo.com/", "selector": "h2", "limit": 20, "start_index": 1},
    "Globo Esporte": {
        "url": "https://ge.globo.com/",
        "selectors": ["h2.bstn-hl-title.gui-color-primary.gui-color-hover.gui-color-primary-bg-after", "h2", "h1"],
        "limit": [5, 10, 10],
        "start_index": [0, 0, 0]
    },
    "La Tercera de Chile": {"url": "https://www.latercera.com/canal/el-deportivo/", "selector": "h6", "limit": 20},
    "Observador Uruguay": {"url": "https://www.elobservador.com.uy/referi", "selector": "h2.titulo", "limit": 15},
    "Record Portugal": {
        "url": "https://www.record.pt/",
        "selectors": ["h1", "h2", "h3"],
        "limits": [5, 10, 10],
        "start_index": [1, 0, 0]
    },
    "BBC": {"url": "https://www.bbc.com/sport", "selector": "h1", "limit": 20},
    "Sky Sports": {"url": "https://www.skysports.com/", "selector": "h3", "limit": 25},
    "Gazzetta dello Sport": {"url": "https://www.gazzetta.it/", "selector": "h3", "limit": 20},
    "Lequipe": {"url": "https://www.lequipe.fr/", "selector": "h2", "limit": 20},
}

# Sidebar para seleccionar fuentes de noticias
st.sidebar.header("Configuración")
selected_sources = st.sidebar.multiselect(
    "Selecciona las fuentes de noticias que deseas scrapear:",
    options=list(news_sources.keys()),
    default=["Ole", "TyC Sports", "La Nación", "Clarín", "Infobae", "Doble Amarilla", "TN Deportivo", "Marca", "As", "Mundo Deportivo"]
)

# Botón para iniciar el scraping
if st.sidebar.button("Scrapear Titulares"):
    if not selected_sources:
        st.warning("Por favor, selecciona al menos una fuente de noticias.")
    else:
        all_headlines = []

        for source_name in selected_sources:
            source_data = news_sources[source_name]
            st.info(f"Scrapeando {source_name}...")

            if 'selectors' in source_data:
                # Manejo de múltiples selectores para una sola fuente
                selectors = source_data['selectors']
                limits = source_data.get('limits', [15]*len(selectors))
                start_indices = source_data.get('start_index', [0]*len(selectors))
                for i, selector in enumerate(selectors):
                    limit = limits[i] if isinstance(limits, list) else limits
                    start_index = start_indices[i] if isinstance(start_indices, list) else start_indices
                    headlines = scrape_news(
                        url=source_data["url"],
                        headline_selector=selector,
                        title_attribute=source_data.get("title_attribute", "text"),
                        fallback_attribute=source_data.get("fallback_attribute", "text"),
                        limit=limit,
                        club_names=source_data.get("club_names"),
                        start_index=start_index,
                        num_to_fetch=source_data.get("num_to_fetch")
                    )
                    all_headlines.extend([(source_name, headline) for headline in headlines if headline])
            else:
                headlines = scrape_news(
                    url=source_data["url"],
                    headline_selector=source_data.get("selector", "h2"),
                    title_attribute=source_data.get("title_attribute", "text"),
                    fallback_attribute=source_data.get("fallback_attribute", "text"),
                    limit=source_data.get("limit", 15),
                    club_names=source_data.get("club_names"),
                    start_index=source_data.get("start_index", 0),
                    num_to_fetch=source_data.get("num_to_fetch")
                )
                all_headlines.extend([(source_name, headline) for headline in headlines if headline])

        if all_headlines:
            # Crear DataFrame
            df = pd.DataFrame(all_headlines, columns=["Fuente", "Titular"])

            # Mostrar DataFrame en Streamlit
            st.success("Scraping completado exitosamente!")
            st.dataframe(df)

            # Opción para descargar el DataFrame como CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar como CSV",
                data=csv,
                file_name='titulares_scrapeados.csv',
                mime='text/csv',
            )
        else:
            st.error("No se encontraron titulares en las fuentes seleccionadas.")
