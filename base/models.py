# adminpanel/models.py
from django.db import models
import uuid
from accounts.models import CustomUser   # link with your user table

class SystemSettings(models.Model):
    system_name = models.CharField(max_length=100, default="Engineering Management Dashboard")
    organization = models.CharField(max_length=100, default="Software Engineering Team II")


    email_notifications = models.BooleanField(default=True)
    system_warnings = models.BooleanField(default=True)
    weekly_reports = models.BooleanField(default=False)

    session_timeout = models.PositiveIntegerField(default=30)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.system_name} Settings"


from django.db import models
from django.conf import settings

class BaseMonthlySpendingMoney(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    DEPARTMENT_CHOICES = [
        ("office", "Office"),
        ("set", "Software Engineering Team"),
        ("het", "Hardware Engineering Team"),
        ("training", "Training School"),
    ]

    MONTH_CHOICES = [
        ("01", "ဇန်နဝါရီလ"), ("02", "ဖေဖော်ဝါရီလရီလ"), ("03", "မတ်ချ်လ"),
        ("04", "ဧပြီလ"), ("05", "မေလ"), ("06", "ဂျုန်လလ"),
        ("07", "ဂျူလိုင်လ"), ("08", "သြဂတ်စ်လ"), ("09", "စပ်တမ်ဘာလ"),
        ("10", "အောက်တိုဘာလ"), ("11", "နိုဗမ်ဘာလ"), ("12", "ဒီဇင်ဘာလ"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=2, choices=MONTH_CHOICES)
    year = models.IntegerField(default=2025)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unit = models.CharField(max_length=50, default="pcs", help_text="e.g. pcs, box, meter, etc.")
    
    
    def total_cost(self):
        return self.quantity * self.estimated_cost

    class Meta:
        abstract = True

class SpendingMoney(BaseMonthlySpendingMoney):
   

    # ---------- File Upload ----------
    attachment = models.FileField(upload_to="spending_money/docs/", blank=True, null=True)
    
    @property

    def total_cost(self):
        return (self.quantity or 0) * (self.estimated_cost or 0)

    def __str__(self):
        return f"{self.item_name} ({self.get_month_display()} {self.year})"
