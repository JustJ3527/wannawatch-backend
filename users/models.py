from multiprocessing import Value
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

from django.utils import timezone

from .utils import get_avatar_upload_path, get_banner_upload_path, delete_old_file

class customUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required.")
        if not username:
            raise ValueError("Username required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class customUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    username = models.CharField(max_length=50, unique=True, verbose_name=_("Username"))
    bio = models.TextField(max_length=500, blank=True, verbose_name=_("Biography"))

    avatar = models.ImageField(upload_to=get_avatar_upload_path, null=True, blank=True, verbose_name=_("Avatar"))
    banner = models.ImageField(upload_to=get_banner_upload_path, null=True, blank=True, verbose_name=_("Banner"))


    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = customUserManager()
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        if self.pk:
            delete_old_file(self, "avatar")
        
        super().save(*args, **kwargs)
    