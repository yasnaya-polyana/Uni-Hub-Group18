from django import forms

from .models import Communities, CommunityMember, Topic


class CreateCommunityForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Communities
        fields = ['name', 'description', 'banner_url', 'icon_url', 'category']
        widgets = {
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
            CommunityMember.objects.create(user=self.user, community=instance, role="admin")
        return instance

class EditCommunityForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Communities
        exclude = ['pkid', 'id', 'owner', 'members', 'created_at', 'updated_at']
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "description": forms.Textarea(attrs={"class": "textarea textarea-bordered w-full", "rows": 4}),
            "banner_url": forms.FileInput(attrs={"class": "file-input file-input-bordered w-full"}),
            "icon_url": forms.FileInput(attrs={"class": "file-input file-input-bordered w-full"}),
        }

class JoinCommunityForm(forms.ModelForm):
    class Meta:
        model = CommunityMember
        fields = []

class RequestMemberForm(forms.ModelForm):
    class Meta:
        model = CommunityMember
        fields = []

class RequestModForm(forms.ModelForm):
    class Meta:
        model = CommunityMember
        fields = []