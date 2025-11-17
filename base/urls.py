from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.users, name='admin.users'),
    path('settings/', views.admin_settings, name='admin.settings'),
    path('all/spending-money/', views.admin_all_spending_money, name='admin.all-spending-money'),
    path('all/spending-money/summary/', views.admin_spending_money_summary, name='admin.spending-money-summary'),
    path("spending/", views.spending_page, name="admin.spending-page"),
    path("spending/export/pdf/", views.export_spending_pdf, name="spending-export-pdf"),
    path("api/spending/", views.SpendingMoneyListCreateAPIView.as_view(), name="spending-list-api"),
    path("api/spending/<uuid:pk>/", views.SpendingMoneyDetailAPIView.as_view(), name="spending-detail-api"),
    path("team-members/", views.all_team_members, name="admin.team-members"),
]
