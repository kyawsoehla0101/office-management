from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from calendar import month_name
from training.models import TrainingSpendingMoney
from django.contrib import messages
from base.models import SystemSettings
from accounts.utils.decorators import role_required
from .models import Member
@login_required 
@role_required("admin", "training")
def index(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    context = {
        "system_name":system_name,
        "organization": organization,
        "active_menu": "training_index",
        "active_students": 256,
        "new_students_this_month": 14,
        "ongoing_courses": 12,
        "certificates_issued": 480,
        "new_certificates_today": 5,
        "active_instructors": 8,
        "courses_per_instructor": 3,
        "last_course_update": timezone.now() - timedelta(days=1),
        "top_courses": [
            {"name": "Python for Beginners", "instructor": "Mr. Hla Win", "students": 48, "completion_rate": 92},
            {"name": "Advanced Django", "instructor": "Ms. Thandar", "students": 36, "completion_rate": 85},
            {"name": "AI & Machine Learning", "instructor": "Dr. Kyaw Soe", "students": 40, "completion_rate": 78},
        ],
        "recent_activities": [
            {"type": "enroll", "message": "👨‍🎓 New student enrolled in 'Python for Beginners'", "timestamp": timezone.now() - timedelta(hours=2)},
            {"type": "complete", "message": "🎉 3 students completed 'Advanced Django'", "timestamp": timezone.now() - timedelta(hours=4)},
            {"type": "enroll", "message": "📚 New batch started for 'AI & ML Basics'", "timestamp": timezone.now() - timedelta(hours=7)},
        ],
    }
    return render(request, "pages/training/index.html", context)
@login_required(login_url="login")
@role_required("training", "admin")
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
        "active_menu": "training_members",
        "system_name": system_name,
        "organization": organization,
    }
    return render(request, 'pages/training/members/members.html', context)

