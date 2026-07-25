from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMultiAlternatives

from .forms import LoginForm, RegisterForm
from .models import UserProfile
from .tokens import email_verification_token

User = get_user_model()




def _send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = request.build_absolute_uri(
        f"/accounts/verify-email/{uid}/{token}/"
    )

    subject = "Verify your TopTech account"

    context = {
        "user": user,
        "verify_url": verify_url,
    }

    text_content = render_to_string(
        "accounts/verification_email.txt",
        context,
    )

    html_content = render_to_string(
        "accounts/verification_email.html",
        context,
    )

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # Store email as username if your project uses email login
            user.username = user.email

            # User must verify email before login
            user.is_active = False
            user.save()

            UserProfile.objects.get_or_create(user=user)

            _send_verification_email(request, user)

            messages.success(
                request,
                "Your account has been created successfully. "
                "Please check your email and click the verification link before logging in."
            )

            return redirect("accounts:login")

    else:
        form = RegisterForm()

    return render(request, "accounts/signup.html", {"form": form})



# def verify_email(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and email_verification_token.check_token(user, token):
#         user.is_active = True
#         user.save(update_fields=['is_active'])
#         messages.success(request, "Email verified! You can now log in.")
#     else:
#         messages.error(request, "Verification link is invalid or has expired.")

#     return redirect('accounts:login')


def login_view(request):
    """Customer login. Replaces the old monolith's user_login() view."""

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')

            # authenticate() also returns None for correct credentials on
            # an inactive (unverified) account - check for that case
            # separately so the message is actually helpful.
            existing = User.objects.filter(username=username).first()
            if existing is not None and not existing.is_active and existing.check_password(password):
                messages.error(request, "Please verify your email before logging in.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Replaces the old monolith's user_logout() view."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:logout')



@login_required(login_url="accounts:login")
def user_dashboard(request):
    """
    Customer dashboard.
    """

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    context = {
        "user": request.user,
        "profile": profile,
    }

    return render(request,"users/user_dashboard.html",context,)



# @login_required
# def user_logout(request):
#     """
#     Display logout confirmation page.
#     Logout only when user confirms.
#     """
#     if request.method == "POST":
#         logout(request)
#         return redirect("home")   # Change 'home' to your homepage URL name

#     return render(request, "accounts/logout.html")