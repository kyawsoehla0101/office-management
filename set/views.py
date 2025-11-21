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
from .models import Project, SoftwareActivity
from .activity import log_activity_dev
from base.utils.date_utils import to_myanmar_date

# SET Index View
@role_required("set", "admin")
def index(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  

     # KPIs
    active_developers = Member.objects.filter(is_active=True).count()
    new_devs_this_month = Member.objects.filter(created_at__month=timezone.now().month).count()

    ongoing_projects = Project.objects.filter(status="active").count()
    last_project_update = Project.objects.order_by("-updated_at").first()

    commits_today = SoftwareActivity.objects.filter(
        type="commit",
        timestamp__date=timezone.now().date()
    ).count()

    commits_growth = 15  # Dummy (optional – later compute)

    open_issues = SoftwareActivity.objects.filter(type="issue").count()
    critical_bugs = SoftwareActivity.objects.filter(
        type="issue",
        message__icontains="critical"
    ).count()

    # Projects list
    active_projects = Project.objects.all()

    # Recent Activities (limit 10)
    recent_activities = SoftwareActivity.objects.order_by("-timestamp")[:10]

    context = {
        "active_developers": active_developers,
        "new_devs_this_month": new_devs_this_month,

        "ongoing_projects": ongoing_projects,
        "last_project_update": last_project_update,

        "commits_today": commits_today,
        "commits_growth": commits_growth,

        "open_issues": open_issues,
        "critical_bugs": critical_bugs,

        "active_projects": active_projects,
        "recent_activities": recent_activities,

        "active_menu": "set_index",
        "system_name": system_name,
        "organization": organization,
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

        member = Member.objects.create(
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
        # 🔥 Activity Log
        log_activity_dev(
            message=f"👤 New member added — {member.full_name}",
            event_type="developer",
            user=request.user
        )
        
        messages.success(request, f"Member '{full_name}' added to {department} team.")
        return redirect("set.members")

    return render(request, "pages/set/members/add-member.html", context)

@role_required("set", "admin")
# def editMember(request, id):
#     system_name = SystemSettings.objects.first().system_name
#     organization = SystemSettings.objects.first().organization  
#     member = get_object_or_404(Member, id=id)
#     if request.method == "POST":
#         member.full_name = request.POST.get("full_name")
#         member.reg_no = request.POST.get("reg_no")
#         member.rank = request.POST.get("rank")
#         member.position = request.POST.get("position")
#         member.joined_date = request.POST.get("joined_date")
#         member.bio = request.POST.get("bio")
#         member.gender = request.POST.get("gender")
#         member.birth_date = request.POST.get("birth_date")
#         member.is_active = bool(request.POST.get("is_active"))

#         if request.FILES.get("profile_photo"):
#             member.profile_photo = request.FILES["profile_photo"]

#         member.save()
#         messages.success(request, f"Member '{member.full_name}' updated successfully!")
#         return redirect("set.members")

#     context = {
#         "active_menu": "set_members",
#         "system_name": system_name,
#         "organization": organization,
#         "member": member,
#         "ranks": Member.RANK_CHOICES,
#         "positions": Member.POSITION_CHOICES,
#         "genders": Member.GENDER_CHOICES,
#     }
#     return render(request, "pages/set/members/edit-member.html", context)


def editMember(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    member = get_object_or_404(Member, id=id)

    # Store old values
    old_name = member.full_name
    old_reg = member.reg_no
    old_rank = member.rank
    old_position = member.position
    old_gender = member.gender
    old_birth = member.birth_date
    old_joined = member.joined_date
    old_active = member.is_active
    old_bio = member.bio
    old_photo = member.profile_photo

    if request.method == "POST":

        new_name = request.POST.get("full_name")
        new_reg = request.POST.get("reg_no")
        new_rank = request.POST.get("rank")
        new_position = request.POST.get("position")
        new_joined = request.POST.get("joined_date")
        new_bio = request.POST.get("bio")
        new_gender = request.POST.get("gender")
        new_birth = request.POST.get("birth_date")
        new_active = bool(request.POST.get("is_active"))
        new_photo = request.FILES.get("profile_photo")

        # Convert dates
        try:
            new_birth_date = datetime.strptime(new_birth, "%Y-%m-%d").date() if new_birth else None
        except:
            new_birth_date = member.birth_date

        try:
            new_joined_date = datetime.strptime(new_joined, "%Y-%m-%d").date() if new_joined else None
        except:
            new_joined_date = member.joined_date

        # ============ LOG CHANGES ============
        if new_name != old_name:
            log_activity_dev(
                f"📝 Member name changed: {old_name} → {new_name}",
                "member",
                request.user
            )

        if new_rank != old_rank:
            log_activity_dev(
                f"🎖 Rank updated: {old_rank} → {new_rank} ({new_name})",
                "member",
                request.user
            )

        if new_position != old_position:
            log_activity_dev(
                f"👨‍💻 Position changed: {old_position} → {new_position} ({new_name})",
                "member",
                request.user
            )

        if new_gender != old_gender:
            log_activity_dev(
                f"⚧ Gender changed: {old_gender} → {new_gender} ({new_name})",
                "member",
                request.user
            )

        if new_birth_date != old_birth:
            log_activity_dev(
                f"🎂 Birthdate updated: {old_birth} → {new_birth_date} ({new_name})",
                "member",
                request.user
            )

        if new_joined_date != old_joined:
            log_activity_dev(
                f"📅 Joined date changed: {old_joined} → {new_joined_date} ({new_name})",
                "member",
                request.user
            )

        if new_active != old_active:
            status = "Active" if new_active else "Inactive"
            old_status = "Active" if old_active else "Inactive"
            log_activity_dev(
                f"🔄 Member status changed: {old_status} → {status} ({new_name})",
                "member",
                request.user
            )

        if new_bio != old_bio:
            log_activity_dev(
                f"🗒 Bio updated for {new_name}",
                "member",
                request.user
            )

        if new_photo:
            log_activity_dev(
                f"🖼 Profile photo updated for {new_name}",
                "member",
                request.user
            )

        # ============ SAVE NEW DATA ============
        member.full_name = new_name
        member.reg_no = new_reg
        member.rank = new_rank
        member.position = new_position
        member.gender = new_gender
        member.birth_date = new_birth_date
        member.joined_date = new_joined_date
        member.bio = new_bio
        member.is_active = new_active

        if new_photo:
            member.profile_photo = new_photo

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
def deleteMember(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    member = get_object_or_404(Member, id=id)

    if request.method == "POST":
        # Store before deletion for log
        deleted_name = member.full_name
        deleted_rank = member.rank
        deleted_position = member.position

        # Delete
        member.delete()

        # LOG ACTIVITY
        log_activity_dev(
            f"🗑 Member deleted: {deleted_name} (Rank: {deleted_rank}, Position: {deleted_position})",
            "member",
            request.user
        )

        messages.success(request, f"Member '{deleted_name}' deleted successfully.")
        return redirect("set.members")

    context = {
        "active_menu": "set_members",
        "system_name": system_name,
        "organization": organization,
        "member": member,
    }
    return render(request, "pages/set/members/member-delete.html", context)


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

from .utils import log_activity
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

        # Create project
        project = Project.objects.create(
            title=title,
            description=desc,
            created_by=request.user,
            status=status,
            project_document=document,
            priority=priority,
            start_date=start_date,
            deadline=deadline,
        )

        # Log project creation
        log_activity(
            message=f"🆕 Project created: {project.title}",
            activity_type="project",
            user=request.user
        )

        # Team Lead assign
        if team_lead_id:
            try:
                lead = Member.objects.get(id=team_lead_id)
                project.team_lead = lead
                project.save()

                log_activity(
                    message=f"👨‍💻 {lead.full_name} assigned as Team Lead for '{project.title}'",
                    activity_type="developer",
                    user=request.user
                )
            except Member.DoesNotExist:
                pass

        # Member Assign (ManyToMany)
        if member_ids:
            project.members.set(member_ids)

            # Log each member
            for mid in member_ids:
                try:
                    m = Member.objects.get(id=mid)
                    log_activity(
                        message=f"👥 Added member {m.full_name} to project '{project.title}'",
                        activity_type="developer",
                        user=request.user
                    )
                except:
                    pass

        messages.success(request, "Project submitted successfully.")
        return redirect("set.projects")

    return render(request, 'pages/set/projects/add-project.html', context)

# def addProject(request):
#     members = Member.objects.all()
#     statuses = Project.STATUS_CHOICES
#     priorities = Project.PRIORITY_CHOICES   
#     system_name = SystemSettings.objects.first().system_name
#     organization = SystemSettings.objects.first().organization  

#     context = {
#         "system_name": system_name,
#         "organization": organization,   
#         "members": members,
#         "statuses": statuses,   
#         "active_menu": "set_projects",
#         "priorities": priorities,
#     }
#     if request.method == "POST":
#         title = request.POST.get("title")
#         desc = request.POST.get("description")
#         document = request.FILES.get("document")
#         priority = request.POST.get("priority")
#         start_date = request.POST.get("start_date")
#         deadline = request.POST.get("deadline")
#         team_lead_id = request.POST.get("lead")
#         member_ids = request.POST.getlist("members")
#         status = request.POST.get("status")
#         document = request.FILES.get("document")

#         project  = Project.objects.create(
#             title=title,
#             description=desc,
#             created_by=request.user,
#             status=status,
#             project_document=document,
#             priority=priority,
#             start_date=start_date,
#             deadline=deadline,
#         )

#         # ✅ team_lead assign
#         if team_lead_id:
#             try:
#                 project.team_lead = Member.objects.get(id=team_lead_id)
#             except Member.DoesNotExist:
#                 pass
#             project.save()

#         # ✅ members assign (ManyToMany)
#         if member_ids:
#             project.members.set(member_ids)
#         messages.success(request, "Project submitted successfully.")
#         return redirect("set.projects")
#     return render(request, 'pages/set/projects/add-project.html', context)

@role_required("set", "admin")
def editProject(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    project = get_object_or_404(Project, id=id)

    # OLD values (for Activity Log)
    old_title = project.title
    old_desc = project.description
    old_status = project.status
    old_priority = project.priority
    old_lead = project.team_lead
    old_deadline = project.deadline
    old_start = project.start_date
    old_document = project.project_document
    old_members = set(project.members.values_list('id', flat=True))
    old_progress = project.progress  # ✅ Progress added

    members = Member.objects.all()
    statuses = Project.STATUS_CHOICES
    priorities = Project.PRIORITY_CHOICES

    if request.method == "POST":
        new_title = request.POST.get("title")
        new_desc = request.POST.get("description")
        new_status = request.POST.get("status")
        new_priority = request.POST.get("priority")
        new_start = request.POST.get("start_date")
        new_deadline = request.POST.get("deadline")
        new_lead_id = request.POST.get("lead")
        new_member_ids = set(request.POST.getlist("members"))
        new_document = request.FILES.get("document")

        # --- UPDATE FIELDS ---
        project.title = new_title
        project.description = new_desc
        project.status = new_status
        project.priority = new_priority
        project.start_date = new_start
        project.deadline = new_deadline

        # Document update
        if new_document:
            project.project_document = new_document
            log_activity(
                f"📄 Document updated for project '{old_title}'",
                "project",
                request.user
            )

        # Team Lead update
        if new_lead_id:
            new_lead = Member.objects.get(id=new_lead_id)
            if old_lead != new_lead:
                log_activity(
                    f"👨‍💻 Team Lead changed: {old_lead.full_name if old_lead else 'None'} → {new_lead.full_name}",
                    "developer",
                    request.user
                )
            project.team_lead = new_lead

        project.save()

        # --- MEMBERS UPDATED ---
        if new_member_ids != old_members:
            removed = old_members - new_member_ids
            added = new_member_ids - old_members

            for m_id in added:
                member = Member.objects.get(id=m_id)
                log_activity(
                    f"➕ Member added: {member.full_name} to project '{new_title}'",
                    "developer",
                    request.user
                )

            for m_id in removed:
                member = Member.objects.get(id=m_id)
                log_activity(
                    f"➖ Member removed: {member.full_name} from project '{new_title}'",
                    "developer",
                    request.user
                )

            project.members.set(new_member_ids)

        # --- TITLE update ---
        if new_title != old_title:
            log_activity(
                f"✏️ Project title changed: '{old_title}' → '{new_title}'",
                "project",
                request.user
            )

        # --- DESCRIPTION update ---
        if new_desc != old_desc:
            log_activity(
                f"📝 Description updated for project '{new_title}'",
                "project",
                request.user
            )

        # --- PRIORITY update ---
        if new_priority != old_priority:
            log_activity(
                f"⚡ Priority changed: {old_priority} → {new_priority} ({new_title})",
                "project",
                request.user
            )

        # --- STATUS update ---
        if new_status != old_status:
            log_activity(
                f"🔄 Status changed: {old_status} → {new_status} ({new_title})",
                "project",
                request.user
            )

            # Completed
            if new_status == "completed":
                log_activity(
                    f"🏁 Project Completed — '{new_title}'",
                    "project",
                    request.user
                )        

        messages.success(request, "Project updated successfully.")
        return redirect("set.projects")

    context = {
        "project": project,
        "members": members,
        "statuses": statuses,
        "priorities": priorities,
        "active_menu": "set_projects",
        "system_name": system_name,
        "organization": organization,
    }
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





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from set.models import Project, Task, Member
from django.utils import timezone

def task_list(request, pid):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    project = get_object_or_404(Project, id=pid)
    tasks = project.tasks.all()
    members = Member.objects.all()

    return render(request, "pages/set/tasks/list.html", {
        "system_name": system_name,
        "organization": organization,   
        "project": project,
        "tasks": tasks,
        "members": members,
    })

def task_add(request, pid):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    project = get_object_or_404(Project, id=pid)
    members = Member.objects.all()

    if request.method == "POST":
        Task.objects.create(
            project=project,
            title=request.POST["title"],
            description=request.POST.get("description"),
            assigned_to_id=request.POST.get("assigned_to"),
            status=request.POST.get("status"),
            start_date=request.POST.get("start_date"),
            due_date=request.POST.get("due_date"),
        )
        messages.success(request, "Task created successfully!")
        return redirect("set.task-list", pid=project.id)

    return render(request, "pages/set/tasks/add.html", {
        "system_name": system_name,
        "organization": organization,   
        "project": project,
        "members": members,
    })


def task_edit(request, tid):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    task = get_object_or_404(Task, id=tid)
    members = Member.objects.all()

    if request.method == "POST":
        task.title = request.POST["title"]
        task.description = request.POST.get("description")
        task.assigned_to_id = request.POST.get("assigned_to")
        task.status = request.POST.get("status")
        task.start_date = request.POST.get("start_date")
        task.due_date = request.POST.get("due_date")

        if task.status == "DONE":
            task.completed_at = timezone.now()

        task.save()
        messages.success(request, "Task updated successfully!")
        return redirect("set.task-list", pid=task.project.id)

    return render(request, "pages/set/tasks/edit.html", {
        "system_name": system_name,
        "organization": organization,   
        "task": task,
        "members": members,
    })


def task_delete(request, tid):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    task = get_object_or_404(Task, id=tid)
    pid = task.project.id
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect("set.task-list", pid=pid, system_name=system_name, organization=organization)


# views.py
from .models import SoftwareActivity

def activity_logs(request):
    logs = SoftwareActivity.objects.all().order_by('-timestamp')

    q = request.GET.get("q")
    if q:
        logs = logs.filter(message__icontains=q)

    t = request.GET.get("type")
    if t:
        logs = logs.filter(type=t)

    return render(request, "pages/set/logs.html", {"logs": logs})
