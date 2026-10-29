from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from .forms import ReviewForm
from .models import Production, Review


@require_GET
def catalog(request):
    films = Production.objects.annotate(average_rating=Avg('reviews__rating')).order_by('title', 'id')
    kind = request.GET.get('kind', '')
    genre = request.GET.get('genre', '')
    if kind:
        films = films.filter(kind=kind)
    if genre:
        films = films.filter(genre=genre)
    genres = Production.objects.values_list('genre', flat=True).distinct().order_by('genre')
    return render(request, 'movies/catalog.html', {'films': films, 'genres': genres, 'kind': kind, 'genre': genre})


@require_GET
def detail(request, pk):
    film = get_object_or_404(Production, pk=pk)
    review = None
    if request.user.is_authenticated:
        review = film.reviews.filter(user=request.user).first()
    form = ReviewForm(instance=review)
    return render(request, 'movies/detail.html', {
        'film': film, 'reviews': film.reviews.select_related('user'),
        'average': film.average(), 'form': form,
    })


@login_required
@require_http_methods(['POST'])
def add_review(request, pk):
    film = get_object_or_404(Production, pk=pk)
    form = ReviewForm(request.POST)
    if form.is_valid():
        # Autor pochodzi z sesji, a film z adresu strony.
        Review.objects.update_or_create(
            production=film, user=request.user,
            defaults={'rating': form.cleaned_data['rating'], 'text': form.cleaned_data['text']},
        )
        return redirect('detail', pk=film.pk)
    return render(request, 'movies/detail.html', {
        'film': film, 'reviews': film.reviews.select_related('user'),
        'average': film.average(), 'form': form,
    }, status=400)


@require_GET
def ranking(request):
    films = Production.objects.annotate(
        average_rating=Avg('reviews__rating'), review_count=Count('reviews'),
    ).filter(review_count__gt=0).order_by('-average_rating', '-review_count', 'title', 'id')[:10]
    return render(request, 'movies/ranking.html', {'films': films})


@require_http_methods(['GET', 'POST'])
def register(request):
    form = UserCreationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('profile')
    return render(request, 'registration/register.html', {'form': form})


@login_required
@require_GET
def profile(request):
    reviews = request.user.reviews.select_related('production')
    return render(request, 'movies/profile.html', {'reviews': reviews})
