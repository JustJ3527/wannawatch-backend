from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import customUser



class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
            "data-valid": "false",
        })
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password",
            "data-valid": "false",
        })
    )

    class Meta:
        model = customUser
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username",
                "data-valid": "false",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "E-mail",
                "data-valid": "false",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Supprime tout autofocus automatique
        for field in self.fields.values():
            field.widget.attrs.pop("autofocus", None)

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "E-mail"
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password"
        })
    )

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = customUser
        fields = ["avatar", "username", "bio", "banner"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }