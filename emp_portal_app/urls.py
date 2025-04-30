from django.urls import path
from .views import *

urlpatterns = [

    path('permissions/', permission_list, name='permission_list'),
    path('permissions/create/', permission_create, name='permission_create'),
    path('permissions/update/<int:pk>/', permission_update, name='permission_update'),
    path('permissions/delete/<int:pk>/', permission_delete, name='permission_delete'),

    path('departments/', department_list, name='department_list'),
    path('departments/create/', department_create, name='department_create'),
    path('departments/update/<int:pk>/', department_update, name='department_update'),
    path('departments/delete/<int:pk>/', department_delete, name='department_delete'),

    path('employees/', employee_list, name='employee_list'),
    path('employees/create/', employee_create, name='employee_create'),
    path('employees/update/<int:pk>/', employee_update, name='employee_update'),
    path('employees/disable/<int:pk>/', employee_disable, name='employee_disable'),

    path('login/', login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/',home,name='home'),
    path('refresh/',refresh_token_view,name='refresh'),

    path('projects/', project_list, name='project_list'),
    path('projects/create/', project_create, name='project_create'),
    path('projects/update/<int:pk>/', project_update, name='project_update'),
    path('projects/delete/<int:pk>/', project_delete, name='project_delete'),
    path('projects/<int:pk>/', project_individual_view, name='project_detail'),

    path('manager/employees', employees_under_manager, name='employees_under_manager'),

    path('project_assignations/', project_assignation_list, name='project_assignation_list'),
    path('project_assignations/create/', project_assignation_create, name='project_assignation_create'),
    path('project_assignations/update/<int:pk>/', project_assignation_update, name='project_assignation_update'),
    #path('project_assignations/delete/<int:pk>/', project_delete, name='project_delete'),
    #path('projects/<int:pk>/', project_individual_view, name='project_detail'),
    
    path('profile_picture', profile_picture, name='profile_picture'),
    path('profile_view', profile_view, name='profile_view'),
    path('getname',getname, name='getname'),

    path('timesheet/create/', submit_time_entry, name='submit_time_entry'),
    path('timesheet/update/<int:entry_id>/', update_time_entry, name='update_time_entry'),
    path('timesheet/timesheet_overview', timesheet_overview, name='timesheet_overview'),
    path('timesheet/timesheet_breakdown', timesheet_breakdown, name='timesheet_breakdown'),
    path('timesheet/get_projects', get_projects, name='get_projects'),

    path('leaves/apply/', apply_leave, name='apply_leave'),
    path('leave-applications/', leave_applications, name='leave_applications'),
    path('leaves/edit/<int:leave_id>/', edit_leave, name='edit_leave'),
    path('leaves/approve/<int:leave_id>/', approve_leave, name='approve_leave'),
    path('leaves/reject/<int:leave_id>/', reject_leave, name='reject_leave'),
    path('leaves/cancel/<int:leave_id>/', cancel_leave, name='cancel_leave'),

    path('employees/profile_update/', profile_update, name='profile_update'),
    path('password_update', password_update, name='password_update'),

    path('toggle_check_in_check_out/', toggle_check_in_check_out, name='toggle_check_in_check_out'),
    path('get_total_time_worked/', get_total_time_worked, name='get_total_time_worked'),

   
    path('shift_initializing_code/', shift_initializing_code, name='shift_initializing_code'),

    path('attendance/tabular_view', attendance_tabular_view,name='attendance_tabular_view'),
    path('attendance/audit_history', attendance_audit_history,name='attendance_audit_history'),


    path('reset-password/', password_reset_request, name='password_reset'),
    path('reset-password-sent/', password_reset_sent, name='password_reset_sent'),
    path('reset-password/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('reset-password-complete/', password_reset_complete, name='password_reset_complete'),

]