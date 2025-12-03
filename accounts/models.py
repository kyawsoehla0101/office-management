from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("set", "Software Engineering Team"),
        ("het", "Hardware Engineering Team"),
        ("training", "Training & Learning"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="‌admin")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_set(self):
        return self.role == "set"

    @property
    def is_het(self):
        return self.role == "het"

    @property
    def is_training(self):
        return self.role == "training"


# accounts/models.py

from django.db import models
from django.conf import settings

class OfficeDevice(models.Model):
    device_id = models.CharField(max_length=64, unique=True)  # cookie ထဲက ID
    label = models.CharField(max_length=100, blank=True, help_text="e.g. Kyaw Soe Hla Laptop")
    note = models.TextField(blank=True)
    is_allowed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    last_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="office_devices",
    )

    def __str__(self):
        status = "✅" if self.is_allowed else "❌"
        return f"{status} {self.label or self.device_id}"
