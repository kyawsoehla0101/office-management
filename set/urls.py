from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='set.index'),
    path('members/', views.members, name='set.members'),
    path('add-report/', views.addReport, name='set.add-report'),
    path('projects/', views.projects, name='set.projects'),
    path('add-member/', views.addMember, name='set.add-member'),
    path('edit-member/<uuid:id>/', views.editMember, name='set.edit-member'),
    path('member-detail/<uuid:id>/', views.memberDetail, name='set.member-detail'),
    path('delete-member/<uuid:id>/', views.deleteMember, name='set.delete-member'),
    path('requirements/', views.requirements, name='set.requirements'),
    path("requirements/summary/", views.requirements_summary, name="set.requirements-summary"),
    path("requirements/<uuid:id>/", views.viewRequirement, name="set.view-requirement"),
    path("requirements/<uuid:id>/edit/", views.editRequirement, name="set.edit-requirement"),
    path("requirements/<uuid:id>/delete/", views.deleteRequirement, name="set.delete-requirement"),
    path("reports/pdf/", views.export_projects_pdf, name="set.export_pdf"),
    path('requirements/add/', views.addRequirement, name='set.add-requirement'),
    path('report/', views.report, name='set.report'),
    path('add-project/', views.addProject, name='set.add-project'),
    path('edit-project/<uuid:id>/', views.editProject, name='set.edit-project'),
    path('project-detail/<uuid:id>/', views.detailProject, name='set.project-detail'),
    path('delete-project/<uuid:id>/', views.deleteProject, name='set.delete-project'),


    path("spending/", views.spending_page, name="set.spending-page"),
    path("spending/export/pdf/", views.export_spending_pdf, name="set.spending-export-pdf"),
    path("api/spending/", views.SpendingMoneyListCreateAPIView.as_view(), name="set.spending-list-api"),
    path("api/spending/<uuid:pk>/", views.SpendingMoneyDetailAPIView.as_view(), name="set.spending-detail-api"),


    path("project/<uuid:pid>/tasks/", views.task_list, name="set.task-list"),
    path("project/<uuid:pid>/tasks/add/", views.task_add, name="set.task-add"),
    path("tasks/<uuid:tid>/edit/", views.task_edit, name="set.task-edit"),
    path("tasks/<uuid:tid>/delete/", views.task_delete, name="set.task-delete"),
]
