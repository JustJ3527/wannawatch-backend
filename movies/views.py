import requests
from .services import TMDB_API_KEY, TMDB_BASE_URL, TMDB_BASE_URL_IMAGE

from django.shortcuts import render
from django.utils import translation


from .services import search_tmdb, get_user_country

def search_view(request):
    query = request.GET.get("q")
    results = search_tmdb(query) if query else []
    return render(request, "movies/search.html", {"results": results, "query": query})

def details_view(request, media_type, tmdb_id):
    """
    Affiche la page de détails d'un film ou d'une série.
    """

    lang = translation.get_language() or "fr"
    lang = lang.lower()
    lang_map = {
        "fr": "fr-FR",
        "en": "en-US"
    }
    tmdb_lang = lang_map.get(lang, "en-US")

    # --- Infos principales
    url = (
        f"https://api.themoviedb.org/3/{media_type.lower()}/{tmdb_id}"
        f"?api_key={TMDB_API_KEY}"
        f"&language={tmdb_lang}"
        f"&append_to_response=videos,credits,watch/providers"
    )

    response = requests.get(url)
    data = response.json()

    # --- Détails utiles
    title = data.get("title") or data.get("name")
    overview = data.get("overview")
    poster = f"{TMDB_BASE_URL_IMAGE}/w500{data.get('poster_path')}" if data.get("poster_path") else None
    backdrop = f"{TMDB_BASE_URL_IMAGE}/original{data.get('backdrop_path')}" if data.get("backdrop_path") else None
    release_date = data.get("release_date") or data.get("first_air_date")
    genres = [g["name"] for g in data.get("genres", [])]
    vote_average = data.get("vote_average")
    runtime = data.get("runtime") or (data.get("episode_run_time")[0] if data.get("episode_run_time") else None)

    # --- Vidéos / trailer
    videos = data.get("videos", {}).get("results", [])
    trailer = next((v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"), None)
    trailer_url = f"https://www.youtube.com/embed/{trailer['key']}" if trailer else None

    # --- Acteurs principaux
    credits = data.get("credits", {}).get("cast", [])[:8]

    # --- Plateformes de streaming
    country_code = get_user_country(request)
    providers = data.get("watch/providers", {}).get("results", {}).get(country_code, {})

    subscriptions = [
        {
            "name": p["provider_name"],
            "logo": f"{TMDB_BASE_URL_IMAGE}/w92{p['logo_path']}" if p.get("logo_path") else None,
            "link": providers.get("link")
        }
        for p in providers.get("flatrate", [])
    ]

    # --- Buy / Rent regroupés par provider
    buy_rent_dict = {}
    for type_key in ["rent", "buy"]:
        for p in providers.get(type_key, []):
            key = p["provider_name"]
            if key not in buy_rent_dict:
                buy_rent_dict[key] = {
                    "name": key,
                    "logo": f"{TMDB_BASE_URL_IMAGE}/w92{p['logo_path']}" if p.get("logo_path") else None,
                    "link": providers.get("link"),
                    "types": set()
                }
            buy_rent_dict[key]["types"].add(type_key)

    # Transformer en liste pour le template
    buy_rent_list = []
    for provider in buy_rent_dict.values():
        provider["types"] = ", ".join([t.title() for t in sorted(provider["types"])])
        buy_rent_list.append(provider)



    context = {
        "id": tmdb_id,
        "title": title,
        "overview": overview,
        "poster": poster,
        "backdrop": backdrop,
        "release_date": release_date,
        "genres": genres,
        "vote_average": vote_average,
        "runtime": runtime,
        "trailer_url": trailer_url,
        "credits": credits,
        "subscriptions": subscriptions,
        "buy_rent_list": buy_rent_list,
        "media_type": media_type,
        "tmdb_lang": tmdb_lang
    }

    return render(request, "movies/details.html", context)