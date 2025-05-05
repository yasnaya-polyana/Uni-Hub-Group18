from django import forms
from django.utils.safestring import mark_safe

from .models import Communities, CommunityMember, Topic
from events.models import Event


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Custom checkbox widget that applies class to each checkbox input"""
    
    def __init__(self, attrs=None, check_test=None):
        attrs = attrs or {}
        attrs['class'] = 'checkbox checkbox-primary topics-checkbox'
        super().__init__(attrs, check_test)
        
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        if 'class' not in attrs:
            attrs['class'] = 'checkbox checkbox-primary topics-checkbox'
        else:
            attrs['class'] += ' checkbox checkbox-primary topics-checkbox'
        
        return super().render(name, value, attrs, renderer)
        
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        attrs = attrs or {}
        attrs['class'] = 'checkbox checkbox-primary topics-checkbox'
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        return option


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'details', 'start_at', 'end_at', 'members_only']
        
    location = forms.CharField(label="location", max_length=100)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user:
            instance.owner = self.user
        if commit:
            instance.save()
            CommunityMember.objects.create(
                user=self.user, community=instance, role="admin"
            )
        return instance


class ApproveRejectCommunityForm(forms.Form):
    DECISION_CHOICES = [
        ("approve", "Approve"),
        ("reject", "Reject"),
    ]

    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "radio radio-primary"}),
        required=True,
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "textarea textarea-bordered w-full", "rows": 3}
        ),
    )


class CreateCommunityForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all().order_by('name'),
        widget=CustomCheckboxSelectMultiple(),
        required=False,
        label="Topics"
    )

    class Meta:
        model = Communities
        fields = ['name', 'description', 'icon_url', 'category', 'colour', 'topics']
        exclude = ['banner_url']
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "description": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 4}
            ),
            "icon_url": forms.FileInput(
                attrs={"class": "file-input input-bordered w-full"}
            ),
            "category": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "colour": forms.TextInput(attrs={'type': 'color', 'class': 'w-full'}),
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
            self.save_m2m()  # Save topics relationship
            CommunityMember.objects.create(
                user=self.user, community=instance, role="admin"
            )
        return instance


class EditCommunityForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all().order_by('name'),
        widget=CustomCheckboxSelectMultiple(),
        required=False,
        label="Topics"
    )

    class Meta:
        model = Communities
        exclude = ['pkid', 'id', 'owner', 'members', 'created_at', 'updated_at', 'status']
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "description": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 4}
            ),
            "icon_url": forms.FileInput(
                attrs={"class": "file-input input-bordered file-input-md w-full"}
            ),
            "category": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "colour": forms.TextInput(attrs={'type': 'color', 'class': 'w-full'}),
        }
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            if 'topics' in self.cleaned_data:
                instance.topics.set(self.cleaned_data['topics'])
                
        return instance


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

