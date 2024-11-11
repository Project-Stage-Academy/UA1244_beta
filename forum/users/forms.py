# """
# forms.py

# This module defines forms for user authentication and role selection within the application. 

# It includes:
# - UserLoginForm: A form for user login that extends Django's AuthenticationForm.
# - RoleSelectionForm: A form for selecting a role from the available roles in the system.
# """

# from django import forms
# from django.contrib.auth.forms import AuthenticationForm
# from .models import Role


# class UserLoginForm(AuthenticationForm):
#     """
#     A form for user login, inheriting from Django's built-in AuthenticationForm.
#     It customizes the username and password fields to enhance user experience 
#     with placeholders and additional HTML attributes.
#     """
#     username = forms.EmailField(
#         label="Email",
#         widget=forms.EmailInput(attrs={
#             'placeholder': 'Enter your email address',
#             'class': 'form-control'
#         })
#     )
    
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'autocomplete': 'off',
#             'placeholder': 'Enter your password'
#         }),
#         label="Password"
#     )


# class RoleSelectionForm(forms.Form):
#     """
#     A form for selecting a role from the available roles in the system.
#     If no roles are available, the dropdown is disabled and a help text message 
#     is displayed to notify the user.
#     """
#     role = forms.ModelChoiceField(
#         queryset=Role.objects.all(),
#         empty_label="Select Role",
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         required=False
#     )

#     def __init__(self, *args, **kwargs):
#         """
#         Initializes the RoleSelectionForm. If no roles are available in the system, 
#         it disables the role selection dropdown and adds a help text to inform the user.
#         """
#         super().__init__(*args, **kwargs)
#         if not Role.objects.exists():
#             self.fields['role'].widget.attrs['disabled'] = 'disabled'
#             self.fields['role'].help_text = "No roles available. Please contact support."
