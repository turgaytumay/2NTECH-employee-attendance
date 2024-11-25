from django.urls import path
from . import views

urlpatterns = [
    path('login/employee/', views.login_employee, name='login_employee'),
    path('login/manager/', views.login_manager, name='login_manager'),
    path('logout/', views.logout_view, name='logout'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('employee/leaves/', views.employee_leaves, name='employee_leaves'),
    path('manager/assign_leave/', views.manager_assign_leave, name='manager_assign_leave'),
    path('request_leave/', views.request_leave, name='request_leave'),
    path('leave_requests/', views.leave_requests, name='leave_requests'),
    path('approve_leave/<int:request_id>/', views.approve_leave, name='approve_leave'),
    path('deny_leave/<int:request_id>/', views.deny_leave, name='deny_leave'),
    path('notifications/', views.notifications, name='notifications'),
    path('manager/monthly_report/', views.monthly_report, name='monthly_report'),
    path('', views.home_redirect, name='home_redirect'),
    
]
