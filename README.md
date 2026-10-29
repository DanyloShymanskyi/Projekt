Markdown
# System Oceniania Filmów i Seriali (Grupa 9)

Aplikacja internetowa służąca do przeglądania oraz oceniania filmów i seriali. Wszystkie dane dotyczące użytkowników, ocen i produkcji są przechowywane w relacyjnej bazie danych SQLite.

## Autorzy projektu
* **Myroslav Sobol** – Backend / Logika aplikacji (projekt Django, modele, baza danych, autoryzacja, panel administratora, system obliczania średnich ocen).
* **Danylo Shymanskyi** – Frontend / Integracja / UX (szablony HTML, stylizacja za pomocą CSS i Bootstrap, wyświetlanie danych, zapewnienie responsywności).
## Główne funkcjonalności
* **Katalog produkcji:** Wyświetlanie głównego katalogu filmów i seriali wraz z ich opisami i plakatami.
* **Wyszukiwanie i filtrowanie:** Umożliwia filtrowanie produkcji według typu (film/serial) lub przypisanego gatunku.
* **System autoryzacji:** Pełna obsługa kont – rejestracja, logowanie i wylogowywanie użytkowników.
* **Oceny i recenzje:** Pozwala wyłącznie zalogowanym użytkownikom na dodawanie ocen (skala 1–10) i pisanie recenzji. Jeden użytkownik może dodać jedną opinię do danej produkcji (każda kolejna wysłana opinia aktualizuje poprzednią).
* **Ranking Top 10:** Aplikacja automatycznie oblicza i aktualizuje średnią ocenę dla każdej produkcji oraz generuje ranking najwyżej ocenianych tytułów.
* **Panel Administratora:** Umożliwia pełne zarządzanie bazą filmów, seriali oraz moderację recenzji.
## Uruchomienie lokalne (Windows)
Do prawidłowego działania aplikacji wymagany jest system z zainstalowanym językiem Python (wersja 3.10 lub nowsza).
1. Utworzenie i aktywacja środowiska wirtualnego:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
Instalacja wymaganych zależności:
PowerShell
pip install -r requirements.txt
Wykonanie migracji bazy danych:
PowerShell
python manage.py migrate
Utworzenie konta administratora (Superuser):
PowerShell
python manage.py createsuperuser
Uruchomienie serwera deweloperskiego:
PowerShell
python manage.py runserver
Panel zarządzania treścią jest dostępny pod adresem: http://127.0.0.1:8000/admin/. Filmy oraz seriale należy dodawać z poziomu tego panelu. Plik z bazą danych oraz hasła użytkowników nie są umieszczane w repozytorium GitHub ze względów bezpieczeństwa.
Struktura plików konfiguracyjnych (movies/)
models.py: Struktura bazy danych (model Production dla filmów/seriali, Review dla ocen użytkownika).
forms.py: Logika formularzy zabezpieczająca przesyłanie samych ocen i treści opinii.
views.py: Funkcje odpowiadające za przetwarzanie żądań i renderowanie odpowiednich szablonów.
urls.py: Routing i zarządzanie ścieżkami podstron.
admin.py: Konfiguracja uprawnień i widoczności modeli w panelu zarządzania.
tests.py: Zestaw testów jednostkowych sprawdzający poprawność logiki oraz autoryzacji.
Wdrożenie na serwerze produkcyjnym (PythonAnywhere)
Zalecana platforma hostingowa to PythonAnywhere. Poniżej znajduje się instrukcja wdrożenia aplikacji:
W konsoli Bash na serwerze (wersja Pythona musi być zgodna z wersją wybraną w ustawieniach aplikacji Web):
Bash
git clone [https://github.com/DanyloShymanskyi/Projekt.git](https://github.com/DanyloShymanskyi/Projekt.git)
cd Projekt
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
W zakładce Web skonfiguruj następujące ścieżki (zastąp LOGIN swoją nazwą użytkownika):
Source code: /home/LOGIN/Projekt
Working directory: /home/LOGIN/Projekt
Virtualenv: /home/LOGIN/Projekt/.venv
Static files: URL /static/, katalog /home/LOGIN/Projekt/staticfiles
Konfiguracja pliku WSGI (edytowanego bezpośrednio przez panel w zakładce Web):
Python
import os
import sys
sys.path.insert(0, '/home/LOGIN/Projekt')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DJANGO_DEBUG'] = '0'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'LOGIN.pythonanywhere.com'
# Klucz należy wygenerować w konsoli i wpisać poniżej (nie udostępniać na GitHubie):
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
os.environ['DJANGO_SECRET_KEY'] = 'TWÓJ_WYGENEROWANY_LOSOWY_KLUCZ'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
Po zapisaniu pliku przeładuj serwer za pomocą przycisku Reload. Aplikacja będzie w pełni operacyjna pod przypisanym adresem HTTPS.
