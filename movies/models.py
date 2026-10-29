from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Q


class Production(models.Model):
    title = models.CharField('tytuł', max_length=200)
    description = models.TextField('opis')
    kind = models.CharField('typ', max_length=10, choices=[('film', 'Film'), ('serial', 'Serial')])
    genre = models.CharField('gatunek', max_length=100)
    year = models.PositiveIntegerField('rok', validators=[MinValueValidator(1888)])
    poster = models.URLField('link do plakatu', blank=True)

    def __str__(self):
        return self.title

    def average(self):
        return self.reviews.aggregate(result=Avg('rating'))['result']


class Review(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField('ocena', validators=[MinValueValidator(1), MaxValueValidator(10)])
    text = models.TextField('opinia', blank=True, max_length=5000)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created', '-id']
        constraints = [
            models.UniqueConstraint(fields=['production', 'user'], name='one_review_per_user'),
            models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=10), name='rating_from_1_to_10'),
        ]

    def __str__(self):
        return f'{self.user} - {self.production}: {self.rating}'
