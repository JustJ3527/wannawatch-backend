from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.search_view, name="search"),
    path("<str:media_type>/<int:tmdb_id>/", views.details_view, name="details"),
]