from django import forms

from posts.models import Post


class PostCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        is_comment = kwargs.pop('is_comment', False)
        super().__init__(*args, **kwargs)

        if is_comment:
            self.fields['title'].required = False

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

    post_ref = forms.CharField(
        required=False,
        label="Post Ref",
    )

    body = forms.CharField(
        required=True,
        label="Body",
        min_length=3,
        max_length=1000,
        # Add validators?
    )
    
    class Meta:
        model = Post
        fields = ("title", "body", "topics", "post_ref")
        widgets = {
            'topics': forms.CheckboxSelectMultiple,
        }