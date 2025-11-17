from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-user/', views.add_user, name='admin.add-user'),
    path('edit-user/<uuid:user_id>/', views.edit_user, name='admin.edit-user'),
    path('delete-user/<uuid:user_id>/', views.delete_user, name='admin.delete-user'),
    path("users/<uuid:user_id>/change-password/", views.change_user_password, name="change-user-password"),

]
