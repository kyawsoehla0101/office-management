from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='training.index'),
    path('students/', views.students, name='training.students'),
    path('requirements/', views.requirements, name='training.requirements'),
    path("requirements/summary/", views.requirements_summary, name="training.requirements-summary"),
    path("requirements/<uuid:id>/", views.viewRequirement, name="training.view-requirement"),
    path("requirements/<uuid:id>/edit/", views.editRequirement, name="training.edit-requirement"),
    path("requirements/<uuid:id>/delete/", views.deleteRequirement, name="training.delete-requirement"),
    path('requirements/add/', views.addRequirement, name='training.add-requirement'),
]
