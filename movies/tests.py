from django.test import TestCase
from django.test import Client, override_settings
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.urls import reverse
from .models import Production, Review

# Puste szablony tylko do testów backendu. HTML należy do Danyla.
templates = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {'loaders': [('django.template.loaders.locmem.Loader', {
        name: '{{ form.errors }}' for name in [
            'movies/catalog.html', 'movies/detail.html', 'movies/ranking.html',
            'movies/profile.html', 'registration/register.html', 'registration/login.html',
        ]
    })]},
}]


@override_settings(TEMPLATES=templates)
class BackendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('myroslav', password='Test-password-482!')
        self.other = User.objects.create_user('danylo', password='Test-password-582!')
        self.film = Production.objects.create(title='Film A', description='Opis', kind='film', genre='Komedia', year=2020)
        self.url = reverse('add_review', args=[self.film.pk])

    def test_register_login_logout(self):
        response = self.client.post(reverse('register'), {
            'username': 'nowy', 'password1': 'Nowe-haslo-792!', 'password2': 'Nowe-haslo-792!',
        })
        self.assertRedirects(response, reverse('profile'))
        user = User.objects.get(username='nowy')
        self.assertTrue(user.check_password('Nowe-haslo-792!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('login'), {'username': 'nowy', 'password': 'Nowe-haslo-792!'})
        self.assertRedirects(response, reverse('profile'))

    def test_invalid_registration(self):
        for name, password in [('myroslav', 'Dobre-haslo-792!'), ('nowy', '123')]:
            response = self.client.post(reverse('register'), {
                'username': name, 'password1': password, 'password2': password,
            })
            self.assertTrue(response.context['form'].errors)
        self.assertEqual(User.objects.count(), 2)

    def test_guest_permissions(self):
        self.assertEqual(self.client.post(self.url, {'rating': 8}).status_code, 302)
        self.assertEqual(self.client.get(reverse('profile')).status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_save_and_update_only_own_review(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {'rating': 8, 'text': 'Dobry', 'user': self.other.pk, 'production': 999})
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.production, self.film)
        self.client.post(self.url, {'rating': 10, 'text': 'Nowa opinia'})
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(self.film.average(), 10)

    def test_invalid_rating_and_get(self):
        self.client.force_login(self.user)
        for rating in [0, 11, 'abc', '', 2.5]:
            response = self.client.post(self.url, {'rating': rating})
            self.assertEqual(response.status_code, 400)
            self.assertTrue(response.context['form'].errors)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertEqual(Review.objects.count(), 0)

    def test_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.url, {'rating': 8}).status_code, 403)

    def test_database_constraints(self):
        Review.objects.create(production=self.film, user=self.user, rating=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(production=self.film, user=self.user, rating=5)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(production=self.film, user=self.other, rating=11)

    def test_average_after_edit_and_delete(self):
        self.assertIsNone(self.film.average())
        first = Review.objects.create(production=self.film, user=self.user, rating=10)
        second = Review.objects.create(production=self.film, user=self.other, rating=2)
        self.assertEqual(self.film.average(), 6)
        second.rating = 6
        second.save()
        self.assertEqual(self.film.average(), 8)
        first.delete()
        self.assertEqual(self.film.average(), 6)

    def test_filters_and_detail(self):
        Production.objects.create(title='Serial B', description='Opis', kind='serial', genre='Dramat', year=2021)
        response = self.client.get(reverse('catalog'), {'kind': 'film', 'genre': 'Komedia'})
        self.assertEqual(list(response.context['films']), [self.film])
        response = self.client.get(reverse('detail', args=[self.film.pk]))
        self.assertEqual(response.context['film'], self.film)
        self.assertEqual(self.client.get(reverse('detail', args=[999])).status_code, 404)

    def test_ranking(self):
        for n in range(12):
            film = Production.objects.create(title=f'Film {n:02}', description='Opis', kind='film', genre='Dramat', year=2020)
            Review.objects.create(production=film, user=self.user, rating=min(n + 1, 10))
        films = list(self.client.get(reverse('ranking')).context['films'])
        self.assertEqual(len(films), 10)
        self.assertNotIn(self.film, films)
        self.assertEqual([f.average_rating for f in films], [10, 10, 10, 9, 8, 7, 6, 5, 4, 3])

    def test_profile(self):
        mine = Review.objects.create(production=self.film, user=self.user, rating=8)
        Review.objects.create(production=self.film, user=self.other, rating=2)
        self.client.force_login(self.user)
        self.assertEqual(list(self.client.get(reverse('profile')).context['reviews']), [mine])

    def test_admin_permissions(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 302)
        admin = User.objects.create_superuser('admin', password='Admin-password-792!')
        self.client.force_login(admin)
        with self.settings(TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates', 'APP_DIRS': True,
            'OPTIONS': {'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ]},
        }]):
            self.assertEqual(self.client.get(reverse('admin:movies_production_changelist')).status_code, 200)
            self.assertEqual(self.client.get(reverse('admin:movies_review_changelist')).status_code, 200)
