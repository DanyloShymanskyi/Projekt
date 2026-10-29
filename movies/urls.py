from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('film/<int:pk>/', views.detail, name='detail'),
    path('film/<int:pk>/review/', views.add_review, name='add_review'),
    path('ranking/', views.ranking, name='ranking'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
]
