from django import forms
from .models import Event

class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['location', 'start_at', 'end_at', 'title', 'details', 'members_only']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'start_at': forms.DateTimeInput(attrs={'class': 'input input-bordered w-full', 'type': 'datetime-local'}),
            'end_at': forms.DateTimeInput(attrs={'class': 'input input-bordered w-full', 'type': 'datetime-local'}),
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
        }