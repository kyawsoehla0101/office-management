from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-user/', views.add_user, name='admin.add-user'),
    path('edit-user/<uuid:user_id>/', views.edit_user, name='admin.edit-user'),
    path('delete-user/<uuid:user_id>/', views.delete_user, name='admin.delete-user'),
    path("users/<uuid:user_id>/change-password/", views.change_user_password, name="change-user-password"),
    path("device/not-allowed/", views.device_not_allowed, name="device_not_allowed"),
    path("devices/", views.device_list, name="admin.device-list"),
    path("devices/<int:id>/allow/", views.allow_device, name="device-allow"),
    path("devices/<int:id>/block/", views.block_device, name="device-block"),
    path("device/<int:pk>/update-label/", views.device_update_label_ajax, name="device-update-label"),

    path("device/<int:id>/toggle-allow/", views.device_toggle_allow, name="device-toggle"),
    path("device/<int:id>/update-label/", views.device_update_label, name="device-update-label"),
    path("device/<int:id>/remove/", views.device_remove, name="device-remove"),

]
