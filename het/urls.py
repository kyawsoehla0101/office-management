from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='het.index'),
    path('members/', views.members, name='het.members'),
    path('add-member/', views.addMember, name='het.add-member'),
    path('edit-member/<uuid:id>/', views.editMember, name='het.edit-member'),
    path('member-detail/<uuid:id>/', views.memberDetail, name='het.member-detail'),
    path('delete-member/<uuid:id>/', views.deleteMember, name='het.delete-member'),
    path('requirements/', views.requirements, name='het.requirements'),
    path("requirements/summary/", views.requirements_summary, name="het.requirements-summary"),
    path("requirements/<uuid:id>/", views.viewRequirement, name="het.view-requirement"),
    path("requirements/<uuid:id>/edit/", views.editRequirement, name="het.edit-requirement"),
    path("requirements/<uuid:id>/delete/", views.deleteRequirement, name="het.delete-requirement"),

    path('requirements/add/', views.addRequirement, name='het.add-requirement'),
    path('reports/', views.reports, name='het.reports'),
    path("reports/export/csv/", views.export_reports_csv, name="het.export-reports-csv"),
    path("reports/export/pdf/", views.export_reports_pdf, name="het.export-reports-pdf"),
    path('report/add/', views.addReport, name='het.add-report'),
    path('repair/', views.repairs, name='het.repairs'),
    path("export-repair/<uuid:id>/", views.export_repair_pdf, name="het.export-repair-pdf"),
    path("delete-repair/<uuid:id>/", views.deleteRepair, name="het.delete-repair"),
    path('repair/add/', views.addRepair, name='het.add-repair'),    
    path('repair/edit/<uuid:id>/', views.editRepair, name='het.edit-repair'),
    path('repair/view/<uuid:id>/', views.view_repair, name='het.view-repair'),
]
