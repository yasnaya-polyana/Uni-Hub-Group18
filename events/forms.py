from django import forms


class EventCreationForm(forms.Form):
    title = forms.CharField(
        required=True,
        label="Title",
        min_length=3,
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
            }
        ),
    )

    body = forms.CharField(
        required=True,
        label="Body",
        min_length=3,
        max_length=1000,
        # Add validators?
    )

    location = forms.CharField(
        required=True,
        label="Location",
        min_length=3,
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
            }
        ),
    )

    start_at = forms.DateTimeField(
        required=True,
        label="Start Time",
        widget=forms.TextInput(
            attrs={"class": "input input-bordered w-full", "type": "datetime-local"}
        ),
        # Add validators?
    )

    end_at = forms.DateTimeField(
        required=True,
        label="Start Time",
        widget=forms.TextInput(
            attrs={"class": "input input-bordered w-full", "type": "datetime-local"}
        ),
        # Add validators?
    )
