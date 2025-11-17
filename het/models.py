from hashlib import blake2b
from django.db import models
import uuid
from accounts.models import CustomUser   # link with your user table
from django.conf import settings
from base.models import BaseMonthlySpendingMoney
class Member(models.Model):
    GENDER_CHOICES = [
        ('male', 'ကျား'),
        ('female', 'မ'),
    ]
    RANK_CHOICES = [
        ('private', 'တပ်သား'),
        ('lance_corporal', 'ဒု-တပ်ကြပ်'),
        ('coporal', 'တပ်ကြပ်'),
        ('sergeant', 'တပ်ကြပ်ကြီး'),
        ('warrant_officer_class-2', 'ဒုအရာခံဗိုလ်'),
        ('warrant_officer_class-1', 'အရာခံဗိုလ်'),
        ('second Lieutenant', 'ဒုဗိုလ်'),
        ('lieutenant', 'ဗိုလ်'),
        ('captain', 'ဗိုလ်ကြီး'),
        ('major', 'ဗိုလ်မှူး'),
        ('colonel', 'ဗိုလ်မှူးကြီး'),
        ('general', 'ဗိုလ်ချုပ်'),

    ]
    DEPARTMENT_CHOICES = [
        ("SET", "Software Engineering Team"),
        ("HET", "Hardware Engineering Team"),
        ("TRAINING", "Training & Learning"),
    ]
    POSITION_CHOICES = [
        ("phone", "ဖုန်းပြုပြင်သူ"),
        ("computer", "ကွန်ပျူတာပြုပြင်သူ"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name="het_members", null=True, blank=True,
        help_text="If this member is linked to a user account"
    )
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES, editable=False, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    rank = models.CharField(max_length=50, choices=RANK_CHOICES, blank=True, null=True)
    full_name = models.CharField(max_length=150)
    reg_no = models.CharField(max_length=10, unique=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
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
        verbose_name = "HET Member"
        verbose_name_plural = "HET Members"
        ordering = ["-created_at"]
    def get_profile_photo_url(self):
        """Return actual file or fallback default"""
        if self.profile_photo and hasattr(self.profile_photo, "url"):
            return self.profile_photo.url
        from django.templatetags.static import static
        return static("profile/default-profile.png")




class HardwareRepair(models.Model):
    STATUS_CHOICES = [
        ("pending", "စောင့်ဆိုင်းဆဲ"),
        ("in_progress", "ပြုပြင်ဆဲ"),
        ("completed", "ပြီးစီး"),
        ("cancelled", "ပယ်ဖျက်ပယ်ဖျက်"),
    ]

    PRIORITY_CHOICES = [
        ("low", "နိမ့်"),
        ("medium", "အတန်အသင့်"),
        ("high", "အရေးကြီး"),
        ("urgent", "လုံးဝအရေးကြီး"),
    ]

    DEVICE_TYPE_CHOICES = [
        ("computer", "Computer / Laptop"),
        ("mobile", "Mobile Device"),
        ("printer", "Printer"),
        ("network", "Network Equipment"),
        ("sensor", "Sensor"),
        ("controller", "Controller Board"),
        ("other", "Other"),
    ]

    # ---------- Basic Info ----------
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    device_name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES, default="other")
    issue_description = models.TextField(help_text="Describe the problem in detail")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")

    # ---------- Assigned Staff ----------
    technician = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_repairs"
    )
    support_team = models.ManyToManyField(
        Member,
        blank=True,
        related_name="repair_tasks"
    )

    # ---------- Dates ----------
    received_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    estimated_completion = models.DateField(blank=True, null=True)

    # ---------- Attachments ----------
    photo_before = models.ImageField(upload_to="het/devices/before/", blank=True, null=True)
    photo_after = models.ImageField(upload_to="het/devices/after/", blank=True, null=True)
    report_document = models.FileField(upload_to="het/devices/reports/", blank=True, null=True)

    # ---------- Additional Info ----------
    repair_notes = models.TextField(blank=True, null=True)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_repairs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------- Helper ----------
    def __str__(self):
        return f"{self.device_name} ({self.ticket_id})"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            import uuid
            self.ticket_id = "HET-" + str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Hardware Repair"
        verbose_name_plural = "Hardware Repairs"

    def get_status_color(self):
        return {
            "pending": "bg-yellow-100 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-200",
            "in_progress": "bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200",
            "completed": "bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200",
            "cancelled": "bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200",
        }.get(self.status, "bg-slate-100 text-slate-800")



class HardwareSpendingMoney(BaseMonthlySpendingMoney):
   

    # ---------- File Upload ----------
    attachment = models.FileField(upload_to="het/requirements/docs/", blank=True, null=True)
    requested_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="het_requested_spending_money"
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="het_approved_spending_money"
    )
    # ---------- Helper ----------
    def total_cost(self):
        return (self.quantity or 0) * (self.estimated_cost or 0)

    def __str__(self):
        return f"{self.item_name} ({self.get_month_display()} {self.year})"
