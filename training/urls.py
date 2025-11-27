from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='training.index'),
    path('members/', views.members, name='training.members'),
    path('add-member/', views.addMember, name='training.add-member'),
    path('edit-member/<uuid:id>/', views.editMember, name='training.edit-member'),
    path('member-detail/<uuid:id>/', views.memberDetail, name='training.member-detail'),
    path('delete-member/<uuid:id>/', views.deleteMember, name='training.delete-member'),
    path('students/', views.students, name='training.students'),
    path('requirements/', views.requirements, name='training.requirements'),
    path("requirements/summary/", views.requirements_summary, name="training.requirements-summary"),
    path("requirements/<uuid:id>/", views.viewRequirement, name="training.view-requirement"),
    path("requirements/<uuid:id>/edit/", views.editRequirement, name="training.edit-requirement"),
    path("requirements/<uuid:id>/delete/", views.deleteRequirement, name="training.delete-requirement"),
    path('requirements/add/', views.addRequirement, name='training.add-requirement'),
]
