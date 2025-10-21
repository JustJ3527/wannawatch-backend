from atexit import register
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Authentification JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # Gestion utilisateur
    # path('register/', RegisterView.as_view(), name='register'),
    # path('profile/', UserProfileView.as_view(), name='profile'),
    # path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name= 'login'),
    path("logout/", views.logout_view, name="logout"),
    path('profile/', views.profile_view, name='profile'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("home/", views.home_view, name="home"),

    path("profile/validate-username/", views.validate_username, name="validate_username"),
]