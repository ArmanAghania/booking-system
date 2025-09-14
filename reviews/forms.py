# reviews/forms.py

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'comment']

        widgets = {
            'rating': forms.RadioSelect(
                attrs={'class': 'hidden'},
                choices=[(i, str(i)) for i in range(1, 6)]
            ),
            'comment': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Share your experience with the doctor...'
                }
            ),
        }

        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review',
        }