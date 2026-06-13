from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignupForm, LoginForm, PasswordVerificationForm
from .models import UserProfile, ContactMessage
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse


# ====================== AUTHENTICATION ======================

def home(request):
    # If user is not logged in, send them to signup
    if not request.user.is_authenticated:
        return redirect('signup')

    return render(request, 'main/base.html')



def signup(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = SignupForm(request.POST)

        if form.is_valid():

            # Create User
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name']
            )

            # Create Profile
            profile = UserProfile.objects.create(
                user=user,
                other_names=form.cleaned_data['other_names'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                phone=form.cleaned_data['phone']
            )

            # Login user
            login(request, user)

            messages.success(
                request,
                "Account created successfully!"
            )

            return redirect('home')

    else:
        form = SignupForm()

    return render(
        request,
        'main/signup.html',
        {
            'form': form
        }
    )
# if user.is_staff or user.is_superuser:
#     return redirect('admin_dashboard')
# else:
#     return redirect('home')

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
    return render(request, 'main/login.html', {'form': form})

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


# def home(request):
#     return render(request, 'home')




def index(request):
    return render(request, "main/base.html", {})




# ====================== ADMIN DASHBOARD ======================



# Check if user is staff or superuser
def is_admin(user):
    return user.is_staff or user.is_superuser



def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_staff = True
            user.save()

            send_verification_email(request, user)
            messages.success(request, "Account created! Please check your email to verify.")
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'admin/custom_signup.html', {'form': form})



def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )

    subject = "Verify Your Admin Account"
    message = render_to_string('admin/email_verification.html', {
        'user': user,
        'verification_link': verification_link,
    })

    send_mail(subject, message, None, [user.email], fail_silently=False)




def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verified successfully! You can now login.")
        return redirect('login')
    else:
        messages.error(request, "Verification link is invalid or has expired.")
        return redirect('signup')




# =========================
# LOGIN VIEW
# =========================
def login_view(request):

    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(
                    request,
                    'You do not have permission to access this dashboard.'
                )

        else:
            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(request, 'admin/custom_login.html')


# =========================
# ADMIN DASHBOARD
# =========================
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):

    total_users = User.objects.count()

    context = {
        'title': 'Admin Dashboard',
        'total_users': total_users,
        'total_orders': 342,
        'revenue': 45890,
    }

    return render(
        request,
        'admin/custom_admin.html',
        context
    )


def custom_admin_view(request):
    total_users = User.objects.count()

    context = {
        'title': 'Admin Dashboard',
        'total_users': total_users,
        'total_orders': 342,
        'revenue': 45890,
    }

    return render(
        request,
        'admin/custom_admin.html',
        context
    )

    


# =========================
# LOGOUT VIEW
# =========================
def logout_view(request):
    logout(request)
    return render(
        request,
        'admin/custom_logout.html'
    )

def admin_panel(request):
    if not request.user.is_authenticated:
        return redirect('custom_login')

    return render(request, 'admin/custom_admin.html')




# ====================== SHOP & PAYMENT ======================
def shop(request):
    products = Product.objects.all()
    return render(request, 'main/shop.html', {'products': products})

# ====================== OTHER PAGES ======================

def branding(request):
    return render(request, "main/branding.html", {})


def social(request):
    return render(request, "main/social.html", {})


def flyer(request):
    return render(request, "main/flyer.html", {})


def clothing(request):
    return render(request, "main/clothing.html", {})


def portfolio(request):
    return render(request, "main/portfolio.html", {})

def contact_admin(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Validation
        if len(name) < 3:
            messages.error(request, "Name must be at least 3 characters.")
            return render(request, 'main/contact.html', {})

        if len(message_text) < 20:
            messages.error(request, "Message must be at least 20 characters.")
            return render(request, 'main/contact.html', {})

        try:
            # Save message to database
            contact_msg = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )

            # Send Email Notification to Admin
            admin_email = 'nicholasereh@gmailcom'   # ← Change this to your real email

            send_mail(
                subject=f"New Contact Message: {subject}",
                message=f"""
You have received a new message from your website!

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message_text}

View in Admin Panel: http://127.0.0.1:8000/admin/
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )

            messages.success(request, "✅ Your message has been sent successfully! Nicholas will reply soon.")
            return redirect('contact')

        except Exception as e:
            messages.error(request, "Failed to send message. Please try again later.")

    return render(request, 'main/contact.html', {})



