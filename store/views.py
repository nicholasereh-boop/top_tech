# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm, PasswordVerificationForm

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect('home')  # Change 'home' to your dashboard/home URL name
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def password_verify(request):
    """Simple password verification page (e.g., before sensitive actions)"""
    if request.method == 'POST':
        form = PasswordVerificationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if request.user.check_password(password):
                messages.success(request, "Password verified successfully!")
                return redirect('home')  # Or wherever you want to go after verification
            else:
                messages.error(request, "Incorrect password.")
    else:
        form = PasswordVerificationForm()
    return render(request, 'password_verify.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


def home(request):
    return render(request, 'home.html')