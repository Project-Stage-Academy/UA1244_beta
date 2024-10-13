from django import forms
from .models import Role
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    """
    Form for user login with email and password.

    Inherits from Django's `AuthenticationForm` but replaces the `username` field with an `EmailField` 
    to allow users to log in using their email.

    Fields:
    - `username`: An email field for the user's email address.
    - `password`: A password input field for the user's password.
    """
    username = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class RoleSelectionForm(forms.Form):
    """
    Form for selecting a role from the available roles.

    This form allows the user to choose a role from the `Role` model.
    The `role` field is a `ModelChoiceField` which displays the list of available roles to choose from.

    Fields:
    - `role`: A `ModelChoiceField` that queries all roles from the `Role` model. The field is rendered 
      as a dropdown with an option to select a role.
    """
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        empty_label="Select Role", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
