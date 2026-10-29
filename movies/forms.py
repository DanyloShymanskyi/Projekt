from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {'rating': forms.Select(choices=[(n, n) for n in range(1, 11)])}
