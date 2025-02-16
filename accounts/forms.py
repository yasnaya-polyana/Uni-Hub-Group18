from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import CustomUser, Course

# User Creation Form
#
#
class CustomUserCreationForm(UserCreationForm):
    # Specify Field Attributes and Form Styling
    #
    first_name = forms.CharField(
        required=True,
        label='First Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'John'
        })
    )
    last_name = forms.CharField(
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Doe'
        })
    )
    username = forms.CharField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Get creative...'
        })
    )

    # Student ID Validation
    # Regex for numbers only
    student_id = forms.CharField(
        required=True,
        label="Student ID",
        max_length=8,
        validators=[RegexValidator(r'^[0-9]*$', 'Only numbers are allowed.')],
        widget=forms.TextInput(attrs={
            'placeholder': 'XXXXXXXX'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'student@live.uwe.ac.uk'
        })
    )

    password2 = forms.CharField(
        label="Confirm Password"
    )
    
    class Meta:
        model = CustomUser

        # All fields which are shown upon sign-up
        #
        fields = ('username', 'email', 'first_name', 'last_name', 'student_id', 'password1', 'password2')
        
    # Initialise all forms with default CSS styling
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'input input-bordered w-full'

# User Login Form
#
#
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )

    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full'})
    )

# Edit User Profile
#
#
class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'student@live.uwe.ac.uk'
        })
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            "class": "select select-bordered w-full"
        }),
        empty_label=None
    )

    profile_picture = forms.FileField(
        label="Profile Picture",
        widget=forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'})
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'bio', 'profile_picture', 'course')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
            'bio': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'})
        } 