from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from accounts.utils.decorators import role_required
from accounts.models import CustomUser
from base.models import SpendingMoney, SystemSettings
from set.models import SoftwareSpendingMoney
from het.models import HardwareSpendingMoney
from training.models import TrainingSpendingMoney
from django.http import HttpResponse
import calendar
from set.models import Member as SetMember
from het.models import Member as HetMember
from training.models import Member as TrainingMember
from .utils import date_utils
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from calendar import month_name
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone
from .utils.date_utils import to_myanmar_date_formatted
from rest_framework import generics, permissions
from datetime import datetime
from .serializers import SpendingMoneySerializer

# Dashboard View
@login_required(login_url="/")
@role_required("admin")
def dashboard(request):
    total_departments = SetMember.objects.values('department').distinct().count()
    total_members = SetMember.objects.all().count() + HetMember.objects.all().count() + TrainingMember.objects.all().count()
    total_set_members = SetMember.objects.all().count()
    total_het_members = HetMember.objects.all().count()
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    context = {
        "system_name": system_name,
        "organization": organization,
        "active_menu": "admin_index",
        "today": timezone.now(),
        "total_set_members": total_set_members,
        "total_het_members": total_het_members,
        "software_count": 8,
        "hardware_count": 4,
        "training_count": 5,
        "software_last_updated": timezone.now(),
        "hardware_last_updated": timezone.now() - timedelta(days=2),
        "training_last_updated": timezone.now() - timedelta(days=1),
        "total_departments": total_departments,
        "total_members": total_members,
        "total_projects": 19,
        "software_progress": 80,
        "hardware_progress": 65,
        "training_progress": 90,
        "notifications": [
            {"message": "New user registered for training program", "level": "info", "timestamp": timezone.now() - timedelta(hours=1)},
            {"message": "Hardware inventory needs review", "level": "warning", "timestamp": timezone.now() - timedelta(hours=3)},
        ],
        "recent_actions": [
            {"type": "add", "message": "Added new Software project 'Quick Chat'", "timestamp": timezone.now() - timedelta(hours=2)},
            {"type": "update", "message": "Updated team member roles", "timestamp": timezone.now() - timedelta(hours=5)},
        ],
    }
    return render(request, 'pages/admin/dashboard.html', context)

