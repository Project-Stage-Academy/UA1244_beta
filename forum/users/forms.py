from django import forms
from .models import Role
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

class RoleSelectionForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        empty_label="Select Role", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )