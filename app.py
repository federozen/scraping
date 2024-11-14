# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

# Descargar stopwords en español si no están descargadas
nltk.download('stopwords')
nltk.download('punkt')

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
club_names = ["Argentinos Juniors", "Atlético Tucumán", "Banfield", "Barracas Central", ...]

# Definir las fuentes de noticias
news_sources = {...}  # Define aquí el diccionario de fuentes de noticias

# Sidebar para seleccionar fuentes de noticias
st.sidebar.header("Configuración")
selected_sources = st.sidebar.multiselect(
    "Selecciona las fuentes de noticias que deseas scrapear:",
    options=list(news_sources.keys()),
    default=["Ole", "TyC Sports", "La Nación", "Clarín", "Infobae"]
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
            df = pd.DataFrame(all_headlines, columns=["Fuente", "Headline"])

            # Preprocesamiento para el análisis de tendencias
            spanish_stopwords = set(stopwords.words('spanish'))
            def preprocess_text(text):
                tokens = word_tokenize(text.lower())
                tokens = [word for word in tokens if word.isalnum() and word not in spanish_stopwords]
                return ' '.join(tokens)

            df['Processed_Headline'] = df['Headline'].apply(preprocess_text)
            all_headlines_text = ' '.join(df['Processed_Headline'].tolist())

            # Nube de palabras
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_headlines_text)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Nube de Palabras de los Títulos')
            st.pyplot(plt)

            # Conteo de palabras
            word_counts = Counter(all_headlines_text.split())
            most_common_words = word_counts.most_common(30)
            words, counts = zip(*most_common_words)
            
            # Gráfico de barras
            plt.figure(figsize=(10, 6))
            plt.barh(words, counts)
            plt.xlabel('Frecuencia')
            plt.ylabel('Palabras')
            plt.title('30 Palabras Más Frecuentes en los Títulos')
            st.pyplot(plt)

            # Informe de tendencias
            st.subheader("Informe de Tendencias en los Títulos")
            st.markdown("""
                En base al análisis de la columna 'Headline', se identificaron las siguientes tendencias:
                - **Palabras más frecuentes:** {}
                - **Temas principales:** Se observan temas recurrentes como...
                - **Fuentes destacadas:** Las fuentes con mayor cantidad de titulares son...
                - **Evolución temporal:** Se recomienda realizar un análisis de series de tiempo para observar cómo varían los temas.
            """.format(", ".join([word for word, count in most_common_words])))

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
