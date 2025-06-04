import streamlit as st
import requests
from bs4 import BeautifulSoup
from googlesearch import search

def web_search(query, num_results=3):
    """Realiza una búsqueda en la web usando Google"""
    try:
        return list(search(query, num_results=num_results, stop=num_results, pause=2))
    except Exception as e:
        st.error(f"Error en búsqueda: {str(e)}")
        return []

def get_news(topic, num_articles=3):
    """Obtiene noticias sobre un tema específico usando NewsAPI"""
    try:
        news_api_key = st.secrets.get("NEWS_API_KEY")
        if not news_api_key:
            st.warning("Clave de NewsAPI no configurada")
            return []
            
        url = f"https://newsapi.org/v2/everything?q={topic}&pageSize={num_articles}&apiKey={news_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        
        formatted = []
        for article in articles:
            title = article.get('title', 'Sin título')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Fuente desconocida')
            formatted.append(f"{title} ({source}) - {url}")
        
        return formatted
    except Exception as e:
        st.error(f"Error al obtener noticias: {str(e)}")
        return []

def handle_web_commands(message_content):
    """Maneja comandos relacionados con búsqueda web y noticias"""
    if message_content.startswith("/buscar "):
        query = message_content[8:]
        results = web_search(query)
        if not results:
            return "🔍 No encontré resultados. Prueba con otros términos."
        return "🔍 **Resultados de búsqueda:**\n\n" + "\n\n".join(f"- [{i+1}] {r}" for i, r in enumerate(results))
    
    elif message_content.startswith("/noticias "):
        topic = message_content[9:]
        articles = get_news(topic)
        if not articles:
            return "📰 No encontré noticias recientes sobre este tema."
        return "📰 **Últimas noticias:**\n\n" + "\n\n".join(f"- {art}" for art in articles)
    
    return None