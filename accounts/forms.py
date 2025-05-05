from config import Config
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import Course, CustomUser, Interest, UserSettings, UserType


# User Creation Form
#
#
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        label="Username",
        min_length=3,
        max_length=30,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9._]*$",
                "Username can only contain letters, numbers, dots and underscores.",
            )
        ],
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Choose a unique username",
            }
        ),
    )

    first_name = forms.CharField(
        required=True,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Your first name",
            }
        ),
    )

    last_name = forms.CharField(
        required=True,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Your last name",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "student@live.uwe.ac.uk",
            }
        ),
    )

    student_id = forms.CharField(
        required=True,
        label="Student ID",
        max_length=8,
        validators=[
            RegexValidator(r"^[0-9]{8}$", "Student ID must be exactly 8 digits.")
        ],
        widget=forms.TextInput(
            attrs={"class": "input input-bordered w-full", "placeholder": "12345678"}
        ),
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
        empty_label="Select a course",
    )

    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "interests-checkbox hidden"}
        ),
        help_text="Select your interests",
    )

    address_line1 = forms.CharField(
        required=True,
        label="Address Line 1",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Street address",
            }
        ),
    )

    address_line2 = forms.CharField(
        required=False,
        label="Address Line 2",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Apartment, suite, etc. (optional)",
            }
        ),
    )

    city = forms.CharField(
        required=True,
        label="City",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "City",
            }
        ),
    )

    county = forms.CharField(
        required=False,
        label="County",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "County (optional)",
            }
        ),
    )

    postcode = forms.CharField(
        required=True,
        label="Postcode",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Postcode",
            }
        ),
    )

    is_staff_member = forms.BooleanField(
        required=False,
        label="I\'m an Academic Staff Member",
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Create a strong password",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Repeat your password",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "student_id",
            "course",
            "interests",
            "address_line1",
            "address_line2",
            "city",
            "county",
            "postcode",
            "is_staff_member",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and not email.endswith(f'@{Config.config["email_domain"]}'):
            raise forms.ValidationError("Please use your UWE student email address.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_student_id(self):
        student_id = self.cleaned_data.get("student_id")
        if CustomUser.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("This Student ID is already registered.")
        return student_id

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "The passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        is_staff = self.cleaned_data.get("is_staff_member", False)

        # Set user type based on staff status
        user_type = None
        if is_staff:
            user_type = UserType.objects.get_or_create(name="ACADEMIC")[0]
        else:
            user_type = UserType.objects.get_or_create(name="STUDENT")[0]

        user.user_type = user_type

        if commit:
            user.save()
        return user


# User Login Form
#
#
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full"}),
    )

    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={"class": "input input-bordered w-full"}),
    )


# Edit User Profile
#
#
class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "student@live.uwe.ac.uk",
            }
        ),
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
        empty_label="Select a course",
    )

    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "interests-checkbox hidden"}
        ),
        help_text="Select your interests",
    )

    profile_picture = forms.FileField(
        label="Profile Picture",
        widget=forms.FileInput(
            attrs={"class": "file-input file-input-bordered w-full"}
        ),
        required=False,
    )

    address_line1 = forms.CharField(
        required=True,
        label="Address Line 1",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Street address",
            }
        ),
    )

    address_line2 = forms.CharField(
        required=False,
        label="Address Line 2",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Apartment, suite, etc. (optional)",
            }
        ),
    )

    city = forms.CharField(
        required=True,
        label="City",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "City",
            }
        ),
    )

    county = forms.CharField(
        required=False,
        label="County",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "County (optional)",
            }
        ),
    )

    postcode = forms.CharField(
        required=True,
        label="Postcode",
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Postcode",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "bio",
            "profile_picture",
            "course",
            "interests",
            "address_line1",
            "address_line2",
            "city",
            "county",
            "postcode",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"class": "input input-bordered w-full"}),
            "bio": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 4}
            ),
            "profile_picture": forms.FileInput(
                attrs={"class": "file-input file-input-bordered w-full"}
            ),
        }


# Edit User Settings
#
#
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ["like_notifications", "comment_notifications", "follow_notifications"]
        widgets = {
            "like_notifications": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-primary"}
            ),
            "comment_notifications": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-primary"}
            ),
            "follow_notifications": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-primary"}
            ),
        }

