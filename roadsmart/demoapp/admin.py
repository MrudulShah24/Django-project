from django.contrib import admin
from .models import CustomUser, RoadIssue , Report, Task, Complaint, StatusUpdate

admin.site.register(CustomUser)
admin.site.register(RoadIssue)
admin.site.register(Report)
admin.site.register(Task)
admin.site.register(Complaint)

@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_status', 'to_status', 'updated_by', 'created_at')
    list_filter = ('to_status', 'created_at')  # Only use actual field names here
    search_fields = ('report__title', 'complaint__issue')