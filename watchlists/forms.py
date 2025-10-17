from django import forms
from .models import Watchlist, WatchlistItem

class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ["name", "description", "privacy"]

class WatchlistItemForm(forms.ModelForm):
    class Meta:
        model = WatchlistItem
        fields = ["movie_id", "title", "poster_url"]