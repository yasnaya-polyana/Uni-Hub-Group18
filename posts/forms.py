from django import forms

from posts.models import Post


class PostCreationForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        label="Title",
        min_length=3,
        max_length=60,
        # validators=[
        #     RegexValidator(
        #         r"^[a-zA-Z0-9._]*$",
        #         "Username can only contain letters, numbers, dots and underscores.",
        #     )
        # ],
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Title",
            }
        ),
    )

    body = forms.CharField(
        required=True,
        label="Body",
        min_length=3,
        max_length=60,
        # validators=[
        #     RegexValidator(
        #         r"^[a-zA-Z0-9._]*$",
        #         "Username can only contain letters, numbers, dots and underscores.",
        #     )
        # ],
        widget=forms.Textarea(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Body",
            }
        ),
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "body",
        )
