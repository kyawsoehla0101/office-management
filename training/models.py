from django.db import models
from base.models import BaseMonthlySpendingMoney
from accounts.models import CustomUser   # link with your user table

import uuid

class Member(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    RANK_CHOICES = [
        ('citizen', 'Citizen'),
        ('private', 'Private'),
        ('lance_corporal', 'Lance Corporal'),
        ('coporal', 'Coporal'),
        ('sergeant', 'Sergeant'),
        ('warrant_officer_class-1', 'Warrant Officer Class - I'),
        ('warrant_officer_class-2', 'Warrant Officer Class - II'),
        ('second Lieutenant', 'Second Lieutenant'),
        ('lieutenant', 'Lieutenant'),
        ('captain', 'Captain'),
        ('major', 'Major'),
        ('colonel', 'Colonel'),
        ('general', 'General'),

    ]
    DEPARTMENT_CHOICES = [
        ("SET", "Software Engineering Team"),
        ("HET", "Hardware Engineering Team"),
        ("TRAINING", "Training & Learning"),
    ]
    POSITION_CHOICES = [
        ("developer", "Developer"),
        ("designer", "UI/UX Designer"),
        ("mobile_developer", "Mobile Developer"),
        ("server_admin", "Server Administrator"),
        ("tester", "Tester"),
        ("manager", "Project Manager"),
        ("intern", "Intern"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name="training_members", null=True, blank=True,
        help_text="If this member is linked to a user account"
    )
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES, editable=False, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    rank = models.CharField(max_length=50, choices=RANK_CHOICES, blank=True, null=True)
    full_name = models.CharField(max_length=150)
    reg_no = models.CharField(max_length=10, unique=True, blank=True, null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, blank=True, null=True)
    joined_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(blank=True, null=True)

    # Optional: project link (if SET has Projects model)
    # project = models.ForeignKey(
    #     "set.Project", on_delete=models.SET_NULL,
    #     null=True, blank=True, related_name="members"
    # )

    profile_photo = models.ImageField(
        upload_to="members/photos/", blank=True, null=True,
        help_text="Optional profile picture"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        """Auto set department if not manually specified"""
        if not self.department and self.user:
            self.department = self.user.role.upper()
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Training Member"
        verbose_name_plural = "Training Members"
        ordering = ["-created_at"]
    def get_profile_photo_url(self):
        """Return actual file or fallback default"""
        if self.profile_photo and hasattr(self.profile_photo, "url"):
            return self.profile_photo.url
        from django.templatetags.static import static
        return static("profile/default-profile.png")
# Create your models here.
class TrainingSpendingMoney(BaseMonthlySpendingMoney):

    # ---------- File Upload ----------
    attachment = models.FileField(upload_to="training/requirements/docs/", blank=True, null=True)
    requested_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="training_requested_spending_money"
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="training_approved_spending_money"
    )
    # ---------- Helper ----------
    class Meta:
        verbose_name = "Training Spending Money"
        verbose_name_plural = "Training Spending Money"
        ordering = ["year", "month"]
    @property
    def total_cost(self):
        return (self.quantity or 0) * (self.estimated_cost or 0)

    @total_cost.setter
    def total_cost(self, value):
        self._total_cost = value
    def __str__(self):
        return f"{self.item_name} ({self.get_month_display()} {self.year})"
