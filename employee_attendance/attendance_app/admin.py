from django.contrib import admin
from .models import Employee, Attendance, LeaveRequest, Notification
from django.contrib.auth.admin import UserAdmin

admin.site.register(Employee, UserAdmin)
admin.site.register(Attendance)
admin.site.register(LeaveRequest)
admin.site.register(Notification)
