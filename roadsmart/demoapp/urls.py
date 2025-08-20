from django.urls import path
from . import views

app_name = "demoapp"

urlpatterns = [
    # ======================
    # Public/Auth URLs
    # ======================
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # ======================
    # Admin URLs
    # ======================
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/admin/users/", views.view_users, name="view_users"),
    path("dashboard/admin/reports/", views.view_reports, name="view_reports"),
    path("dashboard/admin/settings/", views.admin_settings, name="admin_settings"),

    # ======================
    # Municipal Team URLs
    # ======================
    path("dashboard/municipal/", views.municipal_dashboard, name="municipal_dashboard"),
    path("dashboard/municipal/reports/", views.municipal_reports, name="municipal_reports"),
    path("dashboard/municipal/report/<int:report_id>/", views.report_detail, name="report_detail"),
    path("dashboard/municipal/assign-task/<int:report_id>/", views.assign_task, name="assign_task"),
    path("dashboard/municipal/update-status/<int:report_id>/", views.update_report_status, name="update_status"),

    # ======================
    # Repair Team URLs
    # ======================
    path("dashboard/repair-team/", views.repair_team_dashboard, name="repair_team_dashboard"),
    path("dashboard/repair-team/tasks/", views.repair_tasks, name="repair_tasks"),
    path("dashboard/repair-team/task/<int:task_id>/", views.task_detail, name="task_detail"),
    path("dashboard/repair-team/complete-task/<int:task_id>/", views.complete_task, name="complete_task"),

    # ======================
    # Citizen URLs
    # ======================
    path("dashboard/citizen/", views.citizen_dashboard, name="citizen_dashboard"),
    path("dashboard/citizen/reports/", views.citizen_reports, name="citizen_reports"),
    path("report-issue/", views.report_issue, name="report_issue"),
]
