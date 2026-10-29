from django.contrib import admin
from .models import Production, Review


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ['title', 'kind', 'genre', 'year']
    list_filter = ['kind', 'genre']
    search_fields = ['title']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['production', 'user', 'rating', 'created']
    list_filter = ['rating']
    search_fields = ['production__title', 'user__username', 'text']
