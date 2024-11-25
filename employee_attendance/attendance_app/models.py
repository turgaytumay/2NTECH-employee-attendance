from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta

class Employee(AbstractUser):
    annual_leave = models.FloatField(default=15)
    is_manager = models.BooleanField(default=False)

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    late_minutes = models.IntegerField(default=0)

class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    approved = models.BooleanField(null=True)

class Notification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
