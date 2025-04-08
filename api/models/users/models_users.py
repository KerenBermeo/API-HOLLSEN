from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # Sobrescribimos el modelo de usuario por defecto
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    
    # Autenticación
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    # Seguridad
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expires = models.DateTimeField(blank=True, null=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    
    # GDPR
    accepted_terms_at = models.DateTimeField(blank=True, null=True)
    marketing_opt_in = models.BooleanField(default=False)
    
    # Campos adicionales para evitar conflictos con auth.User
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",
        related_query_name="user",
    )

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email'], name='idx_email'),
            models.Index(fields=['is_active'], name='idx_active_users'),
        ]

    def __str__(self):
        return self.email