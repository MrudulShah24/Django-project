from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('municipal', 'Municipal Authority'),
        ('repair_team', 'Repair Team'),
        ('citizen', 'Citizen'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class RoadIssue(models.Model):
    STATUS_CHOICES = [
        ('Pendin    g', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]
    
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reported_issues")
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='road_issues/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reported_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.status})"


class Report(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='reports/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name="assigned_reports")

    def __str__(self):
        return f"{self.title} (Priority: {self.priority})"

class Task(models.Model):
    STATUS_CHOICES = [
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="task")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="repair_tasks")
    task_details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Assigned')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-update linked report status when task is completed
        if self.status == 'Completed' and not self.completed_at:
            self.completed_at = timezone.now()
            self.report.status = 'Completed'
            self.report.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Task {self.id} - {self.status}"

class Complaint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="user_complaints"  
    )

    
class StatusUpdate(models.Model):
    complaint = models.ForeignKey('Complaint', null=True, blank=True, on_delete=models.CASCADE)
    report = models.ForeignKey('Report', null=True, blank=True, on_delete=models.CASCADE)
    from_status = models.CharField(max_length=20)  # Changed from old_status
    to_status = models.CharField(max_length=20)    # Changed from new_status
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # Changed from changed_by
    created_at = models.DateTimeField(auto_now_add=True)  # Changed from timestamp
    
    def __str__(self):
        return f"{self.from_status} → {self.to_status}"