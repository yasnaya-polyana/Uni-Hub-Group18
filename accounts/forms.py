from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input input-bordered w-full'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'input input-bordered w-full'

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full'}))

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'bio', 'profile_picture')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
            'bio': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'})
        } 