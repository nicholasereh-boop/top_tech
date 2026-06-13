from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import login_view, admin_dashboard, logout_view, custom_admin_view, signup_view, verify_email
from . import views
from .views import home, signup
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),
    path('home/', home, name='home'),           # ← Root URL
    path('signup/', signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path("branding/", views.branding, name="branding"),
    path("social/", views.social, name="social"),
    path("flyer/", views.flyer, name="flyer"),
    path("clothing/", views.clothing, name="clothing"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("shop/", views.shop, name="shop"),
    path('contact/', views.contact_admin, name='contact'),


    # ================= admin dashboard ==========
    path('custom_login/', login_view, name='custom_login'),
    path('custom_signup/', signup_view, name='custom_signup'),
    path('custom_admin/', custom_admin_view, name='custom_admin'),
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('custom_logout/', logout_view, name='custom_logout'),
     path(
        'verify-email/<uidb64>/<token>/',
        verify_email,
        name='verify_email'
    ),
]