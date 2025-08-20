from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.utils import timezone  # Add this import at the top with other imports
from django.utils.timezone import now
from .models import Report, Complaint, Task, StatusUpdate
from django.contrib.auth import get_user_model

User = get_user_model()

# ========================
# Authentication Views
# ========================
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect_user_based_on_role(user)
    else:
        form = CustomUserCreationForm()
    return render(request, "demoapp/auth/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect_user_based_on_role(user)
    return render(request, "demoapp/auth/login.html")

def user_logout(request):
    logout(request)
    return render(request, "demoapp/auth/logout.html")

# ========================
# Admin Views
# ========================
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('demoapp:home')
    return render(request, "demoapp/admin/dashboard.html")

@login_required
def view_users(request):
    users = User.objects.all()
    return render(request, "demoapp/admin/users.html", {'users': users})

@login_required
def view_reports(request):
    reports = Report.objects.all()
    return render(request, "demoapp/admin/reports.html", {'reports': reports})

@login_required
def admin_settings(request):
    return render(request, "demoapp/admin/settings.html")

# ========================
# Municipal Views
# ========================
@login_required
def municipal_dashboard(request):
    if request.user.role != 'municipal':
        return redirect('demoapp:home')
    pending_reports = Report.objects.filter(status='Pending').count()
    return render(request, "demoapp/municipal/dashboard.html", {
        'pending_reports': pending_reports
    })

@login_required
def municipal_reports(request):
    priority = request.GET.get('priority', None)
    reports = Report.objects.filter(status__in=['Pending', 'Reviewed'])
    
    if priority:
        reports = reports.filter(priority=priority)
    
    # Sort by priority (Critical first, then High, etc.)
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    reports = sorted(reports, key=lambda x: priority_order[x.priority])
    
    return render(request, "demoapp/municipal/reports.html", {'reports': reports})

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render(request, "demoapp/municipal/report_detail.html", {'report': report})

@login_required
def assign_task(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    repair_teams = User.objects.filter(role="repair_team")
    
    if request.method == "POST":
        repair_team = get_object_or_404(User, id=request.POST["repair_team"])
        
        # Update report status and assignment
        report.status = "Assigned"
        report.assigned_to = repair_team
        report.save()
        
        # Create task
        Task.objects.create(
            report=report,
            assigned_by=request.user,
            assigned_to=repair_team,
            task_details=f"Fix {report.title} (Priority: {report.priority})",
            status="Assigned"
        )
        
        messages.success(request, "Task assigned successfully!")
        return redirect('demoapp:municipal_reports')
    
    return render(request, "demoapp/municipal/assign_task.html", {
        'report': report,
        'repair_teams': repair_teams
    })

# ========================
# Repair Team Views
# ========================
@login_required
def repair_team_dashboard(request):
    if request.user.role != 'repair_team':
        return redirect('demoapp:home')
    active_tasks = Task.objects.filter(assigned_to=request.user, status='Assigned').count()
    return render(request, "demoapp/repair_team/dashboard.html", {
        'active_tasks': active_tasks
    })

@login_required
def repair_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, "demoapp/repair_team/tasks.html", {'tasks': tasks})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    return render(request, "demoapp/repair_team/task_detail.html", {'task': task})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    
    if request.method == "POST":
        task.status = "Completed"
        task.completed_at = timezone.now()
        task.save()
        
        # Update report status
        report = task.report
        report.status = "Completed"
        report.save()
        
        messages.success(request, "Task marked as completed!")
        return redirect('demoapp:repair_tasks')
    
    return render(request, "demoapp/repair_team/complete_task.html", {'task': task})

# ========================
# Citizen Views
# ========================
@login_required
def citizen_dashboard(request):
    user_reports = Report.objects.filter(citizen=request.user).order_by('-created_at')[:5]
    return render(request, "demoapp/citizen/dashboard.html", {
        'reports': user_reports
    })

@login_required
def citizen_reports(request):
    reports = Report.objects.filter(citizen=request.user).order_by('-created_at')
    return render(request, "demoapp/citizen/reports.html", {'reports': reports})

@login_required
def report_issue(request):
    if request.method == "POST":
        new_report = Report.objects.create(
            citizen=request.user,
            title=request.POST["title"],
            description=request.POST["description"],
            location=request.POST["location"],
            image=request.FILES.get("image"),
            status="Pending"
        )
        
        StatusUpdate.objects.create(
            report=new_report,
            updated_by=request.user,
            from_status="New",
            to_status="Pending",
            notes="Report submitted via citizen portal"
        )
        
        messages.success(request, "Report submitted successfully!")
        return redirect('demoapp:citizen_dashboard')
    
    return render(request, "demoapp/citizen/report_issue.html")


@login_required
def submit_complaint(request):
    if request.method == "POST":
        complaint = Complaint.objects.create(
            user=request.user,
            issue=request.POST["issue"],
            description=request.POST.get("description", ""),
            status="Pending"
        )
        messages.success(request, "Complaint submitted!")
        return redirect('demoapp:citizen_dashboard')
    return render(request, "demoapp/citizen/submit_complaint.html")

# ========================
# Utility Views
# ========================
def home(request):
    return render(request, "demoapp/pages/home.html")

def about(request):
    return render(request, "demoapp/pages/about.html")

def contact(request):
    return render(request, "demoapp/pages/contact.html")

def redirect_user_based_on_role(user):
    if user.role == "admin":
        return redirect("demoapp:admin_dashboard")
    elif user.role == "municipal":
        return redirect("demoapp:municipal_dashboard")
    elif user.role == "repair_team":
        return redirect("demoapp:repair_team_dashboard")
    else:
        return redirect("demoapp:citizen_dashboard")
    

@login_required
def update_report_status(request, report_id):
    if request.user.role != 'municipal':
        return redirect('demoapp:home')
    
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == "POST":
        new_status = request.POST.get("status")
        report.status = new_status
        report.save()
        
        StatusUpdate.objects.create(
            report=report,
            updated_by=request.user,
            from_status=report.status,
            to_status=new_status,
            notes=f"Status changed by {request.user.username}"
        )
        
        messages.success(request, "Report status updated!")
        return redirect('demoapp:report_detail', report_id=report.id)
    
    return render(request, "demoapp/municipal/update_status.html", {'report': report})