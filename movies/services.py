import os

from django.db.models.expressions import result
from dotenv import load_dotenv
load_dotenv()

import requests
from django.conf import settings
from django.utils import translation

from .utils import get_tmdb_language

# Constants
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_BASE_URL_IMAGE = "https://image.tmdb.org/t/p"

def search_tmdb(query):
    """Search TMDB API for movies based on query"""
    if not query:
        return []

    tmdb_lang = get_tmdb_language()
    url = f"{TMDB_BASE_URL}/search/multi"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": tmdb_lang,
        "include_adult": False,
    }
    r = requests.get(url, params=params)
    data = r.json()
    results = []

    for item in data.get("results", []):
        if item.get("media_type") not in ["movie", "tv"]:
            continue
        results.append({
            "id": item.get("id"),
            "title": item.get("title") or item.get("name"),
            "media_type": "Movie" if item.get("media_type") == "movie" else "Tv",
            "poster": f"{TMDB_BASE_URL_IMAGE}/w300{item.get('poster_path')}" if item.get("poster_path") else None,
            "year": (item.get("release_date") or item.get("first_air_date") or "")[:4],
        })
    return results

def get_watch_providers(tmdb_id, media_type, country_code = "EN"):
    """Return streaming platforms"""
    if media_type not in ["movie", "tv"]:
        return []
    
    url = f"{TMDB_BASE_URL}/{media_type}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    r = requests.get(url, params=params)
    data = r.json()

    country_data = data.get("results", {}).get(country_code, {})
    providers = country_data.get("flatrate", []) or []

    formatted = []
    for p in providers:
        formatted.append({
            "name": p.get("provider_name"),
            "logo": f"{TMDB_BASE_URL_IMAGE}/w45{p.get("logo_path")}" if p.get("logo_path") else None
        })

import requests

def get_user_country(request):
    """
    Détecte le pays de l'utilisateur selon son IP (via une API gratuite).
    Exemple : renvoie 'FR', 'US', 'CA', etc.
    """
    try:
        ip = request.META.get('REMOTE_ADDR', '')
        if ip in ('127.0.0.1', 'localhost', ''):
            # Par défaut pour le dev local
            return 'FR'

        response = requests.get(f"https://ipapi.co/{ip}/json/")
        if response.status_code == 200:
            data = response.json()
            return data.get('country_code', 'FR')
    except Exception:
        pass

    return 'FR'


def get_tmdb_details(tmdb_id, media_type, lang="en"):
    url = f"{TMDB_BASE_URL}/{media_type.lower()}/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": lang,
    }
    print(url)
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        
        title = data.get("title") or data.get("name")
        overview = data.get("overview", "")
        
        poster = f"{TMDB_BASE_URL_IMAGE}/w300{data['poster_path']}" if data.get("poster_path") else None
        backdrop = f"{TMDB_BASE_URL_IMAGE}/w780{data['backdrop_path']}" if data.get("backdrop_path") else None

        releaseDate = data.get("release_date") or data.get("first_air_date")

        return {
            "title": title,
            "overview": overview,

            "poster": poster,
            "backdrop": backdrop,

            "release_date": releaseDate,
        }
    return None