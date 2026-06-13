import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from core.models import TimeStampedModel


class UserManager(BaseUserManager):
    def _set_username(self, extra_fields, phone_number=None):
        if "username" not in extra_fields or not extra_fields["username"]:
            extra_fields["username"] = (
                extra_fields.get("email") or phone_number or f"user-{uuid.uuid4().hex[:12]}"
            )
        return extra_fields

    def create_user(self, phone_number=None, password=None, **extra_fields):
        if not phone_number:
            phone_number = f"sys-{uuid.uuid4().hex[:12]}"
        extra_fields = self._set_username(extra_fields, phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")
        if not phone_number:
            phone_number = f"admin-{uuid.uuid4().hex[:12]}"
        extra_fields["username"] = extra_fields.get("email") or phone_number
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    ROLE_CHOICES = [
        ("resident", "Resident"),
        ("coordinator", "Coordinator"),
        ("government", "Government"),
        ("admin", "Admin"),
    ]
    phone_number = models.CharField(max_length=20, unique=True, primary_key=True)
    email = models.EmailField(null=True, blank=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="resident")
    household_size = models.PositiveIntegerField(null=True, blank=True)
    medical_needs = models.TextField(blank=True)
    hub = models.ForeignKey(
        "hubs.Hub", on_delete=models.SET_NULL, null=True, blank=True, related_name="residents"
    )
    secondary_hub = models.ForeignKey(
        "hubs.Hub",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_residents",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    biometric_key = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_invite_accepted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
