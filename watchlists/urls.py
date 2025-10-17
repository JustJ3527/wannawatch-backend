from django.urls import path
from . import views

urlpatterns = [
    path("", views.watchlist_list, name="watchlist_list"),
    path("new/", views.watchlist_create, name="watchlist_create"),
    path("<int:pk>/", views.watchlist_detail, name="watchlist_detail"),
    path("<int:pk>/add/", views.add_item, name="add_item"),
    path("<int:pk>/toggle/<int:item_id>/", views.toggle_watched, name="toggle_watched"),
    path("add/<int:watchlist_id>/", views.add_to_watchlist, name="add_to_watchlist"),

]