import os
import requests
from typing import Dict, Any
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def research(query: str) -> Dict[str, Any]:
    """
    Realiza búsqueda bilingüe usando Serper API
    """
    try:
        # Búsqueda en español
        spanish_results = search_serper(query, "es")
        
        # Búsqueda en inglés
        english_query = f"english {query}"
        english_results = search_serper(english_query, "en")
        
        # Combinar resultados
        results = {
            "spanish": spanish_results,
            "english": english_results
        }
        
        return format_results(results)
        
    except Exception as e:
        logger.error(f"Error en research: {str(e)}")
        return {"error": str(e)}

def search_serper(query: str, language: str) -> Dict[str, Any]:
    """
    Realiza búsqueda usando Serper API
    """
    url = "https://google.serper.dev/search"
    
    payload = {
        "q": query,
        "gl": "es" if language == "es" else "us",
        "hl": language
    }
    
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en búsqueda Serper: {str(e)}")
        return {"error": str(e)}

def format_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formatea los resultados de búsqueda
    """
    formatted = {
        "spanish_results": [],
        "english_results": []
    }
    
    # Formatear resultados en español
    if "spanish" in results and "organic" in results["spanish"]:
        formatted["spanish_results"] = [
            {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            }
            for result in results["spanish"]["organic"][:5]
        ]
    
    # Formatear resultados en inglés
    if "english" in results and "organic" in results["english"]:
        formatted["english_results"] = [
            {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            }
            for result in results["english"]["organic"][:5]
        ]
    
    return formatted

def write_content(research_material: str, topic: str) -> Dict[str, Any]:
    """
    Formatea el contenido para escritura
    """
    try:
        return {
            "content": research_material,
            "topic": topic,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Error en write_content: {str(e)}")
        return {"error": str(e)}