@role_required("training", "admin")
def addMember(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    positions = Member.POSITION_CHOICES
    ranks = Member.RANK_CHOICES
    genders = Member.GENDER_CHOICES
    context = {
        "active_menu": "training_members",
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
        # 🔥 Activity Log
        # log_activity_dev(
        #     message=f"👤 New member added — {member.full_name}",
        #     event_type="developer",
        #     user=request.user
        # )
        
        messages.success(request, f"Member '{full_name}' added to {department} team.")
        return redirect("training.members")

    return render(request, "pages/training/members/add-member.html", context)

@role_required("training", "admin")
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
        # if new_name != old_name:
        #     log_activity_dev(
        #         f"📝 Member name changed: {old_name} → {new_name}",
        #         "member",
        #         request.user
        #     )

        # if new_rank != old_rank:
        #     log_activity_dev(
        #         f"🎖 Rank updated: {old_rank} → {new_rank} ({new_name})",
        #         "member",
        #         request.user
        #     )

        # if new_position != old_position:
        #     log_activity_dev(
        #         f"👨‍💻 Position changed: {old_position} → {new_position} ({new_name})",
        #         "member",
        #         request.user
        #     )

        # if new_gender != old_gender:
        #     log_activity_dev(
        #         f"⚧ Gender changed: {old_gender} → {new_gender} ({new_name})",
        #         "member",
        #         request.user
        #     )

        # if new_birth_date != old_birth:
        #     log_activity_dev(
        #         f"🎂 Birthdate updated: {old_birth} → {new_birth_date} ({new_name})",
        #         "member",
        #         request.user
        #     )

        # if new_joined_date != old_joined:
        #     log_activity_dev(
        #         f"📅 Joined date changed: {old_joined} → {new_joined_date} ({new_name})",
        #         "member",
        #         request.user
        #     )

        # if new_active != old_active:
        #     status = "Active" if new_active else "Inactive"
        #     old_status = "Active" if old_active else "Inactive"
        #     log_activity_dev(
        #         f"🔄 Member status changed: {old_status} → {status} ({new_name})",
        #         "member",
        #         request.user
        #     )

        # if new_bio != old_bio:
        #     log_activity_dev(
        #         f"🗒 Bio updated for {new_name}",
        #         "member",
        #         request.user
        #     )

        # if new_photo:
        #     log_activity_dev(
        #         f"🖼 Profile photo updated for {new_name}",
        #         "member",
        #         request.user
        #     )

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
        return redirect("training.members")

    context = {
        "active_menu": "training_members",
        "system_name": system_name,
        "organization": organization,
        "member": member,
        "ranks": Member.RANK_CHOICES,
        "positions": Member.POSITION_CHOICES,
        "genders": Member.GENDER_CHOICES,
    }
    return render(request, "pages/training/members/edit-member.html", context)

@role_required("training", "admin")
def memberDetail(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    member = get_object_or_404(Member, id=id)
    context = {
        "active_menu": "training_members",
        "system_name": system_name,
        "organization": organization,
        "member": member,
    }
    return render(request, 'pages/training/members/member-detail.html', context) 
@role_required("training", "admin")
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
        # log_activity_dev(
        #     f"🗑 Member deleted: {deleted_name} (Rank: {deleted_rank}, Position: {deleted_position})",
        #     "member",
        #     request.user
        # )

        messages.success(request, f"Member '{deleted_name}' deleted successfully.")
        return redirect("training.members")

    context = {
        "active_menu": "training_members",
        "system_name": system_name,
        "organization": organization,
        "member": member,
    }
    return render(request, "pages/training/members/member-delete.html", context)



def students(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    students = [
        {
            "name": "Aung Kyaw",
            "email": "aungkyaw@example.com",
            "phone": "0967890123",
            "course_name": "Python for Beginners",
            "enrolled_at": timezone.now() - timedelta(days=10),
        },
        {
            "name": "Mg Mg",
            "email": "mgmg@example.com",
            "phone": "0967890456",
            "course_name": "Advanced Django",
            "enrolled_at": timezone.now() - timedelta(days=5),
        },
        {
            "name": "Htet Naing",
            "email": "htetnaing@example.com",
            "phone": "0967890789",
            "course_name": "AI & Machine Learning",
            "enrolled_at": timezone.now() - timedelta(days=2),
        },
    ]
    context = {
        "system_name":system_name,
        "organization": organization,
        "active_menu": "training_members",
        "students": students,
    }
    return render(request, 'pages/training/students/students.html', context)



@role_required("training", "admin")
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
        requirements = TrainingSpendingMoney.objects.filter(year=selected_year)
    else:
        try:
            selected_month_int = int(selected_month)
        except ValueError:
            selected_month_int = current_month

        requirements = TrainingSpendingMoney.objects.filter(  
            month=selected_month_int, year=selected_year
        )

    # 🧾 Calculate total
    total_cost = sum(r.total_cost() for r in requirements)

    # Dropdown lists
    months = [("all", "All Months")] + [(i, month_name[i]) for i in range(1, 13)]
    years = range(current_year - 5, current_year + 3)

    context = {
        "system_name":system_name,
        "organization": organization,
        "requirements": requirements,
        "total_cost": total_cost,
        "months": months,
        "years": years,
        "selected_month": selected_month,
        "selected_year": int(selected_year),
        "active_menu": "training_requirements",
    }
    return render(request, "pages/training/requirements/requirements.html", context)

@role_required("training", "admin")
def requirements_summary(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    today = timezone.now()
    current_year = today.year

    # Group by month and sum total cost
    monthly_totals = (
        TrainingSpendingMoney.objects
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
        "system_name":system_name,
        "organization": organization,
        "monthly_totals": monthly_totals,
        "yearly_total": yearly_total,
        "year": current_year,
        "active_menu": "training_requirements_summary",
    }
    return render(request, "pages/training/requirements/requirement-summary.html", context)

@role_required("training", "admin")
def addRequirement(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    from .models import TrainingSpendingMoney
    if request.method == "POST":
        item = TrainingSpendingMoney(
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
        return redirect("training.requirements")

    month_choices = TrainingSpendingMoney.MONTH_CHOICES
    return render(request, "pages/training/requirements/add-requirement.html", {"month_choices": month_choices, "active_menu": "training_requirements","system_name":system_name,"organization": organization})
@role_required("training", "admin")
def viewRequirement(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    requirement = get_object_or_404(TrainingSpendingMoney, id=id)
    return render(request, "pages/training/requirements/view-requirement.html", {"requirement": requirement, "active_menu": "training_requirements","system_name":system_name,"organization": organization})

@role_required("training", "admin")
def editRequirement(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    requirement = get_object_or_404(TrainingSpendingMoney, id=id)
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
        return redirect("training.requirements")

    return render(request, "pages/training/requirements/edit-requirement.html", {
        "requirement": requirement,
        "system_name":system_name,
        "organization": organization,
        "months": months,
        "years": years,
        "categories": categories,
        "active_menu": "training_requirements",
    })
@role_required("training", "admin")
def deleteRequirement(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    requirement = get_object_or_404(TrainingSpendingMoney, id=id)
    if request.method == "POST":
        requirement.delete()
        return redirect("training.requirements")

    return render(request, "pages/training/requirements/delete-requirement.html", {"requirement": requirement, "active_menu": "training_requirements","system_name":system_name,"organization": organization})