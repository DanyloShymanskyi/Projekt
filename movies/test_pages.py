from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Production, Review


class PageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('danylo', password='Test-password-582!')
        self.film = Production.objects.create(
            title='Film A', description='Opis filmu', kind='film',
            genre='Komedia', year=2020, poster='https://example.com/poster.jpg',
        )

    def test_catalog_and_poster(self):
        page = self.client.get(reverse('catalog'), {'genre': 'Komedia'})
        self.assertContains(page, 'Film A')
        self.assertContains(page, 'value="Komedia" selected')
        self.assertContains(page, 'src="https://example.com/poster.jpg"')
        self.assertContains(page, 'Brak ocen')
        page = self.client.get(reverse('catalog'), {'kind': 'serial'})
        self.assertNotContains(page, 'Film A')
        self.assertContains(page, 'Brak filmów i seriali')

    def test_review_and_errors(self):
        url = reverse('detail', args=[self.film.pk])
        self.assertNotContains(self.client.get(url), 'name="rating"')
        self.client.force_login(self.user)
        self.assertContains(self.client.get(url), 'name="rating"')
        Review.objects.create(
            production=self.film, user=self.user, rating=8,
            text='<script>alert(1)</script>',
        )
        page = self.client.get(url)
        self.assertContains(page, '8,0 / 10')
        self.assertContains(page, '&lt;script&gt;')
        self.assertNotContains(page, '<script>alert(1)</script>')
        self.assertContains(self.client.get(reverse('profile')), 'Film A')
        self.assertContains(self.client.get(reverse('ranking')), 'Film A')
        page = self.client.post(reverse('add_review', args=[self.film.pk]), {
            'rating': 11, 'text': 'Moja opinia',
        })
        self.assertContains(page, 'errorlist', status_code=400)
        self.assertContains(page, 'Moja opinia', status_code=400)
