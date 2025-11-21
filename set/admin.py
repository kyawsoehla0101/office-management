from django.contrib import admin
from .models import Member, Project, SoftwareSpendingMoney, Task, SoftwareActivity

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "is_active", "joined_date", "department")
    list_filter = ("position", "is_active")
    search_fields = ("full_name", "position")
    ordering = ("-joined_date",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "priority", "team_lead", "created_by", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("title", "description")
    filter_horizontal = ("members",)

admin.site.register(SoftwareSpendingMoney)
admin.site.register(Task)
admin.site.register(SoftwareActivity)
