from django.shortcuts import render, redirect
from .forms import RoleSelectionForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from .forms import UserLoginForm

User = get_user_model()

def user_login(request):
    """
    Handle user login via email and password.

    This view processes the login form, authenticates the user using their email and password, 
    and logs them in if the credentials are valid. If authentication fails, an error message is displayed.

    Args:
        request (HttpRequest): The incoming HTTP request, which can include POST data.

    Returns:
        HttpResponse: A rendered login template on GET requests or failed login attempts.
        Redirect: A redirect to the index page upon successful login.
    """
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Username or password is incorrect")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    """
    Handle user logout.

    This view logs out the current authenticated user and redirects them to the index page.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        Redirect: A redirect to the index page after logout.
    """
    logout(request)
    return redirect('index')

def index(request):
    """
    Render the homepage.

    This view displays the main index page for the application.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: A rendered index template.
    """
    return render(request, 'index.html')

@login_required
def select_role(request):
    """
    Handle role selection for authenticated users.

    This view allows a logged-in user to select and change their active role using a form. 
    After successfully changing the role, the user is redirected to the index page.

    Args:
        request (HttpRequest): The incoming HTTP request, which may include POST data.

    Returns:
        HttpResponse: A rendered role selection form on GET requests or invalid form submissions.
        Redirect: A redirect to the index page upon successful role selection.
    """
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            selected_role = form.cleaned_data.get('role')
            request.user.active_role = selected_role
            request.user.save()

            messages.success(request, f'Your role has been changed to {selected_role}.')
            return redirect('index')
    else:
        form = RoleSelectionForm()

    return render(request, 'users/select_user.html', {'form': form})
