from django.db.models import Sum

import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Member, HardwareRepair, HardwareSpendingMoney     
from accounts.utils.decorators import role_required
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
from calendar import month_name
from django.db.models import F
from base.models import SystemSettings
from django.contrib.auth.decorators import login_required
from base.utils import date_utils



# Dashboard View
@role_required("het","admin")
def dashboard(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    recent_repairs = HardwareRepair.objects.order_by('-updated_at')[:5]
    context = {
        "system_name": system_name,
        "organization": organization,
        "recent_repairs": recent_repairs,
        "active_menu": "het_index",
        "active_machines": 23,
        "new_devices_this_week": 4,
        "under_maintenance": 5,
        "repairs_completed": 17,
        "system_uptime": 99.2,
        "last_repair_update": timezone.now() - timedelta(days=1),
        "maintenance_logs": [
            {"device_name": "3D Printer 01", "technician": "Aung Ko", "status": "Completed", "last_checked": timezone.now() - timedelta(hours=3)},
            {"device_name": "Laser Cutter", "technician": "Thazin Win", "status": "Pending", "last_checked": timezone.now() - timedelta(hours=5)},
            {"device_name": "Microcontroller Batch #12", "technician": "Myo Min", "status": "In Progress", "last_checked": timezone.now() - timedelta(hours=6)},
        ],
        "recent_activities": [
            {"type": "repair", "message": "✅ Power supply of CNC machine replaced successfully", "timestamp": timezone.now() - timedelta(hours=1)},
            {"type": "issue", "message": "⚠️ Temperature sensor malfunction detected", "timestamp": timezone.now() - timedelta(hours=3)},
            {"type": "repair", "message": "🛠️ 3D printer nozzle cleaned and recalibrated", "timestamp": timezone.now() - timedelta(hours=5)},
        ],
    }
    return render(request, 'pages/het/index.html', context)

# Members View
@role_required("het", "admin")
def members(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    members = Member.objects.all()
    total_members = members.count()
    total_active_members = members.filter(is_active=True).count()
    total_inactive_members = members.filter(is_active=False).count()
    total_male_members = members.filter(gender='male').count()
    total_female_members = members.filter(gender='female').count()
    context = {
        "system_name": system_name,
        "organization": organization,
        "active_menu": "het_members",
        "members": members,
        "total_members": total_members,
        "total_active_members": total_active_members,
        "total_inactive_members": total_inactive_members,
        "total_male_members": total_male_members,
        "total_female_members": total_female_members,
    }
    return render(request, 'pages/het/members/members.html', context)

# Add Member View
@role_required("het", "admin")
def addMember(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    positions = Member.POSITION_CHOICES
    ranks = Member.RANK_CHOICES
    genders = Member.GENDER_CHOICES
    context = {
        "system_name": system_name,
        "organization": organization,
        "active_menu": "het_members",
        "positions": positions,
        "ranks": ranks, 
        "genders": genders,
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
        return redirect("het.members")

    return render(request, "pages/het/members/add-member.html", context)

# Edit Member View
@role_required("het", "admin")
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
        return redirect("het.members")

    context = {
        "system_name": system_name,
        "organization": organization,
        "active_menu": "het_members",
        "member": member,
        "ranks": Member.RANK_CHOICES,
        "positions": Member.POSITION_CHOICES,
        "genders": Member.GENDER_CHOICES,
    }
    return render(request, "pages/het/members/edit-member.html", context)

# Member Detail View
@role_required("het", "admin")
def memberDetail(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    member = get_object_or_404(Member, id=id)
    context = {
        "system_name": system_name,
        "organization": organization,
        "active_menu": "het_members",
        "member": member,
    }
    return render(request, 'pages/het/members/member-detail.html', context) 

# Delete Member View
@role_required("het", "admin")   
def deleteMember(request,id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    member = get_object_or_404(Member, id=id)
    context = {
        "system_name": system_name,
        "organization": organization,
        "active_menu": "het_members",
        "member": member,
    }
    if request.method == "POST":
        member.delete()
        messages.success(request, f"Member '{member.full_name}' deleted successfully.")
        return redirect('het.members')
    return render(request, 'pages/het/members/member-delete.html', context)


def reports(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")

    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # GET (user selected)
    selected_month = request.GET.get("month", "all")
    selected_year = request.GET.get("year", "all")

    # Month choices (1–12  + display name)
    import calendar
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # Years (list around current year)
    years = [y for y in range(current_year - 3, current_year + 2)]

    # ---------- Queryset ----------
    repairs = HardwareRepair.objects.all().order_by("-created_at")

    # Search
    if q:
        repairs = repairs.filter(
            Q(device_name__icontains=q) |
            Q(technician__full_name__icontains=q) |
            Q(ticket_id__icontains=q)
        )

    # Status
    if status:
        repairs = repairs.filter(status=status)

    # Month filter (created_at)
    if selected_month != "all":
        repairs = repairs.filter(created_at__month=selected_month)

    # Year filter (created_at)
    if selected_year != "all":
        repairs = repairs.filter(created_at__year=selected_year)

    return render(request, "pages/het/reports/reports.html", {
        "months": months,
        "years": years,
        "system_name": system_name,
        "organization": organization,
        "current_month": current_month,
        "current_year": current_year,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "repairs": repairs,
        "active_menu": "het_reports",
        "status_choices": HardwareRepair.STATUS_CHOICES,
    })

@role_required("het", "admin")
def export_reports_csv(request):
    """Export repair reports to CSV"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="repair_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(["Ticket ID", "Device Name", "Technician", "Status", "Completed Date", "Cost Estimate (MMK)"])

    repairs = HardwareRepair.objects.all()
    for r in repairs:
        writer.writerow([
            r.ticket_id,
            r.device_name,
            r.technician.full_name if r.technician else "-",
            r.get_status_display(),
            r.completed_date or "-",
            r.cost_estimate or "0",
        ])
    return response

@role_required("het", "admin")
# def export_reports_pdf(request):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),topMargin=5,       # အပေါ် margin ကို လျှော့
#     bottomMargin=5,
#     leftMargin=30,
#     rightMargin=30,)
#     elements = []
#     styles = getSampleStyleSheet()

#     header = Paragraph("<b>Arakan Army</b>", ParagraphStyle(name="Header",fontSize=14, parent=styles["Title"]))
#     header2 = Paragraph("<b>Hardware Engineering Team</b>", ParagraphStyle(name="Header2",fontSize=11, parent=styles["Title"]))
#     title = Paragraph("<b>Hardware Repair Report Summary</b>", ParagraphStyle(name="Title",fontSize=16, parent=styles["Title"]))
#     elements.append(header)
#     elements.append(Spacer(1, 2))
#     elements.append(header2)
#     elements.append(Spacer(1, 2))
#     elements.append(title)
#     elements.append(Spacer(1, 12))

#     # ---------- Table Data ----------
#     data = [["Ticket ID", "Device Name", "Technician", "Status", "Start Date", "Completed Date", "Cost (MMK)"]]
#     repairs = HardwareRepair.objects.all().order_by("-completed_date")

#     for r in repairs:
#         data.append([
#             r.ticket_id,
#             r.device_name,
#             r.technician.full_name if r.technician else "-",
#             r.get_status_display(),
#             r.start_date.strftime("%Y-%m-%d") if r.start_date else "-",
#             r.completed_date.strftime("%Y-%m-%d") if r.completed_date else "-",
#             f"{r.cost_estimate or 0:.2f}",
#         ])

#     # ---------- Date Header Row (aligned with table) ----------
#     current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
#     date = Paragraph(
#                 f"<para alignment='right'><b>Date:</b> {current_date}</para>",
#                 styles["Normal"],
#             )
#     elements.append(date)
#     elements.append(Spacer(1, 12))

#     # ---------- Main Table ----------
#     main_table = Table(data, colWidths=[90, 140, 120, 90, 100, 120])
#     main_table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
#         ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#         ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("FONTSIZE", (0, 0), (-1, 0), 11),
#         ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
#         ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
#         ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
#     ]))

#     # ---------- Combine ----------
#     elements.append(Spacer(1, 6))
#     elements.append(main_table)

#     doc.build(elements)
#     pdf = buffer.getvalue()
#     buffer.close()

#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = 'attachment; filename="repair_reports_table.pdf"'
#     response.write(pdf)
#     return response

@role_required("het", "admin")
def addReport(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    return render(request, 'pages/het/reports/add-report.html', {
        "system_name": system_name,
        "organization": organization,   
        "active_menu": "het_reports"
    })


@role_required("het", "admin")
def repairs(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")
    
    repairs = HardwareRepair.objects.select_related("technician").prefetch_related("support_team").all()
    if q:
        repairs = repairs.filter(device_name__icontains=q) | repairs.filter(technician__full_name__icontains=q) | repairs.filter(ticket_id__icontains=q)
    if status:
        repairs = repairs.filter(status=status)

    context = {
        "system_name": system_name,
        "organization": organization,   
        "active_menu": "het_repairs",
        "repairs": repairs,
        "status_choices": HardwareRepair.STATUS_CHOICES,
        "total_repairs": repairs.count(),
        "pending_repairs": repairs.filter(status="pending").count(),
        "progress_repairs": repairs.filter(status="in_progress").count(),
        "completed_repairs": repairs.filter(status="completed").count(),
    }
    context.update({
    "current_month": timezone.now().month,
    "current_year": timezone.now().year,
    "years": range(2020, 2031),
})
    return render(request, "pages/het/repairs/repairs.html", context)

@role_required("het", "admin")
def addRepair(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization

    if request.method == "POST":
        try:
            data = request.POST
            repair = HardwareRepair.objects.create(
                device_name=data.get("device_name"),
                device_type=data.get("device_type"),
                issue_description=data.get("issue_description"),
                technician_id=data.get("technician") or None,
                priority=data.get("priority"),
                cost_estimate=data.get("cost_estimate") or None,
            # created_by=request.user,
            )

            repair.support_team.set(request.POST.getlist("support_team"))
            if request.FILES.get("photo_before"):
                repair.photo_before = request.FILES["photo_before"]
            if request.FILES.get("report_document"):
                repair.report_document = request.FILES["report_document"]
            repair.save()
            messages.success(request, "Repair record added successfully!")
            # -----------------------------
            # 🔐 Generate PDF via WeasyPrint
            # -----------------------------
            current_date = to_myanmar_date(timezone.now())

            html_string = render_to_string(
                "pages/het/repairs/receipt-pdf.html",
                {
                    "repair": repair,
                    "current_date": current_date,
                }
            )

            pdf_file = HTML(string=html_string).write_pdf()

            response = HttpResponse(pdf_file, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{repair.ticket_id}.pdf"'
            return response

        except Exception as e:
            print("Error", e)
            return HttpResponse("Error", status=500)
        

    context = {
        "members": Member.objects.all(),
        "device_types": HardwareRepair.DEVICE_TYPE_CHOICES,
        "priorities": HardwareRepair.PRIORITY_CHOICES,
        "active_menu": "het_repairs",
        "system_name": system_name,
        "organization": organization,   
    }
    return render(request, "pages/het/repairs/add-repair.html", context)

@role_required("het", "admin")
def editRepair(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    repair = get_object_or_404(HardwareRepair, id=id)

    if request.method == "POST":
        data = request.POST
        repair.device_name = data.get("device_name")
        repair.device_type = data.get("device_type")
        repair.technician_id = data.get("technician") or None
        repair.priority = data.get("priority")
        repair.status = data.get("status")
        repair.repair_notes = data.get("repair_notes")
        repair.cost_estimate = data.get("cost_estimate") or None
        repair.start_date = data.get("start_date") or None
        repair.completed_date = data.get("completed_date") or None
        repair.support_team.set(request.POST.getlist("support_team"))

        if request.FILES.get("photo_after"):
            repair.photo_after = request.FILES["photo_after"]
        if request.FILES.get("report_document"):
            repair.report_document = request.FILES["report_document"]

        repair.save()
        messages.success(request, "Repair updated successfully!")
        return redirect("het.repairs")

    context = {
        "system_name": system_name,
        "organization": organization,   
        "repair": repair,
        "members": Member.objects.all(),
        "device_types": HardwareRepair.DEVICE_TYPE_CHOICES,
        "status_choices": HardwareRepair.STATUS_CHOICES,
        "priorities": HardwareRepair.PRIORITY_CHOICES,
        "active_menu": "het_repairs",
    }
    return render(request, "pages/het/repairs/edit-repair.html", context)

@role_required("het", "admin")
def deleteRepair(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    repair = get_object_or_404(HardwareRepair, id=id)
    context = {
        "system_name": system_name,
        "organization": organization,       
        "repair": repair,
        "active_menu": "het_repairs",
    }
    if request.method == "POST":
        repair.delete()
        messages.success(request, f"Repair record {repair.ticket_id} deleted successfully.")
        return redirect("het.repairs")
    return render(request, "pages/het/repairs/delete-repair.html", context)

@role_required("het", "admin")
def view_repair(request, id):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    repair = get_object_or_404(HardwareRepair, id=id)
    context = {
        "system_name": system_name,
        "organization": organization,           
        "repair": repair,
        "active_menu": "het_repairs",
    }
    return render(request, "pages/het/repairs/view-repair.html", context)



from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.conf import settings
import os
from datetime import datetime
from .utils.date_utils import to_myanmar_date



@role_required("het", "admin")

def export_reports_pdf(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization
    selected_month = request.GET.get("month","all")
    selected_year = request.GET.get("year","all")
    
    # Default = current month/year
    today = timezone.now()
    month = request.GET.get("month", "all")     # string
    year = request.GET.get("year", "all")       # string
    repairs = HardwareRepair.objects.all().order_by("-created_at")
    if year != "all":
        try:
            year_int = int(year)
            repairs = repairs.filter(created_at__year=year_int)
        except:
            pass

    # ----------------------------
    # MONTH FILTER
    # ----------------------------
    if month != "all":
        try:
            month_int = int(month)
            repairs = repairs.filter(created_at__month=month_int)
        except:
            pass


    # Filter Repairs
    

    # Summary values
    total_repairs = repairs.count()
    completed_count = repairs.filter(status="completed").count()
    in_progress_count = repairs.filter(status="in_progress").count()
    pending_count = repairs.filter(status="pending").count()
    cancelled_count = repairs.filter(status="cancelled").count()
    total_cost = repairs.aggregate(total=Sum("cost_estimate"))["total"] or 0

    context = {
        "system_name": system_name,
        "organization": organization,   
        "repairs": repairs,
        "current_date": to_myanmar_date(today),
        "total_repairs": total_repairs,
        "completed_count": completed_count,
        "in_progress_count": in_progress_count,
        "pending_count": pending_count,
        "cancelled_count": cancelled_count,
        "total_cost": total_cost,
        "selected_month": selected_month,
        "selected_year": selected_year,
    }

    html = render_to_string("pages/het/reports/repairs_report_pdf.html", context)
    pdf = HTML(string=html).write_pdf()

    

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Repair_Report_{selected_year}_{selected_month}.pdf"'
    return response

def export_repair_pdf(request, id):
    repair = get_object_or_404(HardwareRepair, id=id)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50)
    styles = getSampleStyleSheet()
    elements = []

    # --- Header ---
    title1 = Paragraph(
        f"<b>Arakan Army</b>",
        styles["Title"]
    )
    title2 = Paragraph(
        f"<b>Hardware Engineering Team</b>",
        styles["Title"]
    )
    title = Paragraph(
        f"<b>Repair Report - {repair.ticket_id}</b>",
        styles["Title"]
    )
    elements.append(title1)
    elements.append(title2)
    elements.append(title)
    elements.append(Spacer(1, 12))
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    date = Paragraph(
                f"<para alignment='right'><b>Date:</b> {current_date}</para>",
                styles["Normal"],
            )
    elements.append(date)
    elements.append(Spacer(1, 12))

    # --- Info Table ---
    data = [
        ["Device Name", repair.device_name],
        ["Device Type", repair.get_device_type_display()],
        ["Technician", str(repair.technician.full_name or '-')],
        ["Status", repair.get_status_display()],
        ["Priority", repair.get_priority_display()],
        ["Received Date", repair.received_date.strftime('%Y-%m-%d')],
        ["Start Date", repair.start_date.strftime('%Y-%m-%d') if repair.start_date else '-'],
        ["Completed Date", repair.completed_date.strftime('%Y-%m-%d') if repair.completed_date else '-'],
        ["Cost Estimate", f"{repair.cost_estimate or 0} MMK"],
        ["Estimated Completion", repair.estimated_completion.strftime('%Y-%m-%d') if repair.estimated_completion else '-'],
        ["Support Team", ", ".join([member.full_name for member in repair.support_team.all()]) or '-'],
    ]
    table = Table(data, colWidths=[150, 330])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3f2fd")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # --- Issue Description ---
    elements.append(Paragraph(f"<b>Issue Description:</b><br/>{repair.issue_description}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    # --- Repair Notes ---
    if repair.repair_notes:
        elements.append(Paragraph(f"<b>Repair Notes:</b><br/>{repair.repair_notes}", styles["Normal"]))
        elements.append(Spacer(1, 15))

    # --- Footer ---
    footer = Paragraph(
        f"<para alignment='center' size=9 color='#666'>Generated by Hardware Engineering Team • {datetime.now().strftime('%Y-%m-%d')}</para>",
        styles["Normal"]
    )
    elements.append(footer)

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{repair.ticket_id}.pdf"'
    return response



from rest_framework import generics, permissions
from datetime import datetime
from .serializers import HardwareSpendingMoneySerializer
from .models import HardwareSpendingMoney

# Spending Money API View

class SpendingMoneyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = HardwareSpendingMoneySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = HardwareSpendingMoney.objects.all().order_by("-created_at")
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
    queryset = HardwareSpendingMoney.objects.all()
    serializer_class = HardwareSpendingMoneySerializer
    permission_classes = [permissions.IsAuthenticated]

# Spending Money Page View
@login_required(login_url="/")
@role_required("admin", "het")
def spending_page(request):
    system_name = SystemSettings.objects.first().system_name
    organization = SystemSettings.objects.first().organization  
    
    months = HardwareSpendingMoney.MONTH_CHOICES
    
    years = range(2023, datetime.now().year + 6)
    return render(request, "pages/het/spending-money/spending_page.html", {"months": months, "years": years, "system_name": system_name, "organization": organization, "active_menu": "het_spending_page"})

# Spending Money PDF Export View
@login_required(login_url="/")
@role_required("admin", "het")
def export_spending_pdf(request):
    month = request.GET.get("month", "all")
    year = request.GET.get("year", datetime.now().year)
    qs = HardwareSpendingMoney.objects.all()
    current_date = date_utils.to_myanmar_date_formatted(datetime.now())

    if month != "all":
        qs = qs.filter(month=month)
    if year != "all":
        qs = qs.filter(year=year)
    total_sum = sum([r.total_cost for r in qs])
    html = render_to_string("pages/het/spending-money/spending_pdf.html", {"records": qs, "total_sum": total_sum, "month": month, "year": year, "current_date": current_date})
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="spending_{month}_{year}.pdf"'
    return response