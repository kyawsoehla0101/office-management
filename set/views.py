from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from set.decorators import set_required
from django.contrib.auth.decorators import login_required
from set.models import Member, Project
from accounts.utils.decorators import role_required
from set.models import SoftwareSpendingMoney
from calendar import month_name
from django.db.models import F, Q   
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from base.models import SystemSettings
from base.utils import date_utils

# SET Index View
@role_required("set", "admin")
def index(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    context = {
        "active_menu": "set_index",
        "active_developers": 42,
        "new_devs_this_month": 3,
        "ongoing_projects": 9,
        "commits_today": 158,
        "system_name": system_name,
        "organization": organization,
        "commits_growth": 12,
        "open_issues": 14,
        "critical_bugs": 2,
        "last_project_update": timezone.now() - timedelta(days=1),
        "projects": [
            {"name": "JobSeeker Portal", "lead": "Aung Kyaw", "progress": 85, "last_commit": timezone.now()},
            {"name": "Quick Chat App", "lead": "May Thazin", "progress": 70, "last_commit": timezone.now() - timedelta(hours=2)},
            {"name": "Resume Builder", "lead": "Min Htet", "progress": 95, "last_commit": timezone.now() - timedelta(hours=5)},
        ],
        "recent_activities": [
            {"type": "commit", "message": "🚀 Deployed new version of Resume Builder", "timestamp": timezone.now() - timedelta(hours=1)},
            {"type": "issue", "message": "❗ Fixed critical bug in authentication", "timestamp": timezone.now() - timedelta(hours=3)},
            {"type": "merge", "message": "✅ Merged new chat module (Socket.io)", "timestamp": timezone.now() - timedelta(hours=5)},
        ]
    }
    return render(request, 'pages/set/index.html', context)
@login_required(login_url="login")
@role_required("set", "admin")
def members(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    members = Member.objects.all().order_by("department", "position")
    total_active_members = members.filter(is_active=True).count()
    total_genders = members.values_list("gender", flat=True).distinct().count()
    total_male_members = members.filter(gender=Member.GENDER_CHOICES[0][0]).count()
    total_female_members = members.filter(gender=Member.GENDER_CHOICES[1][0]).count()  
    total_positions = members.values_list("position", flat=True).distinct().count()
    total_inactive_members = members.filter(is_active=False).count()    

    context = {
        "members": members,
        "total_members": len(members),
        "total_projects": 8,
        "total_departments": 2,
        "total_active_members": total_active_members,
        "total_genders": total_genders,
        "total_male_members": total_male_members,
        "total_female_members": total_female_members,
        "total_positions": total_positions,
        "total_inactive_members": total_inactive_members,
        "active_menu": "set_members",
        "system_name": system_name,
        "organization": organization,
    }
    return render(request, 'pages/set/members/members.html', context)

def addReport(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    return render(request, 'pages/set/add-report.html', {
        "active_menu": "set_report",
        "system_name": system_name,
        "organization": organization,
    })    

def projects(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    projects = Project.objects.all().order_by("status", "priority")
    total_projects = len(projects)
    total_active_projects = projects.filter(status=Project.STATUS_CHOICES[0][0]).count()
    total_inactive_projects = projects.filter(status=Project.STATUS_CHOICES[1][0]).count()
    total_planning_projects = projects.filter(status=Project.STATUS_CHOICES[0][0]).count()
    total_completed_projects = projects.filter(status=Project.STATUS_CHOICES[2][0]).count()
    total_ongoing_projects = projects.filter(status=Project.STATUS_CHOICES[1][0]).count()
    total_on_hold_projects = projects.filter(status=Project.STATUS_CHOICES[3][0]).count()
    total_cancelled_projects = projects.filter(status=Project.STATUS_CHOICES[4][0]).count()
    total_priorities = projects.values_list("priority", flat=True).distinct().count()
    total_low_priority_projects = projects.filter(priority=Project.PRIORITY_CHOICES[0][0]).count()
    total_medium_priority_projects = projects.filter(priority=Project.PRIORITY_CHOICES[1][0]).count()
    total_high_priority_projects = projects.filter(priority=Project.PRIORITY_CHOICES[2][0]).count()


    context = {
        "projects": projects,
        "system_name": system_name,
        "organization": organization,
        "total_projects": total_projects,
        "total_active_projects": total_active_projects,
        "total_inactive_projects": total_inactive_projects,
        "total_planning_projects": total_planning_projects,
        "total_completed_projects": total_completed_projects,
        "total_ongoing_projects": total_ongoing_projects,
        "total_priorities": total_priorities,
        "total_low_priority_projects": total_low_priority_projects,
        "total_medium_priority_projects": total_medium_priority_projects,
        "total_high_priority_projects": total_high_priority_projects,
        "total_on_hold_projects": total_on_hold_projects,
        "total_cancelled_projects": total_cancelled_projects,
        "active_menu": "set_projects",
    }
    return render(request, 'pages/set/projects/projects.html', context)

@role_required("set", "admin")
def addMember(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    positions = Member.POSITION_CHOICES
    ranks = Member.RANK_CHOICES
    genders = Member.GENDER_CHOICES
    context = {
        "active_menu": "set_members",
        "positions": positions,
        "ranks": ranks, 
        "genders": genders,
        "system_name": system_name,
        "organization": organization,
    } 
    if request.method == "POST":
        reg_no = request.POST.get("reg_no")
        full_name = request.POST.get("full_name")
        position = request.POST.get("position")
        joined_date = request.POST.get("joined_date")
        position = request.POST.get("position")
        bio = request.POST.get("bio")
        profile_photo = request.FILES.get("profile_photo")
        rank = request.POST.get("rank")
        gender = request.POST.get("gender")
        birth_date = request.POST.get("birth_date")
        # if not profile_photo:
        #     messages.error(request, "Profile photo is required.")
        #     return redirect("set.add_member")
            


        # Auto assign department from user role
        department = request.user.role.upper()  # e.g. "set" → "SET"

        Member.objects.create(
            reg_no=reg_no,
            full_name=full_name,
            position=position,
            joined_date=joined_date,
            department=department,
            user=request.user,
            bio=bio,
            profile_photo=profile_photo,
            rank=rank,
            gender=gender,
            birth_date=birth_date,
        )
        
        messages.success(request, f"Member '{full_name}' added to {department} team.")
        return redirect("set.members")

    return render(request, "pages/set/members/add-member.html", context)

@role_required("set", "admin")
def editMember(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    member = get_object_or_404(Member, id=id)
    if request.method == "POST":
        member.full_name = request.POST.get("full_name")
        member.reg_no = request.POST.get("reg_no")
        member.rank = request.POST.get("rank")
        member.position = request.POST.get("position")
        member.joined_date = request.POST.get("joined_date")
        member.bio = request.POST.get("bio")
        member.gender = request.POST.get("gender")
        member.birth_date = request.POST.get("birth_date")
        member.is_active = bool(request.POST.get("is_active"))

        if request.FILES.get("profile_photo"):
            member.profile_photo = request.FILES["profile_photo"]

        member.save()
        messages.success(request, f"Member '{member.full_name}' updated successfully!")
        return redirect("set.members")

    context = {
        "active_menu": "set_members",
        "system_name": system_name,
        "organization": organization,
        "member": member,
        "ranks": Member.RANK_CHOICES,
        "positions": Member.POSITION_CHOICES,
        "genders": Member.GENDER_CHOICES,
    }
    return render(request, "pages/set/members/edit-member.html", context)
@role_required("set", "admin")
def memberDetail(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    member = get_object_or_404(Member, id=id)
    context = {
        "active_menu": "set_members",
        "system_name": system_name,
        "organization": organization,
        "member": member,
    }
    return render(request, 'pages/set/members/member-detail.html', context) 
@role_required("set", "admin")
def deleteMember(request,id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    member = get_object_or_404(Member, id=id)
    context = {
        "active_menu": "set_members",
        "system_name": system_name,
        "organization": organization,
        "member": member,
    }
    if request.method == "POST":
        member.delete()
        messages.success(request, f"Member '{member.full_name}' deleted successfully.")
        return redirect('set.members')
    return render(request, 'pages/set/members/member-delete.html', context)

@role_required("set", "admin")
def requirements(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Default month/year
    selected_month = request.GET.get("month")
    selected_year = request.GET.get("year")

    # 🧩 Handle defaults
    if not selected_month:
        selected_month = str(current_month)
    if not selected_year:
        selected_year = str(current_year)

    # 🔹 filtering logic
    if selected_month == "all":
        requirements = SoftwareSpendingMoney.objects.filter(year=selected_year)
    else:
        try:
            selected_month_int = int(selected_month)
        except ValueError:
            selected_month_int = current_month

        requirements = SoftwareSpendingMoney.objects.filter(  
            month=selected_month_int, year=selected_year
        )

    # 🧾 Calculate total
    total_cost = sum((r.estimated_cost or 0) * (r.quantity or 0) for r in requirements)

    # Dropdown lists
    months = [("all", "All Months")] + [(i, month_name[i]) for i in range(1, 13)]
    years = range(current_year - 5, current_year + 3)

    context = {
        "system_name": system_name,
        "organization": organization,
        "requirements": requirements,
        "total_cost": total_cost,
        "months": months,
        "years": years,
        "selected_month": selected_month,
        "selected_year": int(selected_year),
        "active_menu": "set_requirements",
    }
    return render(request, "pages/set/requirements/requirements.html", context)

@role_required("set", "admin")
def requirements_summary(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    today = timezone.now()
    current_year = today.year

    # Group by month and sum total cost
    monthly_totals = (
        SoftwareSpendingMoney.objects
        .filter(year=current_year)
        .values("month")
        .annotate(total=Sum(F("estimated_cost") * F("quantity")))
        .order_by("month")
    )

    # Calculate total yearly cost
    yearly_total = sum([m["total"] or 0 for m in monthly_totals])

    # Convert month numbers to names
    from calendar import month_name
    for m in monthly_totals:
        m["month_name"] = month_name[int(m["month"])]

    context = {
        "system_name": system_name,
        "organization": organization,
        "monthly_totals": monthly_totals,
        "yearly_total": yearly_total,
        "year": current_year,
        "active_menu": "set_requirements_summary",
    }
    return render(request, "pages/set/requirements/requirement-summary.html", context)

@role_required("set", "admin")
def addRequirement(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    if request.method == "POST":
        item = SoftwareSpendingMoney(
            item_name=request.POST.get("item_name"),
            category=request.POST.get("category"),
            quantity=request.POST.get("quantity") or 1,
            unit=request.POST.get("unit") or "pcs",
            estimated_cost=request.POST.get("estimated_cost") or 0,
            month=request.POST.get("month"),
            year=request.POST.get("year"),
            description=request.POST.get("description"),
            requested_by=request.user,
        )
        if request.FILES.get("attachment"):
            item.attachment = request.FILES["attachment"]
        item.save()
        messages.success(request, "Monthly requirement submitted successfully!")
        return redirect("set.requirements")

    month_choices = SoftwareSpendingMoney.MONTH_CHOICES
    return render(request, "pages/set/requirements/add-requirement.html", {"month_choices": month_choices, "active_menu": "set_requirements", "system_name": system_name, "organization": organization})
@role_required("set", "admin")
def viewRequirement(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    requirement = get_object_or_404(SoftwareSpendingMoney, id=id)
    return render(request, "pages/set/requirements/view-requirement.html", {"requirement": requirement, "active_menu": "set_requirements", "system_name": system_name, "organization": organization})

@role_required("set", "admin")
def editRequirement(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    requirement = get_object_or_404(SoftwareSpendingMoney, id=id)
    today = timezone.now()
    current_year = today.year

    months = [(i, month_name[i]) for i in range(1, 13)]
    years = range(current_year - 5, current_year + 3)

    categories = [
        ("electrical", "Electrical Equipment"),
        ("computer", "Computer Device"),
        ("network", "Network Tools"),
        ("office", "Office Supplies"),
        ("other", "Other"),
    ]

    if request.method == "POST":
        requirement.item_name = request.POST.get("item_name")
        requirement.category = request.POST.get("category")
        requirement.quantity = request.POST.get("quantity") or 0
        requirement.estimated_cost = request.POST.get("estimated_cost") or 0
        requirement.month = request.POST.get("month")
        requirement.year = request.POST.get("year")
        requirement.description = request.POST.get("description")

        if request.FILES.get("attachment"):
            requirement.attachment = request.FILES["attachment"]

        requirement.save()
        return redirect("set.requirements")

    return render(request, "pages/set/requirements/edit-requirement.html", {
        "requirement": requirement,
        "months": months,
        "years": years,
        "categories": categories,
        "active_menu": "set_requirements",
        "system_name": system_name,
        "organization": organization,
    })
@role_required("set", "admin")
def deleteRequirement(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    requirement = get_object_or_404(SoftwareSpendingMoney, id=id)
    if request.method == "POST":
        requirement.delete()
        return redirect("set.requirements")

    return render(request, "pages/set/requirements/delete-requirement.html", {"requirement": requirement, "active_menu": "set_requirements", "system_name": system_name, "organization": organization})

@role_required("set", "admin")
def report(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    projects = Project.objects.all().select_related("team_lead").prefetch_related("members")

    search_query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "")
    selected_priority = request.GET.get("priority", "")

    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(team_lead__full_name__icontains=search_query)
        )

    if selected_status:
        projects = projects.filter(status=selected_status)

    if selected_priority:
        projects = projects.filter(priority=selected_priority)

    context = {
        "system_name": system_name,
        "organization": organization,
        "projects": projects,
        "search_query": search_query,
        "selected_status": selected_status,
        "selected_priority": selected_priority,
        "Project": Project,  # for STATUS_CHOICES in template
        "active_menu": "set_reports",
    }

    return render(request, "pages/set/reports/report.html", context)

@role_required("set", "admin")
def addProject(request):
    members = Member.objects.all()
    statuses = Project.STATUS_CHOICES
    priorities = Project.PRIORITY_CHOICES   
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  

    context = {
        "system_name": system_name,
        "organization": organization,   
        "members": members,
        "statuses": statuses,   
        "active_menu": "set_projects",
        "priorities": priorities,
    }
    if request.method == "POST":
        title = request.POST.get("title")
        desc = request.POST.get("description")
        document = request.FILES.get("document")
        priority = request.POST.get("priority")
        start_date = request.POST.get("start_date")
        deadline = request.POST.get("deadline")
        team_lead_id = request.POST.get("lead")
        member_ids = request.POST.getlist("members")
        status = request.POST.get("status")
        document = request.FILES.get("document")

        project  = Project.objects.create(
            title=title,
            description=desc,
            created_by=request.user,
            status=status,
            project_document=document,
            priority=priority,
            start_date=start_date,
            deadline=deadline,
        )

        # ✅ team_lead assign
        if team_lead_id:
            try:
                project.team_lead = Member.objects.get(id=team_lead_id)
            except Member.DoesNotExist:
                pass
            project.save()

        # ✅ members assign (ManyToMany)
        if member_ids:
            project.members.set(member_ids)
        messages.success(request, "Project submitted successfully.")
        return redirect("set.projects")
    return render(request, 'pages/set/projects/add-project.html', context)

@role_required("set", "admin")
def editProject(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    context = {
        "system_name": system_name,
        "organization": organization,   
        "active_menu": "set_projects",
        "priorities": Project.PRIORITY_CHOICES,
        "statuses": Project.STATUS_CHOICES,
        "members": Member.objects.all(),
    }
    project = get_object_or_404(Project, id=id)
    if request.method == "POST":
        project.title = request.POST.get("title")
        project.description = request.POST.get("description")
        project.lead = request.POST.get("lead")
        project.priority = request.POST.get("priority")
        project.start_date = request.POST.get("start_date")
        project.deadline = request.POST.get("deadline")
        project.members.set(request.POST.getlist("members"))
        project.status = request.POST.get("status")
        project_document = request.FILES.get("document")
        if project_document:
            project.project_document = project_document
        project.save()
        messages.success(request, f"Project '{project.title}' updated successfully.")
        return redirect("set.projects")
    context["project"] = project
    return render(request, "pages/set/projects/edit-project.html", context)

@role_required("set", "admin")
def detailProject(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    project = get_object_or_404(Project, id=id)
    return render(request, "pages/set/projects/project-detail.html", {
        "system_name": system_name,
        "organization": organization,   
        "project": project,
        "active_menu": "set_projects"
    })

@role_required("set", "admin")
def deleteProject(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    project = get_object_or_404(Project, id=id)
    if request.method == "POST":
        project.delete()
        messages.success(request, f"Project '{project.title}' deleted successfully.")
        return redirect("set.projects")
    return render(request, "pages/set/projects/project-delete.html", {
        "system_name": system_name,
        "organization": organization,   
        "project": project,
        "active_menu": "set_projects"
    })

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from datetime import datetime
from django.utils import timezone
from .models import Project
from .utils.date_utils import to_myanmar_date
def export_projects_pdf(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    projects = Project.objects.all().order_by("status", "priority")

    context = {
        "system_name": system_name,
        "organization": organization,   
        "projects": projects,
        "current_date": to_myanmar_date(timezone.now()),

        "total_projects": projects.count(),
        "completed_count": projects.filter(status="COMPLETED").count(),
        "ongoing_count": projects.filter(status="ONGOING").count(),
        "planning_count": projects.filter(status="PLANNING").count(),
    }

    html_string = render_to_string("pages/set/projects/project-report-pdf.html", context)

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=SET_Project_Report.pdf"
    return response



from rest_framework import generics, permissions
from datetime import datetime
from .serializers import SoftwareSpendingMoneySerializer

# Spending Money API View

class SpendingMoneyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SoftwareSpendingMoneySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = SoftwareSpendingMoney.objects.all().order_by("-created_at")
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
    queryset = SoftwareSpendingMoney.objects.all()
    serializer_class = SoftwareSpendingMoneySerializer
    permission_classes = [permissions.IsAuthenticated]

# Spending Money Page View
@login_required(login_url="/")
@role_required("admin", "set")
def spending_page(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    
    months = SoftwareSpendingMoney.MONTH_CHOICES
    
    years = range(2023, datetime.now().year + 6)
    return render(request, "pages/set/spending-money/spending_page.html", {"months": months, "years": years, "system_name": system_name, "organization": organization, "active_menu": "set_spending_page"})

# Spending Money PDF Export View
@login_required(login_url="/")
@role_required("admin", "set")
def export_spending_pdf(request):
    month = request.GET.get("month", "all")
    year = request.GET.get("year", datetime.now().year)
    qs = SoftwareSpendingMoney.objects.all()
    current_date = date_utils.to_myanmar_date_formatted(datetime.now())

    if month != "all":
        qs = qs.filter(month=month)
    if year != "all":
        qs = qs.filter(year=year)
    total_sum = sum([r.total_cost for r in qs])
    html = render_to_string("pages/set/spending-money/spending_pdf.html", {"records": qs, "total_sum": total_sum, "month": month, "year": year, "current_date": current_date})
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="spending_{month}_{year}.pdf"'
    return response