# reviews/forms.py

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    # Explicitly define the rating field to ensure it has choices from 1 to 5
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect, # This will be hidden by our star UI
        label="Your Rating",
        required=True
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment', 'is_anonymous']
        labels = {
            'comment': 'Your Review (Optional)',
            'is_anonymous': 'Submit my review anonymously'
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }