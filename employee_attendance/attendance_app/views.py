from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Employee, Attendance, LeaveRequest, Notification
from django.utils import timezone
from datetime import datetime, time, timedelta, date
from django.contrib import messages
from django.db.models import Sum

def home_redirect(request):
    return redirect('login_employee')
# Login
def login_employee(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and not user.is_manager:
            login(request, user)
            return redirect('employee_dashboard')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
    return render(request, 'login_employee.html')

def login_manager(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_manager:
            login(request, user)
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
    return render(request, 'login_manager.html')

def logout_view(request):
    logout(request)
    return redirect('login_employee')

# Personel Dashboard
def employee_dashboard(request):
    if not request.user.is_authenticated or request.user.is_manager:
        return redirect('login_employee')
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(employee=request.user, date=today)
    
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')
        if action == 'check_in':
            if attendance.check_in is None:
                attendance.check_in = timezone.now().time()
                company_start_time = time(8, 0)
                if attendance.check_in > company_start_time:
                    delta = datetime.combine(today, attendance.check_in) - datetime.combine(today, company_start_time)
                    attendance.late_minutes = int(delta.total_seconds() // 60)
                    request.user.annual_leave -= attendance.late_minutes / 480
                    request.user.save()
                    check_annual_leave(request.user)
                    managers = Employee.objects.filter(is_manager=True)
                    for manager in managers:
                        Notification.objects.create(
                            employee=manager,
                            message=f"{request.user.username} {attendance.late_minutes} dakika geç kaldı."
                        )
                attendance.save()
        elif action == 'check_out':
            if attendance.check_out is None:
                attendance.check_out = timezone.now().time()
                attendance.save()
    else:
        pass
    
    leave_requests = LeaveRequest.objects.filter(employee=request.user)
    context = {
        'attendance': attendance,
        'leave_requests': leave_requests,
    }
    return render(request, 'employee_dashboard.html', context)

def manager_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('login_manager')
    employees = Employee.objects.filter(is_manager=False)
    employee_data = []
    for employee in employees:
        total_late = Attendance.objects.filter(employee=employee).aggregate(total_late=Sum('late_minutes'))['total_late'] or 0
        employee_data.append({
            'employee': employee,
            'total_late': total_late,
        })
    context = {
        'employee_data': employee_data,
    }
    return render(request, 'manager_dashboard.html', context)

def employee_leaves(request):
    if not request.user.is_authenticated or request.user.is_manager:
        return redirect('login_employee')
    leave_requests = LeaveRequest.objects.filter(employee=request.user, approved=True)
    context = {
        'leave_requests': leave_requests,
    }
    return render(request, 'employee_leaves.html', context)

def manager_assign_leave(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('login_manager')
    if request.method == 'POST':
        employee_id = request.POST['employee']
        days = float(request.POST['days'])
        employee = Employee.objects.get(id=employee_id)
        employee.annual_leave += days
        employee.save()
        messages.success(request, f"{employee.username} kullanıcısına {days} gün izin eklendi.")
    employees = Employee.objects.filter(is_manager=False)
    context = {
        'employees': employees,
    }
    return render(request, 'manager_assign_leave.html', context)

def notifications(request):
    if not request.user.is_authenticated:
        return redirect('login_employee')
    notifications = Notification.objects.filter(employee=request.user, is_read=False)
    for notification in notifications:
        notification.is_read = True
        notification.save()
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications.html', context)

def monthly_report(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('login_manager')
    employees = Employee.objects.filter(is_manager=False)
    report = []
    for employee in employees:
        attendances = Attendance.objects.filter(employee=employee, date__month=timezone.now().month)
        total_hours = 0
        for attendance in attendances:
            if attendance.check_in and attendance.check_out:
                check_in_datetime = datetime.combine(attendance.date, attendance.check_in)
                check_out_datetime = datetime.combine(attendance.date, attendance.check_out)
                work_duration = (check_out_datetime - check_in_datetime).total_seconds() / 3600  # saat cinsinden
                total_hours += work_duration
        report.append({
            'employee': employee,
            'total_hours': total_hours,
        })
    context = {
        'report': report,
    }
    return render(request, 'monthly_report.html', context)

def check_annual_leave(employee):
    if employee.annual_leave < 3:
        managers = Employee.objects.filter(is_manager=True)
        for manager in managers:
            Notification.objects.create(
                employee=manager,
                message=f"{employee.username} kullanıcısının yıllık izni 3 günden azaldı."
            )

def request_leave(request):
    if not request.user.is_authenticated or request.user.is_manager:
        return redirect('login_employee')
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        delta = (end - start).days + 1
        if delta <= request.user.annual_leave:
            leave_request = LeaveRequest.objects.create(
                employee=request.user,
                start_date=start_date,
                end_date=end_date,
            )
            leave_request.save()
            messages.success(request, 'İzin talebiniz alındı.')
        else:
            messages.error(request, 'Yeterli izin gününüz yok.')
        return redirect('employee_dashboard')
    return render(request, 'request_leave.html')

def leave_requests(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('login_manager')
    requests = LeaveRequest.objects.filter(approved=None)
    context = {
        'requests': requests,
    }
    return render(request, 'leave_requests.html', context)

def approve_leave(request, request_id):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('login_manager')
    leave_request = LeaveRequest.objects.get(id=request_id)
    start = leave_request.start_date
    end = leave_request.end_date
    delta = (end - start).days + 1
    employee = leave_request.employee
    if employee.annual_leave >= delta:
        leave_request.approved = True
        leave_request.save()
        employee.annual_leave -= delta
        employee.save()
        check_annual_leave(employee)
        messages.success(request, 'İzin talebi onaylandı.')
    else:
        messages.error(request, 'Personelin yeterli izin günü yok.')
    return redirect('leave_requests')

def deny_leave(request, request_id):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('login_manager')
    leave_request = LeaveRequest.objects.get(id=request_id)
    leave_request.approved = False
    leave_request.save()
    messages.info(request, 'İzin talebi reddedildi.')
    return redirect('leave_requests')
