from pydoc import describe
from random import choices
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User =  get_user_model()

class Watchlist(models.Model):
    PRIVACY_CHOICES = [
        ("private", "Private"),
        ("public", "Public"),
        ("collaborative", "Collaborative")
    ]
    
    owner = models.ForeignKey(User, related_name='owned_watchlists', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="collaborative_watchlists", blank=True, verbose_name=_("Members"))

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(max_length=300, blank=True, verbose_name=_("Description"))
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default="private", verbose_name=_("privacy"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "name")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.name} ({self.owner})"
    
    def can_edit(self, user):
        return user == self.owner or (self.privacy == "collaborative" and user in self.members.all())

class WatchlistItem(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name="items")
    movie_id = models.CharField(max_length=50) # ID from TMDB
    title = models.CharField(max_length=255)

    poster_url = models.URLField(blank=True)
    media_type = models.CharField(max_length=50, default='movie')  # film ou série


    watched = models.BooleanField(default=False)

    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="added_items")
    added_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("watchlist", "movie_id")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.title} in {self.watchlist.name}"