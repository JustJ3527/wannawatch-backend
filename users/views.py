
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, login_not_required
from django.template.loader import render_to_string

from django.utils.translation import gettext_lazy as _


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm, CustomLoginForm, ProfileEditForm
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer



User = get_user_model()

# ========================================
# WEBSITE
#========================================

@login_not_required
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})

@login_not_required
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("profile")

    else:
        form = CustomLoginForm()
    return render(request, "users/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")

def home_view(request):
    if request.user:
        user = request.user
        return render(request, "users/home.html", {"user": user})
    return redirect("home")


def validate_username(request):
    username = request.GET.get("username", "").strip()
    valid = True
    message = ""

    if not username:
        valid = False
        message = _("Username cannot be empty.")
    elif len(username) < 3:
        valid = False
        message = _("Username too short (min 3 characters).")
    elif User.objects.filter(username__iexact=username).exclude(pk=request.user.pk).exists():
        valid = False
        message = _("This username is already taken.")
    else:
        message = _("This username is available!")

    html = render_to_string("users/partials/username_feedback.html", {
        "valid": valid,
        "message": message,
    })
    return HttpResponse(html)


@login_required
def profile_view(request):
    user = request.user

    if request.headers.get("HX-Request"):
        html = render_to_string("users/partials/profile_static.html", {"user": user})
        return HttpResponse(html)

    return render(request, "users/profile.html", {"user": user})

@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                html = render_to_string("user/partials/profile_static.html", {"user": user})
                return HttpResponse(html)
            return redirect("profile")
    else:
        form = ProfileEditForm(instance=user)
    
    if request.headers.get("HX-Request"):
            html = render_to_string("users/partials/profile_edit.html", {"form": form, "user": user})
            return HttpResponse(html)

    return render(request, "users/profile.html", {"form": form, "user": user, "edit": True})

# ========================================
# USER SETTINGS
# ========================================


# ========================================
# API
# ========================================
class RegisterView(generics.CreateAPIView):
    """
    Vue pour l'inscription d'un nouvel utilisateur
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Compte créé avec succès'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue pour récupérer et mettre à jour le profil utilisateur
    GET/PUT /api/auth/profile/
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        user = self.request.user
        print(f"🔍 Profile request for user: {user}")
        return user
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print(f"📤 Profile data: {serializer.data}")
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    Vue pour changer le mot de passe
    POST /api/auth/change-password/
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'message': 'Mot de passe modifié avec succès'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Vue pour se déconnecter (blacklister le refresh token)
    POST /api/auth/logout/
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message': 'Déconnexion réussie'
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                'error': 'Token invalide'
            }, status=status.HTTP_400_BAD_REQUEST)