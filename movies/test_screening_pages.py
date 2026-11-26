from datetime import datetime
from types import SimpleNamespace
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import path
from django.utils import timezone
from .urls import urlpatterns as movie_urls


def page(request, pk):
    return HttpResponse()


urlpatterns = movie_urls + [
    path('show/<int:pk>/join/', page, name='join_show'),
    path('show/<int:pk>/leave/', page, name='leave_show'),
]


@override_settings(ROOT_URLCONF=__name__)
class ScreeningPageTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get('/film/1/')
        self.request.user = User(username='danylo')
        self.show = SimpleNamespace(
            pk=1, film=SimpleNamespace(pk=1, title='Film A'),
            date=timezone.make_aware(datetime(2026, 12, 10, 18)),
            place='Sala 1', free=5, joined=False, closed=False,
        )

    def render(self, name='screenings', ready=True):
        return render_to_string('movies/' + name + '.html', {
            'shows_ready': ready, 'shows': [self.show], 'my_shows': [self.show],
        }, request=self.request)

    def test_join_form(self):
        html = self.render()
        self.assertIn('10.12.2026 18:00', html)
        self.assertIn('Sala 1', html)
        self.assertIn('action="/show/1/join/"', html)
        self.assertIn('method="post"', html)
        self.assertIn('csrfmiddlewaretoken', html)

    def test_guest_full_and_closed(self):
        self.request.user = AnonymousUser()
        html = self.render()
        self.assertIn('Zaloguj się', html)
        self.assertNotIn('<form', html)
        self.show.free = 0
        self.assertIn('Brak wolnych miejsc', self.render())
        self.show.closed = True
        self.assertIn('Zapisy na ten seans są zamknięte', self.render())

    def test_cancel_when_full(self):
        self.show.joined = True
        self.show.free = 0
        html = self.render()
        self.assertIn('Jesteś zapisany', html)
        self.assertIn('action="/show/1/leave/"', html)
        self.assertNotIn('Zapisz się na seans', html)
        self.assertIn('Film A', self.render('bookings'))

    def test_missing_backend_and_empty_list(self):
        self.assertIn('nie są jeszcze dostępne', self.render(ready=False))
        with override_settings(ROOT_URLCONF='movies.urls'):
            html = self.render()
            self.assertIn('Zapisy są chwilowo niedostępne', html)
            self.assertNotIn('<form', html)
        html = render_to_string('movies/screenings.html', {
            'shows_ready': True, 'shows': [],
        }, request=self.request)
        self.assertIn('Nie ma jeszcze zaplanowanych seansów', html)

    def test_escape_place(self):
        self.show.place = '<script>alert(1)</script>'
        html = self.render()
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)
