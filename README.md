# Ocena filmów i seriali

Backend: Myroslav Sobol, grupa 9. Django 5.2 i SQLite.

Kod obejmuje projekt, modele, migracje, panel admina, rejestrację, logowanie,
wylogowanie, profil, oceny, recenzje i ranking. HTML, CSS, Bootstrap i integracja
interfejsu należą do Danyla. Nie ma tu gotowych szablonów stron użytkownika.
Do czasu ich dodania takie strony zgłoszą `TemplateDoesNotExist`.
Panel `/admin/` działa samodzielnie. Testy używają pustych szablonów w pamięci.

## Uruchomienie na Windows

W folderze projektu, Python 3.10 lub nowszy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

Panel: http://127.0.0.1:8000/admin/ . Dodaj filmy i seriale przez panel.
Baza i hasła użytkowników nie są przechowywane w GitHub.

## Jak działa kod

- `movies/models.py`: Production to film lub serial, Review to ocena użytkownika.
- `movies/forms.py`: formularz przyjmuje tylko ocenę i treść opinii.
- `movies/views.py`: proste funkcje obsługujące strony.
- `movies/urls.py`: adresy stron.
- `movies/admin.py`: zarządzanie produkcjami i moderowanie recenzji.
- `movies/tests.py`: sprawdzenie logiki i uprawnień.

Jedna recenzja na użytkownika i produkcję. Kolejne wysłanie aktualizuje ją.
Autor pochodzi z sesji. Ocena: liczba całkowita 1–10. Opinia może być pusta.
Średnia jest obliczana z aktualnych ocen, także po moderacji. Brak ocen daje
`None`. Ranking: maksymalnie 10 ocenionych produkcji, od najwyższej średniej;
remis rozstrzyga liczba ocen, potem tytuł i id. Profil używa standardowego
User i pokazuje własne recenzje. Zarządzanie produkcjami wymaga praw admina.

## Szablony dla Danyla

Umieść pliki w `templates/` lub `movies/templates/`.

| Adres i nazwa URL | Szablon | Dane |
| --- | --- | --- |
| `/` — `catalog` | `movies/catalog.html` | films, genres, kind, genre |
| `/film/<pk>/` — `detail` | `movies/detail.html` | film, reviews, average, form |
| `/ranking/` — `ranking` | `movies/ranking.html` | films |
| `/register/` — `register` | `registration/register.html` | form |
| `/login/` — `login` | `registration/login.html` | form, next |
| `/profile/` — `profile` | `movies/profile.html` | reviews, request.user |

Film: `title`, `description`, `kind` (film/serial), `genre`, `year`, `poster`
(opcjonalny URL). Katalog i ranking: `film.average_rating`; ranking ma też
`film.review_count`. Recenzja: `user`, `production`, `rating`, `text`, `created`.
Filtry: `?kind=film&genre=Komedia`.

Rejestracja i logowanie: POST na ten sam adres, `{{ form.as_p }}` i
`{% csrf_token %}`. Rejestracja: `username`, `password1`, `password2`.
Logowanie: `username`, `password`, opcjonalne `next`.
Wylogowanie: POST do `{% url 'logout' %}` z CSRF.
Opinia: POST do `{% url 'add_review' film.pk %}` z CSRF i polami `rating`, `text`.
Wyświetl błędy `form`; błędna opinia zwraca 400. Formularz opinii pokazuj
zalogowanym. Tekst recenzji wyświetlaj normalnie, bez filtra `safe`.

## Etapy do 12 listopada 2026

Etap 1 opisuje dostarczone sprawozdanie zespołu. Backend etapu 2: modele,
migracja, SQLite. Backend etapu 3: konta, profil i uprawnienia. Pełny etap 3
wymaga jeszcze szablonów i integracji Danyla. Recenzje i ranking realizują
dalsze zadania Myroslava z podziału pracy.

## GitHub

Gałąź: `myroslav-backend`. Repozytorium było puste. Pobierz aktualny kod przed
pracą, aby zachować zmiany drugiej osoby. Pull Request wymaga istniejącej
gałęzi docelowej z historią projektu.

## PythonAnywhere

Najpierw połącz backend z szablonami. Wybierz aplikację Web przeznaczoną dla
projektu; nie zastępuj przypadkiem istniejącej aplikacji laboratoryjnej.
W poniższych przykładach zamień LOGIN i domenę na dane konta.

W konsoli Bash (Python musi być zgodny z wersją wybraną w Web):

```bash
git clone --branch myroslav-backend https://github.com/DanyloShymanskyi/Projekt.git
cd Projekt
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

Web: Manual configuration, zgodna wersja Pythona.
Source code i Working directory: `/home/LOGIN/Projekt`.
Virtualenv: `/home/LOGIN/Projekt/.venv`.
Static files: URL `/static/`, katalog `/home/LOGIN/Projekt/staticfiles`.
Plik WSGI otwierany z zakładki Web:

```python
import os
import sys

sys.path.insert(0, '/home/LOGIN/Projekt')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DJANGO_DEBUG'] = '0'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'LOGIN.pythonanywhere.com'
os.environ['DJANGO_SECRET_KEY'] = 'TU_WSTAW_WLASNY_LOSOWY_KLUCZ'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Wygeneruj klucz w konsoli:
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`.
Wklej go tylko do pliku WSGI na koncie, nie do GitHub. Domena musi być zgodna
z adresem w Web. Kliknij Reload i otwórz witrynę przez HTTPS.

Źródła: [PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/),
[Django](https://docs.djangoproject.com/en/5.2/releases/5.2.18/).

## Przekazanie pracy

Zespołowi przekaż gałąź z backendem i opis szablonów powyżej. Sprawozdanie
etapów 1–3 przygotuj według wzoru prowadzącej, z rzeczywistymi wynikami i
zrzutami po integracji. Wzór `Sprawozdanie_szczegolowe_etapy_1-3.docx` nie
został dostarczony. Testy backendu nie potwierdzają gotowego interfejsu.
Publikacja PythonAnywhere i wysłanie zadania nie są wykonane.
