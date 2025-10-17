from django.contrib import admin
from .models import Watchlist, WatchlistItem

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'privacy', 'created_at')
    list_filter = ('privacy',)

@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'watchlist', 'added_by', 'added_at')