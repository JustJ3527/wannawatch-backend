from django.shortcuts import HttpResponse, render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db import models

from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from .models import Watchlist, WatchlistItem
from .forms import WatchlistForm, WatchlistItemForm
from movies.utils import get_tmdb_language
from movies.services import get_tmdb_details

@login_required
def watchlist_list(request):
    watchlists = Watchlist.objects.filter(
        models.Q(owner=request.user) | models.Q(members=request.user)
    ).distinct()
    return render(request, "watchlists/list.html", {"watchlists": watchlists})

@login_required
def watchlist_create(request):
    if request.method == "POST":
        form = WatchlistForm(request.POST)
        if form.is_valid():
            watchlist = form.save(commit=False)
            watchlist.owner = request.user
            watchlist.save()
            return redirect("watchlist_detail", pk=watchlist.pk)
    else:
        form = WatchlistForm()
    return render(request, "watchlists/create.html", {"form": form})

@login_required
def watchlist_detail(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk)
    
    # Check if user can edit or consult watchlist
    if watchlist.privacy == "private" and not watchlist.can_edit(request.user):
        return HttpResponseForbidden("Access denied.")
    
    tmdbLang = get_tmdb_language()

    items = watchlist.items.all()
    for item in items:
        details = get_tmdb_details(item.movie_id, item.media_type, lang=tmdbLang)
        if details:
            item.tmdb_title = details.get("title")
            item.tmdb_poster = details.get("poster")
            item.tmdb_overview = details.get("overview")
            item.tmdb_release_date = details.get("release_date")

    form = WatchlistItemForm()

    return render(request, "watchlists/detail.html", {
        "watchlist": watchlist,
        "items": items,
        "form": form, 
        "tmdb_lang": tmdbLang
    })

@login_required
def add_item(request, pk):
    watchlist = get_object_or_404(Watchlist, pk=pk)
    if not watchlist.can_edit(request.user):
        return HttpResponseForbidden("Access denied.")
    
    if request.method == "POST":
        form = WatchlistItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.watchlist = watchlist
            item.added_by = request.user
            item.save()
            return redirect("watchlist_detail", pk=pk)
    return redirect("watchlist_detail", pk=pk)

@login_required
def toggle_watched(request, pk, item_id):
    item = get_object_or_404(WatchlistItem, pk=item_id, watchlist_id=pk)
    if not item.watchlist.can_edit(request.user):
        message = _("Access denied.")
        type_ = "error"
        return JsonResponse({"message": message, "type": type_})

    item.watched = not item.watched
    item.save()


    if request.headers.get("HX-Request"):
        # --- Récupérer la langue TMDB
        tmdbLang = get_tmdb_language()

        # --- Récupérer les détails TMDB
        details = get_tmdb_details(item.movie_id, item.media_type, lang=tmdbLang)
        if details:
            item.tmdb_title = details.get("title")
            item.tmdb_poster = details.get("poster")
            item.tmdb_overview = details.get("overview")
            item.tmdb_release_date = details.get("release_date")
        else:
            item.tmdb_title = item.title
            item.tmdb_poster = item.posyer
            item.tmdb_overview = item.overview
            item.tmdb_release_date = item.release_date

        html = render_to_string("watchlists/partials/watchlist_item.html", {"item": item})
        return HttpResponse(html)

    return redirect("watchlist_detail", pk=pk)

@login_required
def add_to_watchlist(request, watchlist_id):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id)

    if not watchlist.can_edit(request.user):
        return HttpResponseForbidden("You cannot edit this watchlist.")

    movie_id = request.POST.get("movie_id")
    title = request.POST.get("title")
    poster_url = request.POST.get("poster_url")
    media_type = request.POST.get("media_type")

    if not all([movie_id, title, media_type]):
        return JsonResponse({"error": "Missing movie information"}, status=400)

    item, created = WatchlistItem.objects.get_or_create(
        watchlist=watchlist,
        movie_id=movie_id,
        defaults={
            "title": title,
            "poster_url": poster_url,
            "media_type": media_type,
            "added_by": request.user,
        }
    )

    if not created:
        message = _("'%(title)s' is already in '%(watchlist)s'") % {
            "title": title,
            "watchlist": watchlist.name
        }
        type_ = "info"
    else:
        message = _("'%(title)s' added to '%(watchlist)s'") % {
            "title": title,
            "watchlist": watchlist.name
        }
        type_ = "success"

    return JsonResponse({"message": message, "type": type_})