# Users View
@login_required(login_url="/")
@role_required("admin")
def users(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    users = CustomUser.objects.all().order_by('id')
    total_users = len(users)
    total_admins = sum(1 for user in users if user.role == "admin")
    
    total_active = sum(1 for user in users if user.is_active)
    total_inactive = total_users - total_active

    context = {
        "system_name": system_name,
        "organization": organization,
        "total_users": total_users, 
        "total_admins": total_admins,
        "total_active": total_active,   
        "total_inactive": total_inactive,
        "active_menu": "admin_users",
        "users": users,
    }
    return render(request, 'pages/admin/users.html', context)

@login_required(login_url="/")
@role_required("admin")
def admin_settings(request):
    settings_obj, created = SystemSettings.objects.get_or_create(id=1)

    if request.method == "POST":
        settings_obj.system_name = request.POST.get("system_name", settings_obj.system_name)
        settings_obj.organization = request.POST.get("organization", settings_obj.organization)

        settings_obj.email_notifications = "email_notifications" in request.POST
        settings_obj.system_warnings = "system_warnings" in request.POST
        settings_obj.weekly_reports = "weekly_reports" in request.POST

        settings_obj.session_timeout = int(request.POST.get("session_timeout", 30))

        settings_obj.save()

        messages.success(request, " Settings saved successfully!")
        return redirect("admin.settings")

    # GET request → form values show
    context = {
        "system_name": settings_obj.system_name,
        "organization": settings_obj.organization,
        "email_notifications": settings_obj.email_notifications,
        "system_warnings": settings_obj.system_warnings,
        "weekly_reports": settings_obj.weekly_reports,
        "session_timeout": settings_obj.session_timeout,
        "active_menu": "admin_settings",
    }
    return render(request, "pages/admin/settings.html", context)

# Spending Money View
@login_required(login_url="/")
@role_required("admin")
def admin_all_spending_money(request):
    MYANMAR_MONTHS = [
    "ဇန်နဝါရီလ",   # 01
    "ဖေဖော်ဝါရီလ", # 02
    "မတ်လ",         # 03
    "ဧပြီလ",       # 04
    "မေလ",          # 05
    "ဂျုန်လ",         # 06
    "ဂျူလိုင်လ",      # 07
    "ဩဂတ်စ်လ",      # 08
    "စပ်တမ်ဘာလ",    # 09
    "အောက်တိုဘာလ",  # 10
    "နိုဗမ်ဘာလ",     # 11
    "ဒီဇင်ဘာလ",      # 12
    ]

    today = timezone.now()
    current_month = today.month
    current_year = today.year
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization

    # Filters
    selected_dept = request.GET.get("department", "all")
    selected_month = request.GET.get("month", str(current_month))
    selected_year = request.GET.get("year", str(current_year))
    # All Month option (value = "all")
    months = [("all", "လအားလုံး")] + [(str(i).zfill(2), MYANMAR_MONTHS[i-1]) for i in range(1, 13)]
    years = range(current_year - 5, current_year + 2)
    
    # Empty result list
    spending_money = []

    # Helper for cost calculation
    def annotate_total(qs, dept_name):
        qs = qs.annotate(
            total_cost=ExpressionWrapper(
                F("quantity") * F("estimated_cost"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        for r in qs:
            r.department = dept_name
            spending_money.append(r)    

    # If "all" month is selected → don’t filter by month
    month_filter = {} if selected_month == "all" else {"month": str(selected_month).zfill(2)}

    if selected_dept in ["set", "all"]:
        qs = SoftwareSpendingMoney.objects.filter(year=selected_year, **month_filter)
        annotate_total(qs, "SET")

    if selected_dept in ["het", "all"]:
        qs = HardwareSpendingMoney.objects.filter(year=selected_year, **month_filter)
        annotate_total(qs, "HET")

    if selected_dept in ["training", "all"]:
        qs = TrainingSpendingMoney.objects.filter(year=selected_year, **month_filter)
        annotate_total(qs, "TRAINING")
    if selected_dept in ["office", "all"]:
        qs = SpendingMoney.objects.filter(year=selected_year, **month_filter)
        annotate_total(qs, "OFFICE")

    total_cost = sum(float(r.total_cost or 0) for r in spending_money)
    total_items = len(spending_money)
    spending_money = sorted(spending_money, key=lambda x: (x.department, x.month))
    context = {
        "spending_money": spending_money,
        "total_cost": total_cost,
        "total_items": total_items,
        "selected_dept": selected_dept,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "months": months,
        "spending_money": spending_money,
        "years": years,
        "system_name": system_name,
        "organization": organization,
        "active_menu": "admin_all_spending_money",
    }

    return render(request, "pages/admin/admin-all-spending-money.html", context)

# Spending Money Summary View
@login_required(login_url="/")
@role_required("admin")
def admin_spending_money_summary(request):
    MYANMAR_MONTHS = [
    "ဇန်နဝါရီလ",   # 01
    "ဖေဖော်ဝါရီလ", # 02
    "မတ်လ",         # 03
    "ဧပြီလ",       # 04
    "မေလ",          # 05
    "ဂျုန်လ",         # 06
    "ဂျူလိုင်လ",      # 07
    "ဩဂတ်စ်လ",      # 08
    "စပ်တမ်ဘာလ",    # 09
    "အောက်တိုဘာလ",  # 10
    "နိုဗမ်ဘာလ",     # 11
    "ဒီဇင်ဘာလ",      # 12
    ]
    # --- Get selected year or default to current year
    today = timezone.now()
    current_year = today.year
    selected_year = int(request.GET.get("year", current_year))
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    
    # --- Prepare data containers
    summary_data = []
    yearly_total = 0
    total_set = total_het = total_training = total_office = 0

    # --- Quantity × Cost Expression
    total_expr = ExpressionWrapper(
        F("quantity") * F("estimated_cost"),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )

    # --- Generate all months summary
    for i in range(1, 13):
        month_num = str(i).zfill(2)
        month_label = MYANMAR_MONTHS[i-1]

        set_total = (
            SoftwareSpendingMoney.objects.filter(year=selected_year, month=month_num)
            .aggregate(total=Sum(total_expr))["total"] or 0
        )
        het_total = (
            HardwareSpendingMoney.objects.filter(year=selected_year, month=month_num)
            .aggregate(total=Sum(total_expr))["total"] or 0
        )
        training_total = (
            TrainingSpendingMoney.objects.filter(year=selected_year, month=month_num)
            .aggregate(total=Sum(total_expr))["total"] or 0
        )
        office_total = (
            SpendingMoney.objects.filter(year=selected_year, month=month_num)
            .aggregate(total=Sum(total_expr))["total"] or 0
        )

        grand_total = set_total + het_total + training_total + office_total
        yearly_total += grand_total
        total_set += set_total
        total_het += het_total
        total_training += training_total
        total_office += office_total

        summary_data.append({
            "month": month_label,
            "set_total": set_total,
            "het_total": het_total,
            "training_total": training_total,
            "office_total": office_total,
            "grand_total": grand_total,
        })

    # --- Export PDF Logic
    if "export" in request.GET and request.GET["export"] == "pdf":
        return export_spending_money_pdf(summary_data, total_set, total_het, total_training,total_office, yearly_total, selected_year)

    # --- Render normal HTML
    years = range(current_year - 16, current_year + 7)
    context = {
        "year": selected_year,
        "years": years,
        "system_name": system_name,
        "organization": organization,
        "summary_data": summary_data,
        "yearly_total": yearly_total,
        "total_set": total_set,
        "total_het": total_het,
        "total_training": total_training,
        "total_office": total_office,
        "active_menu": "admin_all_spending_money_summary",
    }
    return render(request, "pages/admin/admin-all-spending-money-summary.html", context)    



# Spending Money PDF Export Function
def export_spending_money_pdf(summary_data, total_set, total_het, total_training,total_office, yearly_total, year = to_myanmar_date_formatted(timezone.now())):

    current_date = to_myanmar_date_formatted(timezone.now())
        # Myanmar month mapping
    MYANMAR_MONTH_MAP = {
        "January": "ဂျန်နဝါရီ",
        "February": "ဖေဖော်ဝါရီ",
        "March": "မတ်ချ်",
        "April": "ဧပြီ",
        "May": "မေ",
        "June": "ဂျုန်",
        "July": "ဂျူလိုင်",
        "August": "သြဂတ်စ်",
        "September": "စပ်တမ်ဘာ",
        "October": "အောက်တိုဘာ",
        "November": "နိုဗမ်ဘာ",
        "December": "ဒီဇင်ဘာ",
    }
    # Convert month names inside summary_data
    for row in summary_data:
        eng_month = row["month"]
        row["month_mm"] = MYANMAR_MONTH_MAP.get(eng_month, eng_month)

    html_string = render_to_string(
        "pages/admin/admin-all-spending-money-summary-pdf.html",
        {
            "summary_data": summary_data,
            "total_set": total_set,
            "total_het": total_het,
            "total_training": total_training,
            "yearly_total": yearly_total,
            "year": year,
            "current_date": current_date,
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"all_spending_money_summary_{year}.pdf\"'
    return response


# Spending Money API View

class SpendingMoneyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SpendingMoneySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = SpendingMoney.objects.all().order_by("-created_at")
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")
        if month and month != "all":
            qs = qs.filter(month=month)
        if year and year != "all":
            qs = qs.filter(year=year)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Spending Money Detail API View

class SpendingMoneyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SpendingMoney.objects.all()
    serializer_class = SpendingMoneySerializer
    permission_classes = [permissions.IsAuthenticated]

# Spending Money Page View
@login_required(login_url="/")
@role_required("admin")
def spending_page(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    
    months = SpendingMoney.MONTH_CHOICES
    
    years = range(2023, datetime.now().year + 6)
    return render(request, "pages/admin/spending-money/spending_page.html", {"months": months, "years": years, "system_name": system_name, "organization": organization, "active_menu": "admin_spending_page"})

# Spending Money PDF Export View
@login_required(login_url="/")
@role_required("admin")
def export_spending_pdf(request):
    month = request.GET.get("month", "all")
    year = request.GET.get("year", datetime.now().year)
    qs = SpendingMoney.objects.all()
    current_date = date_utils.to_myanmar_date_formatted(datetime.now())

    if month != "all":
        qs = qs.filter(month=month)
    if year != "all":
        qs = qs.filter(year=year)
    total_sum = sum([r.total_cost for r in qs])
    html = render_to_string("pages/admin/spending-money/spending_pdf.html", {"records": qs, "total_sum": total_sum, "month": month, "year": year, "current_date": current_date})
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="spending_{month}_{year}.pdf"'
    return response


# Team Members View
@login_required(login_url="/")
@role_required("admin")
def all_team_members(request):
    set_members = SetMember.objects.all()
    het_members = HetMember.objects.all()
    training_members = TrainingMember.objects.all()
    return render(request, "pages/admin/team_members.html", {
        "set_members": set_members,
        "het_members": het_members,
        "training_members": training_members,
        "active_menu": "admin_team_members",
    })


def custom_404(request, exception):
    return render(request, "pages/errors/404.html", status=404)