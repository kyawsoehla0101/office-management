from hashlib import blake2b
from django.db import models
import uuid
from accounts.models import CustomUser   # link with your user table
from base.models import BaseMonthlySpendingMoney
from django.utils import timezone

class Member(models.Model):
    GENDER_CHOICES = [
        ('male', 'ကျား'),
        ('female', 'မ'),
    ]
    RANK_CHOICES = [
        ('private', 'တပ်သား'),
        ('lance_corporal', 'ဒုတပ်ကြပ်'),
        ('coporal', 'တပ်ကြပ်'),
        ('sergeant', 'တပ်ကြပ်ကြီး'),
        ('warrant_officer_class-2', 'ဒု-အရာခံဗိုလ်'),
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
        related_name="set_members", null=True, blank=True,
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
        verbose_name = "SET Member"
        verbose_name_plural = "SET Members"
        ordering = ["-created_at"]
    def get_profile_photo_url(self):
        """Return actual file or fallback default"""
        if self.profile_photo and hasattr(self.profile_photo, "url"):
            return self.profile_photo.url
        from django.templatetags.static import static
        return static("profile/default-profile.png")


class Project(models.Model):
    STATUS_CHOICES = [
        ("PLANNING", "အစီအစိုင်ဆွဲနိန်"),
        ("ONGOING", "လုပ်နိန်ဆဲ"),
        ("COMPLETED", "ပြီးစီး"),
        ("ONHOLD", "ရပ်တန့်"),
        ("CANCELLED", "ပယ်ဖျက်"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "နိမ့်"),
        ("MEDIUM", "အလယ်အလတ်"),
        ("HIGH", "မြင့်"),
    ]

    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # Relationships
    team_lead = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_projects"
    )
    members = models.ManyToManyField(
        Member,
        blank=True,
        related_name="member_projects",
        help_text="Select members working on this project"
    )

    # Status & Dates
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLANNING")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    start_date = models.DateField()
    deadline = models.DateField(blank=True, null=True)
    # progress = models.IntegerField(default=0, help_text="Project progress percentage (0-100)")
    progress = models.PositiveIntegerField(default=0, editable=False, blank=True, null=True)
    project_document = models.FileField(
        upload_to="set/projects/docs/", blank=True, null=True,
        help_text="Optional project document"
    )
    # Meta info
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="created_projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def total_members(self):
        return self.members.count()
    members_list = property(lambda self: self.members.all())
    full_members_list = property(lambda self: [member.full_name for member in self.members_list])
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    def get_status_display(self):
        return dict([(value, key) for key, value in self.STATUS_CHOICES]).get(self.status, self.status.title())

    @property
    def progress(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(status="DONE").count()
        return int((done / total) * 100)


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Completed"),
    ]

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="tasks"
    )
    

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        Member, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SoftwareSpendingMoney(BaseMonthlySpendingMoney):
   

    # ---------- File Upload ----------
    attachment = models.FileField(upload_to="set/requirements/docs/", blank=True, null=True)
    requested_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="set_requested_spending_money"
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="set_approved_spending_money"
    )
    # ---------- Helper ----------
    @property
    def total_cost(self):
        return (self.quantity or 0) * (self.estimated_cost or 0)

    @total_cost.setter
    def total_cost(self, value):
        self._total_cost = value
    def __str__(self):
        return f"{self.item_name} ({self.get_month_display()} {self.year})"



class SoftwareActivity(models.Model):
    ACTIVITY_TYPES = [
        ("commit", "Commit"),
        ("issue", "Issue"),
        ("project", "Project Update"),
        ("developer", "Developer Update"),
    ]

    message = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="software_activities"
    )

    def __str__(self):
        return f"{self.type}: {self.message[:30]}"