from django.utils import translation
def get_tmdb_language():
    """
    Return language in the right format for tmdb (ex: 'fr-FR', 'en-US').
    """
    lang = translation.get_language() or "fr"
    lang = lang.lower()
    lang_map = {
        "fr": "fr-FR",
        "en": "en-US",
    }
    return lang_map.get(lang, "en-US")