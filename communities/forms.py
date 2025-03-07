from django import forms

from .models import Communities, CommunityMember


class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Communities
        fields = ("id", "name", "description", "banner_url", "icon_url")
        widgets = {
            "id": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "description": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 4}
            ),
            "banner_url": forms.FileInput(
                attrs={"class": "file-input file-input-bordered w-full"}
            ),
            "icon_url": forms.FileInput(
                attrs={"class": "file-input file-input-bordered w-full"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user:
            instance.owner = self.user
        if commit:
            instance.save()
            instance.members.add(self.user)
        return instance


class JoinCommunityForm(forms.ModelForm):
    class Meta:
        model = CommunityMember
        fields = []

