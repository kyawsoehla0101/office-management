from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from calendar import month_name
from training.models import TrainingSpendingMoney
from django.contrib import messages
from base.models import SystemSettings
from accounts.utils.decorators import role_required
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