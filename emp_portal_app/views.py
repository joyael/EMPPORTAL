from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.utils import timezone

from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import jwt

from django.db.models import Q

from EMPPORTAL import settings
from emp_portal_app.auth import get_current_user, role_required
from emp_portal_app.models import SHIFT_HOURS_IN_A_DAY, CheckInOut, Shift, default_working_days
from .helper_functions import calculate_attendance, check_leave_balance, check_leave_conflicts, generate_attendance_list, get_dates, get_remaining_leave_data, get_the_break_down_total_data, get_the_overview_total_data, is_user_checked_in, log_timings, majority_month, timesheeet_overview_data_extract
from .operations_by_role import operations

from .forms import *
from .utils import create_access_token, check_refresh_token, create_refresh_token, insert_refresh_token, is_refresh_token_active, make_refresh_token_inactive, token_generator

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login as session_login

from django.contrib.auth.hashers import make_password

from django.contrib.sessions.models import Session
import json

from allauth.socialaccount.models import SocialAccount

from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils.timezone import localtime, make_aware

from emp_portal_app.models import CASUAL_LEAVE_QUARTERLY_COUNT, RH_YEARLY_COUNT, SHIFT_HOURS_IN_A_DAY, SICK_LEAVE_QUARTERLY_COUNT



# Create your views here.

def refresh_token_view(request):
    refresh_token = request.COOKIES.get('refresh_token')  # Get the refresh token from the cookie
    if not refresh_token:
        return JsonResponse({'error': 'Refresh token not found'}, status=401)
    if check_refresh_token(refresh_token):
        if not is_refresh_token_active(refresh_token):
            return JsonResponse({'error': 'Refresh token Inactivated'}, status=401)
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = Employee.objects.get(employee_id=user_id)

        # Generate a new access token
        new_access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)
        insert_refresh_token(new_refresh_token)

        # Set the new access token as a cookie
        response = JsonResponse({'message': 'Access token refreshed successfully'})
        response.set_cookie('access_token', new_access_token, httponly=True, secure=True)  # Set the access token cookie
        response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True) # Setting new refresh token for rotation

        make_refresh_token_inactive(refresh_token)

        return response
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Refresh token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid refresh token'}, status=401)



class LogoutView(View):
    def post(self, request):
        # Get the refresh token from cookies
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            make_refresh_token_inactive(refresh_token)  # Invalidate the refresh token

        # Clear the cookies
        response = JsonResponse({'message': 'Logged out successfully.'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        logout(request)

        return response


def permission_list(request):
    permissions = Permission.objects.all()
    return render(request, 'permission_list.html', {'permissions': permissions})


def permission_create(request):
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('permission_list')
    else:
        form = PermissionForm()
    return render(request, 'permission_create.html', {'form': form, 'action': 'Create'})


def permission_update(request, pk):
    permission = get_object_or_404(Permission, pk=pk)
    if request.method == 'POST':
        form = PermissionForm(request.POST, instance=permission)
        if form.is_valid():
            form.save()
            return redirect('permission_list')  
    else:
        form = PermissionForm(instance=permission)
    return render(request, 'permission_create.html', {'form': form, 'action': 'Update'})


def permission_delete(request, pk):
    permission = get_object_or_404(Permission, pk=pk)
    if request.method == 'POST':
        permission.delete()
        return redirect('permission_list')  
    return render(request, 'permission_confirm_delete.html', {'permission': permission})




def department_list(request):
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    departments = Department.objects.all()
    return render(request, 'department_list.html', {
        'departments': departments, 'operations': operations1, 'level':int(level),'active_title':'Departments',
        'page_paths':['Departments','Department List']
        })


def department_create(request):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department Created")
            if 'add_new' in request.POST:
                return redirect('department_create')
            else:
                return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'department_form.html', {'form': form, 'action': 'Create', 'operations': operations1, 'level':int(level),'active_title':'Departments'})


def department_update(request, pk):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'department_form.html', {'form': form, 'action': 'Update', 'operations': operations1, 'level':int(level),'active_title':'Departments'})


def department_delete(request, pk):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'department_confirm_delete.html', {'department': department, 'operations': operations1, 'level':int(level),'active_title':'Departments'})



def employee_list(request):
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees, 'operations': operations1, 'level':int(level),'active_title':'Employees','page_paths': ['Employees','Employee List'],})


def employee_create(request):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Employee Created successfully")
            return redirect('employee_list') 
    else:
        form = EmployeeForm()
    return render(request, 'employee_form.html', {'form': form, 'action': 'Create', 'operations': operations1, 'level':int(level),'active_title':'Employees','page_paths': ['Employees','Employee Create'],})


def employee_update(request, pk):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list') 
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_form.html', {'form': form, 'action': 'Update', 'operations': operations1, 'level':int(level),'active_title':'Employees','page_paths': ['Employees','Employee Update'],})


def employee_disable(request, pk):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeStatusForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()  # Only the status will be updated
            messages.success(request, 'Employee status updated successfully.')
            return redirect('employee_list')  #Redirect to the employee list or another page
    else:
        form = EmployeeStatusForm(instance=employee)
    return render(request, 'employee_disable_form.html', {'employee': employee,'form':form, 'operations': operations1, 'level':int(level),'active_title':'Employees',
        'page_paths': ['Employees','Employee Disable'],})



def login(request):
    flag=0
    if request.user:
        try:
            email = request.user.email
            user = Employee.objects.filter(email=email).first()
            if user:
                flag=1
        except Exception:
            pass

    if request.method == 'POST':
        email = request.POST.get('email')  #Get the email from the POST data
        password = request.POST.get('password_hash')  #Get the password from the POST data

        
        # Check if the user exists
        user = Employee.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Email does not exist")
            return redirect('login')
        
        # Check the password
        encoded_password = user.password_hash
        if not check_password(password, encoded_password):  # Check password
            messages.error(request, "Incorrect password")
            return redirect('login')
        flag=1

    if flag==1:    
        # Assuming create_access_token and create_refresh_token are defined elsewhere
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        insert_refresh_token(refresh_token)

        messages.success(request, "Login Successful!")
        
        response = redirect('home')
        response.set_cookie('access_token', access_token, httponly=True, secure=True)
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
        return response
    else:
        return render(request, 'login.html')  # Render the login form for GET requests


def home(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    dates = get_dates()

    def get_time_period_data(from_date, to_date):
        time_entries = Timesheet.objects.filter(date__range=[from_date, to_date])
        overview_data = timesheeet_overview_data_extract(user, from_date, to_date, [user], time_entries)
        
        if not overview_data["the_timesheet_overview_data"]:
            return {
                "logged_hours": 0,
                "total_hours": 0,
                "project_hours": 0,
                "bench_hours": 0,
                "training_hours": 0,
                "learning_hours": 0,
                "leave_days": 0,
                "deviation": 0,
                "has_deviation": False,
            }
        
        data = overview_data["the_timesheet_overview_data"][0]
        return {
            "logged_hours": data.get("total_hours", 0),
            "total_hours": overview_data.get("minimum_working_hours", 0),
            "project_hours": data.get("project_hours", 0),
            "bench_hours": data.get("bench_hours", 0),
            "training_hours": data.get("training_hours", 0),
            "learning_hours": data.get("learning_hours", 0),
            "leave_days": data.get("leave_days", 0),
            "deviation": data.get("deviation", 0),
            "has_deviation": data.get("has_deviation", False),
        }

    # Current week
    current_week_data = get_time_period_data(dates["current_week"]["first_date"], dates["current_week"]["current_date"])
    
    # Last week
    last_week_data = get_time_period_data(dates["last_week"]["first_date"], dates["last_week"]["last_date"])
    
    # Current month
    current_month_data = get_time_period_data(dates["current_month"]["first_date"], dates["current_month"]["current_date"])
    
    # Last month
    last_month_data = get_time_period_data(dates["last_month"]["first_date"], dates["last_month"]["last_date"])

    print(current_week_data)
    return render(request, 'home.html', {
        'current_week_data': current_week_data,
        'last_week_data': last_week_data,
        'current_month_data': current_month_data,
        'last_month_data': last_month_data,
        'operations': operations1, 
        'level': int(level),
        'active_title': 'Home',
        'page_paths': ['Home',],
    })

def getname(request):
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    name = user.name() + " (" + user.get_role_display() + ")"
    return JsonResponse({'name': name})

def project_list(request):
    validate_user = role_required(request=request,permission_name="manager")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    projects = Project.objects.all().order_by('created_at')
    return render(request, 'projects/project_list.html', {'projects': projects, 'operations': operations1, 'level':int(level),'active_title':'Projects','page_paths': ['Projects','Project List'],})

def project_create(request):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Create', 'operations': operations1, 'level':int(level),'active_title':'Projects','page_paths': ['Projects','Project Create'],})

def project_update(request, pk):
    validate_user = role_required(request=request, permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    project = get_object_or_404(Project, project_id=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Update', 'operations': operations1, 'level': int(level),'active_title':'Projects','page_paths': ['Projects','Project Update'],})

def project_delete(request, pk):
    validate_user = role_required(request=request,permission_name ="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project, 'operations': operations1, 'level':int(level),'active_title':'Projects','page_paths': ['Projects','Project Delete'],})

def project_individual_view(request, pk):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_individual_view.html', {
        'project': project, 
        'operations': operations1, 
        'level':int(level),
        'active_title':'Projects',
        'page_paths':['Projects','Project Individual View'],

        })


def employees_under_manager(request):
    validate_user = role_required(request=request,permission_name="manager")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    manager = user
    employees = Employee.objects.filter(reporting_manager=manager)
    return render(request, 'employees_under_manager.html', {
        'manager': manager,
        'employees': employees, 'operations': operations1, 
        'level':int(level),'active_title':'Employees',
        'page_paths':['Employees','Employees under manager'],
    })


def project_assignation_create(request):
    validate_user = role_required(request=request,permission_name="manager")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]
    manager = user
    if request.method == 'POST':
        form = ProjectAssignationForm(request.POST, logged_in_user=user)
        if form.is_valid():
            assignation = form.save(commit=False)
            if(level>1):
                assignation.assigning_manager = manager
            assignation.save()
            messages.success("Project assignation created")
            if 'add_new' in request.POST:
                return redirect('project_assignation_create')
            return redirect('project_assignation_list')
        else:
            print(form.errors)
            messages.error(request, "submitted form is invalid")
    else:
        form = ProjectAssignationForm(logged_in_user=manager)
    return render(request, 'assignations/project_assignation_form.html', {
        'form': form,
        'action':'Create',
        'operations': operations1,
        'level':level,
        'active_title':'Project Assignations',
        'page_paths':['Project Assignations','Create Project Assignation'],
    })


def project_assignation_update(request, pk):
    validate_user = role_required(request=request,permission_name="manager")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    manager = user
    assignation = get_object_or_404(ProjectAssignation, assign_id=pk)
    if request.method == 'POST':
        form = ProjectAssignationForm(request.POST, instance = assignation, logged_in_user = manager)
        if form.is_valid():
            assignation = form.save(commit=False)
            if(int(level)>1):
                assignation.assigning_manager = manager
            assignation.save()
            messages.success("Project assignation updated")
            if 'add_new' in request.POST:
                return redirect('project_assignation_create')
            return redirect('project_assignation_list')
    else:
        form = ProjectAssignationForm(instance=assignation, logged_in_user=manager)
    return render(request, 'assignations/project_assignation_form.html', {
            'form': form, 
            'action': 'Update',
            'operations': operations1, 
            'level':int(level),
            'page_paths':['Project Assignation','Project Assignation Update'],
            'active_title':'Project Assignations'
        })


def project_assignation_list(request):
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]
    if(int(level)==2):
        assignations = ProjectAssignation.objects.filter(assigning_manager=user)
    elif(level==3):
        assignations = ProjectAssignation.objects.filter(employee=user)
    else:
        assignations = ProjectAssignation.objects.all()

    projects = set()
    employees = set()
    assigning_managers = set()
    roles = set()
    statuses = set()

    for assignation in assignations:
        projects.add(assignation.project)
        employees.add(assignation.employee)
        assigning_managers.add(assignation.assigning_manager)
        roles.add(assignation.role)
        status = (assignation.status, assignation.get_status_display())  # Use a tuple for uniqueness
        statuses.add(status)

    # Convert sets back to lists if needed
    projects = list(projects)
    employees = list(employees)
    assigning_managers = list(assigning_managers)
    roles = list(roles)
    statuses = [{'num': num, 'name': name} for num, name in statuses]  # Convert back to list of dicts


    if request.method == "POST":
        role = request.POST.get('role_for_form')
        status = request.POST.get('status')
        assigning_manager_id = request.POST.get('assigning_manager_id')
        employee_id = request.POST.get('employee_id')
        project_id = request.POST.get('project_id')
        date_input = request.POST.get('dateInput')
        if(role!='nil'):
            print("Role is not nil , it is : ",role)
            assignations=assignations.filter(role=role)
        if(status!='nil'):
            print("status is not nil")
            assignations=assignations.filter(status=status)
        if(assigning_manager_id!='nil'):
            print("assigning_manager_id is not nil")
            assigning_manager = Employee.objects.get(employee_id=assigning_manager_id)
            assignations = assignations.filter(assigning_manager=assigning_manager)
        if(employee_id!='nil'):
            print("employee_id is not nil")
            employee = Employee.objects.get(employee_id=employee_id)
            assignations = assignations.filter(employee=employee)
        if(project_id!='nil'):
            print("project_id is not nil")
            project = Project.objects.get(project_id=project_id)
            assignations = assignations.filter(project=project)
        if date_input:
            print("DateInput is : "+date_input)
            received_date = datetime.strptime(date_input, '%Y-%m-%d').date()
            assignations = assignations.filter(start_date__lte=received_date, end_date__gte=received_date)

        html_content =  render(request, 'assignations/project_assignations_filtered_part.html', {
            'assignations': assignations,
            'level':int(level),
            'projects':projects,
            'employees':employees,
            'roles':roles,
            'statuses':statuses,
            'assigning_managers':assigning_managers,
        })
        return JsonResponse({'html': html_content.content.decode('utf-8')})



    return render(request, 'assignations/project_assignation_list.html', {
        'assignations': assignations,
        'operations': operations1, 
        'level':int(level),
        'projects':projects,
        'employees':employees,
        'roles':roles,
        'statuses':statuses,
        'assigning_managers':assigning_managers,
        'page_paths':['Project Assignations','Project Assignation List'],
        'active_title':'Project Assignations'
    })


def profile_picture(request):
    if request.user.is_authenticated:
        user = request.user
        profile_picture = ""
        try:
            social_account = SocialAccount.objects.get(user=user, provider='google')
            profile_picture_url = social_account.extra_data.get('picture')
            profile_picture = profile_picture_url
        except SocialAccount.DoesNotExist:
            profile_picture = ""
        return JsonResponse({'profile_picture': profile_picture})
    return JsonResponse({'profile_picture': ''})
        

def profile_view(request):
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    sessions = Session.objects.filter(expire_date__gte=datetime.now())  # Active sessions
    print(len(sessions))
    user_sessions = []
    for session in sessions:
        data = session.get_decoded()
        if str(request.user.id) == str(data.get('_auth_user_id')):  # Match logged-in user
            user_sessions.append({
                'session_key': session.session_key,
                'ip': data.get('ip', 'Unknown IP'),  #If IP is stored
                'browser': data.get('browser', 'Unknown Browser'),
                'device': data.get('device', 'Unknown Device'),
                'last_activity': session.expire_date
            })
    
    return render(request, 'profile_view.html', {
        'user':user,
        'operations': operations1, 
        'level':int(level),
        'page_paths':['Profile'],
        'active_title':'Profile',
        'user_sessions': user_sessions,
    })


def submit_time_entry(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    if request.method == 'POST':
        form = TimesheetForm(request.POST, logged_in_user=user)
        if form.is_valid():
            timesheet = form.save(commit=False)
            timesheet.employee = user
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            print("The employee is : ",user.name())
            selected_project = form.cleaned_data.get('project')

            if selected_project not in ['bench', 'training', 'learning']:
                project_instance = get_object_or_404(Project, project_name=selected_project)
                timesheet.project_real = project_instance
            
            timesheet.save()
            print("The time_entry saved ")
            print("the timesheet date is ", timesheet.date)
            print("The time_entry saved ")
            print("the timesheet date is ", timesheet.date)
            print("The time_entry saved ")
            print("the timesheet date is ", timesheet.date)
            print("The time_entry saved ")
            print("the timesheet date is ", timesheet.date)
            print("The time_entry saved ")
            print("the timesheet date is ", timesheet.date)
            print("The time_entry saved ")
            print("the timesheet date is ", timesheet.date)
            print("The time_entry saved ")
            print("the timesheet date is ", timesheet.date)

            messages.success(request,"Time Entry Added ")

            if 'add_new' in request.POST:
                return redirect('submit_time_entry')
            return redirect('timesheet_breakdown')
    else:
        form = TimesheetForm(logged_in_user=user)

    return render(request, 'timesheet/submit_time_entry.html', {
        'form': form,
        'action': 'Create',
        'operations': operations1,
        'level': level,
        'active_title': 'Timesheet',
        'page_paths': ['Timesheet', 'Submit Time Entry'],
    })


def update_time_entry(request, entry_id):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    # Retrieve the existing timesheet entry to be updated
    timesheet_entry = get_object_or_404(Timesheet, id = entry_id)

    if request.method == 'POST':
        form = TimesheetForm(request.POST, instance=timesheet_entry, logged_in_user=user)
        if form.is_valid():
            timesheet = form.save(commit=False)
            selected_project = form.cleaned_data.get('project')

            if selected_project not in ['bench', 'training', 'learning']:
                project_instance = get_object_or_404(Project, project_name=selected_project)
                timesheet.project_real = project_instance
            
            timesheet.save()
            messages.success(request, "Time entry updated successfully.")
            return redirect('timesheet_breakdown')
    else:
        form = TimesheetForm(instance=timesheet_entry, logged_in_user=user)
        date_of_time_entry = timesheet_entry.date.strftime('%Y-%m-%d')
        project_of_time_entry = timesheet_entry.project

    return render(request, 'timesheet/submit_time_entry.html', {
        'form': form,
        "date_of_time_entry": date_of_time_entry,
        'project_of_time_entry': project_of_time_entry,
        'action': 'Update',
        'operations': operations1,
        'level': level,
        'active_title': 'Timesheet',
        'page_paths': ['Timesheet', 'Update Time Entry'],
    })


def timesheet_overview(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    today = datetime.today().date()
    to_date_input = today
    from_date_input = today - timedelta(days=15)
    time_entries = Timesheet.objects.filter(date__range=[from_date_input, to_date_input])


    projects = set()
    employees = set()
    print("Length of employees at first : ",len(employees))


    constant_project_things = [
        {'project_name':'Bench','project_id':'bench'},
        {'project_name':'Training','project_id':'training'},
        {'project_name':'Learning','project_id':'learning'},
    ]
    
    if level <= 1:
        all_projects = Project.objects.all()
        for p in all_projects:
            projects.add(p)
        all_employees =  Employee.objects.all()
        for e in all_employees:
            employees.add(e)

    elif level == 2:
        #user is manager
        manager = user
        employees.add(manager)
        employees_under_manager = Employee.objects.filter(reporting_manager=manager)
        for emp in employees_under_manager:
            employees.add(emp)
        for employee in employees:
            pas = ProjectAssignation.objects.filter(employee=employee)
            for pa in pas:
                projects.add(pa.project)
        project_assignations = ProjectAssignation.objects.filter(assigning_manager=manager)
        for pa in project_assignations:
            employees.add(pa.employee)
        for employee in employees:
            pas = ProjectAssignation.objects.filter(employee=employee)
            for pa in pas:
                projects.add(pa.project)
        time_entries = time_entries.filter(employee__in=employees)
                
    elif level == 3:
        employee = user
        employees.add(employee)
        pas = ProjectAssignation.objects.filter(employee=employee)
        for pa in pas:
            projects.add(pa.project)
        time_entries = time_entries.filter(employee=employee)
        
    projects = list(projects)
    employees = list(employees)

    projects.extend(constant_project_things)

    the_timesheet_overview_data = []
    overview_total_data = dict()
    minimum_working_hours = 0

    output = timesheeet_overview_data_extract(user,from_date_input,to_date_input,employees,time_entries)

    the_timesheet_overview_data = output["the_timesheet_overview_data"]
    print("Actual length of timesheet overview data : ",len(the_timesheet_overview_data))
    item_list = the_timesheet_overview_data  # Get all data
    page_number = request.GET.get('page', 1)  # Get the page number
    items_per_page = 50  # Number of items per page
    paginator = Paginator(item_list, items_per_page)

    try:
        page_number = int(page_number)  # Ensure it's an integer
        items = paginator.page(page_number)  # Get the requested page
    except PageNotAnInteger:
        items = paginator.page(1)  # Default to first page if not an integer
    except EmptyPage:
        items = paginator.page(paginator.num_pages)  # Get last page if out of range
    
    print("Length after pagination : ",len(items))

    # Convert to list if needed
    paginated_items = list(items)

    paginated_timesheet_overview_data = paginated_items
    overview_total_data = get_the_overview_total_data(paginated_timesheet_overview_data)
    minimum_working_hours = output["minimum_working_hours"]
    fromdateInputValue = from_date_input.strftime('%Y-%m-%d')
    todateInputValue = to_date_input.strftime('%Y-%m-%d')



    if request.method != "POST":
        return render(request, 'timesheet/timesheet_overview.html', {
            'the_timesheet_overview_data':items,
            'items':items,
            'overview_total_data':overview_total_data,
            'minimum_working_hours':minimum_working_hours,
            'projects':projects,
            'employees':employees,
            'fromdateInputValue' : fromdateInputValue,
            'todateInputValue' : todateInputValue,
            'operations': operations1,
            'level': level,
            'active_title': 'Timesheet',
            'page_paths': ['Timesheet', 'Timesheet Overview'],
        })

    if request.method == "POST":
        employee_id = request.POST.get('employee_id')
        project_id = request.POST.get('project_id')
        from_date_input = request.POST.get('fromdateInput')
        to_date_input = request.POST.get('todateInput')
        
        today = datetime.today().date()
        
        # Set default values if any date input is missing
        if not from_date_input or not to_date_input:
            to_date_input = today
            from_date_input = today - timedelta(days=15)
        else:
            # Convert the input strings to date objects
            to_date_input = datetime.strptime(to_date_input, "%Y-%m-%d").date()
            from_date_input = datetime.strptime(from_date_input, "%Y-%m-%d").date()
        
        # Ensure that from_date is not later than to_date
        if from_date_input > to_date_input:
            from_date_input = to_date_input - timedelta(days=15)
        
        # Start with all timesheet records
        time_entries = Timesheet.objects.all()
        
        if employee_id != 'nil':
            print("employee_id is not nil")
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                employees = [employee,]
                time_entries = time_entries.filter(employee=employee)
            except Employee.DoesNotExist:
                time_entries = time_entries.none()  # or handle error as needed
                
        if project_id != 'nil':
            print("project_id is not nil")
            try:
                if project_id in ('bench', 'training', 'learning'):
                    project =  project_id
                else:
                    project = Project.objects.get(project_id=project_id)
                time_entries = time_entries.filter(project=project)
            except Project.DoesNotExist:
                time_entries = time_entries.none()  # or handle error as needed

        # Filter by date range
        time_entries = time_entries.filter(date__range=[from_date_input, to_date_input])

        output = timesheeet_overview_data_extract(user,from_date_input,to_date_input,employees,time_entries)
        the_timesheet_overview_data = output["the_timesheet_overview_data"]
        item_list = the_timesheet_overview_data  # Get all data
        page_number = request.GET.get('page', 1)  # Get the page number
        items_per_page = 50  # Number of items per page
        paginator = Paginator(item_list, items_per_page)

        try:
            page_number = int(page_number)  #Ensure it's an integer
            items = paginator.page(page_number)  #Get the requested page
        except PageNotAnInteger:
            items = paginator.page(1)  #Default to first page if not an integer
        except EmptyPage:
            items = paginator.page(paginator.num_pages)  #Get last page if out of range

        # Convert to list if needed
        paginated_items = list(items)

        paginated_timesheet_overview_data = paginated_items

        overview_total_data = get_the_overview_total_data(paginated_timesheet_overview_data)
        minimum_working_hours = output["minimum_working_hours"]
        fromdateInputValue = from_date_input.strftime('%Y-%m-%d')
        todateInputValue = to_date_input.strftime('%Y-%m-%d')


        html_content =  render(request, 'timesheet/time_sheet_overview_filtered_part.html', {
            'the_timesheet_overview_data' : items,
            'level':int(level),
        })
        html_content_p =  render(request, 'timesheet/pagination_part_after_filter.html', {
            'items' : items,
            'level':int(level),
        })
        print(overview_total_data)
        return JsonResponse({
            'fromdateInputValue' : from_date_input,
            'todateInputValue' : to_date_input,
            'html': html_content.content.decode('utf-8'),
            'html_p': html_content_p.content.decode('utf-8'),
            'minimum_working_hours':minimum_working_hours,
            'timesheet_overview_data':paginated_items,
            'overview_total_data':overview_total_data,
        })


def timesheet_breakdown(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    today = datetime.today().date()
    to_date_input = today
    from_date_input = today - timedelta(days=15)
    

    time_entries = Timesheet.objects.filter(date__range=[from_date_input, to_date_input])
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)
    print("From date : ", from_date_input, "  To date : ",to_date_input)

    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    print("Length of time_entries_first :", time_entries.count())
    for time_entry in time_entries:
        print("the time entry is : ", time_entry.description , " and employee is : ", time_entry.employee.name() )
        print("the time entry is : ", time_entry.description , " and employee is : ", time_entry.employee.name() )
        print("the time entry is : ", time_entry.description , " and employee is : ", time_entry.employee.name() )
        print("the time entry is : ", time_entry.description , " and employee is : ", time_entry.employee.name() )
        print("the time entry is : ", time_entry.description , " and employee is : ", time_entry.employee.name() )
        print("the time entry is : ", time_entry.description , " and employee is : ", time_entry.employee.name() )
        print("the time entry is : ", time_entry.description , " and employee is : ", time_entry.employee.name() )


    projects = set()
    employees = set()
    print("Length of employees at first : ",len(employees))


    constant_project_things = [
        {'project_name':'Bench','project_id':'bench'},
        {'project_name':'Training','project_id':'training'},
        {'project_name':'Learning','project_id':'learning'},
    ]
    
    if level <= 1:
        all_projects = Project.objects.all()
        for p in all_projects:
            projects.add(p)
        all_employees =  Employee.objects.all()
        for e in all_employees:
            employees.add(e)

    elif level == 2:
        #user is manager
        manager = user
        employees.add(manager)
        employees_under_manager = Employee.objects.filter(reporting_manager=manager)
        for emp in employees_under_manager:
            employees.add(emp)
        for employee in employees:
            pas = ProjectAssignation.objects.filter(employee=employee)
            for pa in pas:
                projects.add(pa.project)
        project_assignations = ProjectAssignation.objects.filter(assigning_manager=manager)
        for pa in project_assignations:
            employees.add(pa.employee)
        for employee in employees:
            pas = ProjectAssignation.objects.filter(employee=employee)
            for pa in pas:
                projects.add(pa.project)
        time_entries = time_entries.filter(employee__in=employees)
                
    elif level == 3:
        employee = user
        employees.add(employee)
        pas = ProjectAssignation.objects.filter(employee=employee)
        for pa in pas:
            projects.add(pa.project)
        time_entries = time_entries.filter(employee=employee)
    

    
    print("Length of time_entries at last :", time_entries.count())
    print("Length of time_entries at last :", time_entries.count())
    print("Length of time_entries at last :", time_entries.count())
    print("Length of time_entries at last :", time_entries.count())
    print("Length of time_entries at last :", time_entries.count())
    print("Length of time_entries at last :", time_entries.count())
    print("Length of time_entries at last :", time_entries.count())
    print("Length of time_entries at last :", time_entries.count())

    for time_entry in time_entries:
        print("the time entry is : ", time_entry.description)
        print("the time entry is : ", time_entry.description)
        print("the time entry is : ", time_entry.description)
        print("the time entry is : ", time_entry.description)
        print("the time entry is : ", time_entry.description)
        print("the time entry is : ", time_entry.description)
        
    projects = list(projects)
    employees = list(employees)

    projects.extend(constant_project_things)

    # the_timesheet_overview_data = []
    breakdown_total_data = dict()
    minimum_working_hours = 0

    # output = timesheeet_overview_data_extract(user,from_date_input,to_date_input,employees,time_entries)

    # the_timesheet_overview_data = output["the_timesheet_overview_data"]
    # print("Actual length of timesheet overview data : ",len(the_timesheet_overview_data))
    item_list = time_entries  # Get all data
    page_number = request.GET.get('page', 1)  # Get the page number
    items_per_page = 50  # Number of items per page
    paginator = Paginator(item_list, items_per_page)

    try:
        page_number = int(page_number)  # Ensure it's an integer
        items = paginator.page(page_number)  # Get the requested page
    except PageNotAnInteger:
        items = paginator.page(1)  # Default to first page if not an integer
    except EmptyPage:
        items = paginator.page(paginator.num_pages)  # Get last page if out of range
    
    print("Length after pagination : ",len(items))

    # Convert to list if needed
    paginated_items = list(items)

    paginated_time_entries = paginated_items
    breakdown_total_data = get_the_break_down_total_data(paginated_time_entries,user, from_date_input, to_date_input)
    total_timesheet_time = breakdown_total_data["total_timesheet_time"]
    total_time_available_you = breakdown_total_data["total_time_available_you"]
    total_time_logged_you = breakdown_total_data["total_time_logged_you"]
    deviation_you = breakdown_total_data["deviation_you"]
    has_deviation_you = True if deviation_you < 0 else False
    deviation_you = format(deviation_you, ".2f")



    fromdateInputValue = from_date_input.strftime('%Y-%m-%d')
    todateInputValue = to_date_input.strftime('%Y-%m-%d')


    if request.method != "POST":
        return render(request, 'timesheet/timesheet_breakdown.html', {
            'paginated_time_entries':paginated_time_entries,
            'the_timesheet_overview_data':items,
            'items':items,
            'projects':projects,
            'employees':employees,
            'fromdateInputValue' : fromdateInputValue,
            'todateInputValue' : todateInputValue,
            'total_timesheet_time':total_timesheet_time,
            'total_time_available_you':total_time_available_you,
            'total_time_logged_you':total_time_logged_you,
            'deviation_you':deviation_you,
            'has_deviation_you':has_deviation_you,
            'operations': operations1,
            'level': level,
            'active_title': 'Timesheet',
            'page_paths': ['Timesheet', 'Timesheet Overview'],
        })
    
    if request.method == "POST":
        employee_id = request.POST.get('employee_id')
        project_id = request.POST.get('project_id')
        from_date_input = request.POST.get('fromdateInput')
        to_date_input = request.POST.get('todateInput')
        
        today = datetime.today().date()
        
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)
        print("From date : ", from_date_input, "  To date : ",to_date_input)

        # Set default values if any date input is missing
        if not from_date_input or not to_date_input:
            to_date_input = today
            from_date_input = today - timedelta(days=15)
        else:
            # Convert the input strings to date objects
            to_date_input = datetime.strptime(to_date_input, "%Y-%m-%d").date()
            from_date_input = datetime.strptime(from_date_input, "%Y-%m-%d").date()
        
        # Ensure that from_date is not later than to_date
        if from_date_input > to_date_input:
            from_date_input = to_date_input - timedelta(days=15)
        
        # Start with all timesheet records
        time_entries = Timesheet.objects.all()

        if level <= 1:
            pass

        elif level == 2:
            #user is manager
            manager = user
            employees.add(manager)
            employees_under_manager = Employee.objects.filter(reporting_manager=manager)
            for emp in employees_under_manager:
                employees.add(emp)
            for employee in employees:
                pas = ProjectAssignation.objects.filter(employee=employee)
                for pa in pas:
                    projects.add(pa.project)
            project_assignations = ProjectAssignation.objects.filter(assigning_manager=manager)
            for pa in project_assignations:
                employees.add(pa.employee)
            for employee in employees:
                pas = ProjectAssignation.objects.filter(employee=employee)
                for pa in pas:
                    projects.add(pa.project)
            time_entries = time_entries.filter(employee__in=employees)
                    
        elif level == 3:
            employee = user
            employees.add(employee)
            pas = ProjectAssignation.objects.filter(employee=employee)
            for pa in pas:
                projects.add(pa.project)
            time_entries = time_entries.filter(employee=employee)
        
        if employee_id != 'nil':
            print("employee_id is not nil")
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                employees = [employee,]
                time_entries = time_entries.filter(employee=employee)
            except Employee.DoesNotExist:
                time_entries = time_entries.none()  # or handle error as needed
                
        if project_id != 'nil':
            print("project_id is not nil")
            try:
                if project_id in ('bench', 'training', 'learning'):
                    project =  project_id
                else:
                    project = Project.objects.get(project_id=project_id)
                time_entries = time_entries.filter(project=project)
            except Project.DoesNotExist:
                time_entries = time_entries.none()  # or handle error as needed

        # Filter by date range
        time_entries = time_entries.filter(date__range=[from_date_input, to_date_input])

        item_list = time_entries  # Get all data
        page_number = request.GET.get('page', 1)  # Get the page number
        items_per_page = 50  # Number of items per page
        paginator = Paginator(item_list, items_per_page)

        try:
            page_number = int(page_number)  # Ensure it's an integer
            items = paginator.page(page_number)  # Get the requested page
        except PageNotAnInteger:
            items = paginator.page(1)  # Default to first page if not an integer
        except EmptyPage:
            items = paginator.page(paginator.num_pages)  # Get last page if out of range
        
        print("Length after pagination : ",len(items))

        # Convert to list if needed
        paginated_items = list(items)

        paginated_timesheet_overview_data = paginated_items

        paginated_time_entries = paginated_items
        breakdown_total_data = get_the_break_down_total_data(paginated_time_entries,user, from_date_input, to_date_input)
        total_timesheet_time = breakdown_total_data["total_timesheet_time"]
        total_time_available_you = breakdown_total_data["total_time_available_you"]
        total_time_logged_you = breakdown_total_data["total_time_logged_you"]
        deviation_you = breakdown_total_data["deviation_you"]
        has_deviation_you = True if deviation_you < 0 else False
        deviation_you = format(deviation_you, ".2f")



        fromdateInputValue = from_date_input.strftime('%Y-%m-%d')
        todateInputValue = to_date_input.strftime('%Y-%m-%d')


        html_content =  render(request, 'timesheet/time_sheet_breakdown_filtered_part.html', {
            'paginated_time_entries' : paginated_time_entries,
            'level':int(level),
        })
        html_content_p =  render(request, 'timesheet/pagination_part_after_filter.html', {
            'items' : items,
            'level':int(level),
        })
        print(paginated_time_entries)
        return JsonResponse({
            'fromdateInputValue' : from_date_input,
            'todateInputValue' : to_date_input,
            'html': html_content.content.decode('utf-8'),
            'html_p': html_content_p.content.decode('utf-8'),
            'total_timesheet_time':total_timesheet_time,
            'total_time_available_you':total_time_available_you,
            'total_time_logged_you':total_time_logged_you,
            'deviation_you':deviation_you,
            'has_deviation_you':has_deviation_you,
        })
    

def apply_leave(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]
    
    employee_name = user.name()
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            employee=user
            date = form.cleaned_data['date']
            leave_type = form.cleaned_data['leave_type']
            leave_genre = form.cleaned_data['leave_genre']
            validation_passed = True

            # 1. Check for conflicts with existing leaves
            conflict_exists = check_leave_conflicts(employee, date, leave_genre)
            if conflict_exists:
                messages.error(request, "You already have a conflicting leave on this date.")
                validation_passed = False

            # 2. Check leave limits for restricted holiday, casual, and sick leaves
            if leave_type in ['casual', 'sick', 'restricted']:
                if not check_leave_balance(employee, leave_type, date, leave_genre):
                    messages.error(request, f"You have exceeded the allowed {leave_type} leave quota for this period.")
                    validation_passed = False
            
            exclude_saturdays=True
            if employee.position == '1':
                exclude_saturdays=False

            if date.weekday() == 6:  # Sunday
                messages.error(request, "Selected date is a Sunday")
                validation_passed = False
            if exclude_saturdays and date.weekday() == 5:  # Saturday
                messages.error(request, "Selected date is a Saturday")
                validation_passed = False
            if not exclude_saturdays and date.weekday() == 5:  # Saturday
                if (date.day - 1) // 7 == 1:  # Second Saturday
                    messages.error(request, "Selected date is a Second Saturday")
                    validation_passed = False

            # If validation passes, save the leave request
            if validation_passed:
                leave_request = form.save(commit=False)
                leave_request.employee = employee
                leave_request.status = 'pending'
                leave_request.save()
                messages.success(request,"Leave Applied")

                #code for adding the leave to timsheet
                create_leave_time_entry(request,leave_request)
                
                return redirect('leave_applications')
        else:
            print(form.errors)
            messages.error(request, "submitted form is invalid")
    else:
        form = LeaveRequestForm()
    remaining_leave_data = get_remaining_leave_data(user)
    return render(request, 'Leaves/leave_form.html', {
        'form': form,
        'employee_name':employee_name,
        'remaining_leave_data':remaining_leave_data,
        'action':'Apply',
        'operations': operations1,
        'level':level,
        'active_title':'Leave',
        'page_paths':['Leave','Leave Apply'],
    })

def create_leave_time_entry(request,leave_request):
    hrs = 0
    if leave_request.leave_genre == 'full_day':
        hrs = 8
    elif leave_request.leave_genre == 'first_half' or 'second_half':
        hrs = 4
    
    date=leave_request.date
    hours=hrs
    minutes=0
    seconds=0
    description=leave_request.reason
    project='leave hours'
    employee = leave_request.employee
    leave_id_entry = leave_request.id

    try:
        utc_now = datetime.now()
        if date > utc_now.date():
            raise ValidationError("time entry as date in future")

        if date and employee:
            join_date = employee.join_date
            if date < join_date:
                raise ValidationError("The timesheet entry date cannot be before the employee's join date.")

        if hours == 0 and minutes == 0 and seconds == 0:
            raise ValidationError("Total time must be greater than zero.")

        # Calculate total time in hours
        total_time = hours + (minutes / 60) + (seconds / 3600)

        # Check for existing timesheets on the same date
        if date:
            existing_timesheets = Timesheet.objects.filter(date=date)
            existing_total_time = sum(ts.hours + (ts.minutes / 60) + (ts.seconds / 3600) for ts in existing_timesheets)

            # Ensure total time does not exceed daily limit
            if existing_total_time + total_time > TOTAL_HOURS_IN_A_DAY:
                raise ValidationError(f"Total time for {date} exceeds {TOTAL_HOURS_IN_A_DAY} hours.")

        # Validate description length
        if description and len(description) > 1000:
            raise ValidationError("Description must be less than 1000 characters.")
        
        time_entry_leave = Timesheet.objects.filter(date=leave_request.date, employee=leave_request.employee, description=leave_request.reason).first()
        if time_entry_leave:
            raise ValidationError("Time entry already existing")

        # Create the timesheet entry
        obj = Timesheet.objects.create(
            date=date,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            description=description,
            project=project,
            employee=employee,
            leave_id_entry=leave_id_entry,
        )
        messages.success(request, 'Timesheet entry created successfully.')

    except ValidationError as e:
        # Handle validation errors
        error_str=""
        for error in e.messages:
            error_str += error
        return render(request,'test.html',{'error_str':error_str,})
    except Exception as e:
        # Handle any other exceptions
        messages.error(request, f"An error occurred: {str(e)}")
        error_str = str(e)
        return render(request,'test.html',{'error_str':error_str,}) 


def edit_leave(request, leave_id):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    # Retrieve the leave request to be edited
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    employee_name = leave_request.employee.name()

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            date = form.cleaned_data['date']
            leave_type = form.cleaned_data['leave_type']
            leave_genre = form.cleaned_data['leave_genre']
            validation_passed = True

            # 1. Check for conflicts with existing leaves, excluding the current leave request
            conflict_exists = check_leave_conflicts(user, date, leave_genre, exclude_id=leave_request.id)
            if conflict_exists:
                messages.error(request, "You already have a conflicting leave on this date.")
                validation_passed = False

            # 2. Check leave limits for restricted holiday, casual, and sick leaves
            if leave_type in ['casual', 'sick', 'restricted']:
                if not check_leave_balance(user, leave_type, date, leave_genre, exclude_id=leave_request.id):
                    messages.error(request, f"You have exceeded the allowed {leave_type} leave quota for this period.")
                    validation_passed = False

            # If validation passes, save the leave request
            if validation_passed:
                leave_request = form.save(commit=False)
                leave_request.status = 'pending'  # or keep the existing status if needed
                leave_request.save()
                if leave_request.id:
                    hrs = 0
                    if leave_request.leave_genre == 'full_day':
                        hrs = 8
                    elif leave_request.leave_genre == 'first_half' or leave_request.leave_genre == 'second_half':
                        hrs = 4
                    
                    leave_entry = Timesheet.objects.filter(leave_id_entry=leave_request.id).first()
                    if leave_entry:
                        leave_entry.date = leave_request.date
                        leave_entry.hours = hrs  # Assuming 'hours' is a field in Timesheet
                        leave_entry.minutes = 0  # Assuming 'minutes' is a field in Timesheet
                        leave_entry.seconds = 0  # Assuming 'seconds' is a field in Timesheet
                        leave_entry.description = leave_request.description  # Assuming this is a field
                        leave_entry.project = leave_request.project  # Assuming this is a field
                        leave_entry.save()  # Save the updated leave entry
                        messages.success(request, 'Time entry for leave is also updated')
                messages.success(request,"Leave Updated")
                return redirect('leave_applications')
        else:
            print(form.errors)
            messages.error(request, "Submitted form is invalid")
    else:
        form = LeaveRequestForm(instance=leave_request)

    remaining_leave_data = get_remaining_leave_data(user)
    return render(request, 'Leaves/leave_form.html', {
        'form': form,
        'employee_name':employee_name,
        'remaining_leave_data': remaining_leave_data,
        'action': 'Update',
        'leave':leave_request,
        'operations': operations1,
        'level': level,
        'active_title': 'Leave',
        'page_paths': ['Leaves', 'Edit Leave'],
    })

def delete_leave_time_entry(request,leave_request):
    time_entry_leave = Timesheet.objects.filter(date=leave_request.date, employee=leave_request.employee, description=leave_request.reason).first()
    if time_entry_leave:
        time_entry_leave.delete()
        messages.success(request, "Time entry also deleted")
    else:
        # messages.error(request, "Time entry with the leave not found")
        error_str=""
        error_str+="Time entry with the leave not found"
        error_str+="Date : " + str(leave_request.date)
        error_str+="Employee : " + str(leave_request.employee.name())
        error_str+="Date : " + str(leave_request.reason)
        return render(request,'test.html',{'error_str':error_str,})

def cancel_leave(request, leave_id):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    print("Leaeve id is : ",leave_id)
    print("Leaeve id is : ",leave_id)
    print("Leaeve id is : ",leave_id)
    print("Leaeve id is : ",leave_id)
    print("Leaeve id is : ",leave_id)
    print("Leaeve id is : ",leave_id)
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    if leave_request:
        delete_leave_time_entry(request,leave_request)
        leave_request.delete()
        messages.success(request, "Leave Cancelled")
        return redirect('leave_applications')
    else:
        messages.error(request, "Leave not found")
        return redirect('leave_applications')

def approve_leave(request, leave_id):
    validate_user = role_required(request=request, permission_name="manager")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    if leave_request:
        if user.level() == 2:
            if leave_request.employee.reporting_manager!=user:
                messages.error(request,"Not found as reporting manager")
                return redirect('leave_applications')
        leave_request.status = 'approved'
        leave_request.save()
        time_entry_leave = Timesheet.objects.filter(date=leave_request.date, employee=leave_request.employee, description=leave_request.reason).first()
        if not time_entry_leave:
            create_leave_time_entry(request,leave_request)
        messages.success(request,"Leave Approved")
        return redirect('leave_applications')
    else:
        messages.error(request,"Leave not found")
        return redirect('leave_applications')

def reject_leave(request, leave_id):
    validate_user = role_required(request=request, permission_name="manager")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    if leave_request:
        if user.level() == 2:
            if leave_request.employee.reporting_manager!=user:
                messages.error(request,"Not found as reporting manager")
                return redirect('leave_applications')
        leave_request.status = 'rejected'
        delete_leave_time_entry(request,leave_request)
        leave_request.save()
        messages.success(request,"Leave Rejected")
        return redirect('leave_applications')
    else:
        messages.error(request,"Leave not found")
        return redirect('leave_applications')    


def leave_applications(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    # Fetch leave applications for the logged-in user
    leave_requests = LeaveRequest.objects.filter(employee=user)
    user_is_the_employee = True
    
    if user.level()<=1:
        employees_list = Employee.objects.all()
    else:
        employees_list = Employee.objects.filter(reporting_manager = user)
    employees_list = list(employees_list)
    employees_list.append(user)

    selected_employee = user
    if request.method=='POST':
        employee_id = request.POST["employee_select"]
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, "Employee not exists")
        if employee==user:
            leave_requests = LeaveRequest.objects.filter(employee=employee)
        else:
            if user.level() <= 2:
                if employee.reporting_manager == user or (user.level()<=1):
                    leave_requests = LeaveRequest.objects.filter(employee=employee)
                    selected_employee = employee
                    user_is_the_employee = False
                else:
                    messages.error(request, "Employee not accessible")
            else:
                messages.error(request, "Employee not accessible ")

                


    item_list = leave_requests  # Get all data
    page_number = request.GET.get('page', 1)  # Get the page number
    items_per_page = 50  # Number of items per page
    paginator = Paginator(item_list, items_per_page)

    try:
        page_number = int(page_number)  # Ensure it's an integer
        items = paginator.page(page_number)  # Get the requested page
    except PageNotAnInteger:
        items = paginator.page(1)  # Default to first page if not an integer
    except EmptyPage:
        items = paginator.page(paginator.num_pages)  # Get last page if out of range
    print("Length after pagination : ",len(items))

    # Convert to list if needed
    paginated_items = list(items)

    # Render the leave applications in a template
    return render(request, 'Leaves/leave_applications.html', {
        'employee':user,
        'selected_employee': selected_employee,
        'employees_list':employees_list,
        'user_is_the_employee':user_is_the_employee,
        'leave_requests': paginated_items,
        'items':items,
        'operations': operations1,
        'level':level,
        'active_title':'Leave',
        'page_paths':['Leave','Leave Applications'],
    })


def get_projects(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    if request.method == "POST":
        date = request.POST["date"]
        if not date:
            return JsonResponse({"error": "Date is required"})
        try:
            selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format"}, status=400)
        custom_projects = [
            ('bench', 'Bench'),
            ('training', 'Training'),
            ('learning', 'Learning'),
        ]
        project_choices = []    
        if user.level() <= 1:
            project_choices = []
            projects = Project.objects.filter(
                start_date__lte=selected_date,  # start_date should be before or equal to selected_date
                end_date__gte=selected_date  # end_date should be after or equal to selected_date
            )
            for project in projects:
                project_choices.append((project.project_name, project.project_name))
            project_choices = project_choices + custom_projects


        elif user.level() == 2:
            assigned_projects = ProjectAssignation.objects.filter(
                Q(assigning_manager=user) | Q(employee=user)  # OR condition for user
                ).filter(
                start_date__lte=selected_date,  # start_date should be before or equal to selected_date
                end_date__gte=selected_date  # end_date should be after or equal to selected_date
            ).values_list('project__project_name', flat=True)
            assigned_projects = set(assigned_projects)
            project_choices = [(project, project) for project in assigned_projects] + custom_projects

        else:
            print("Checked the logged in user level ie employee")
            assigned_projects = ProjectAssignation.objects.filter(
                Q(employee=user)  # OR condition for user
                ).filter(
                start_date__lte=selected_date,  # start_date should be before or equal to selected_date
                end_date__gte=selected_date  # end_date should be after or equal to selected_date
            ).values_list('project__project_name', flat=True)
            for project in assigned_projects:
                print(project)
            project_choices = [(project, project) for project in assigned_projects] + custom_projects
            for project in project_choices:
                print(project)
        return JsonResponse({"project_choices":project_choices})

    else:
        return JsonResponse({"error":"Not a POST request"})


def password_update(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)

    if request.method == 'POST':
        current_password = request.POST.get('c_password')
        new_password = request.POST.get('n_password')
        confirm_new_password = request.POST.get('c_n_password')

        if check_password(current_password, user.password_hash):  
            if new_password == current_password:
                messages.error(request, "New password cannot be the same as the current password.")
            elif new_password != confirm_new_password:
                messages.error(request, "New password and confirmation do not match.")
            else:
                has_lower_case = any(c.islower() for c in new_password)
                has_upper_case = any(c.isupper() for c in new_password)
                has_special_char = any(c in "!@#$%^&*" for c in new_password)
                has_digit = any(c.isdigit() for c in new_password)
                is_length_valid = 8 <= len(new_password) <= 16

                if not has_lower_case:
                    raise ValidationError("Password must contain at least one lowercase letter.")
                if not has_upper_case:
                    raise ValidationError("Password must contain at least one uppercase letter.")
                if not has_special_char:
                    raise ValidationError("Password must contain at least one special character.")
                if not has_digit:
                    raise ValidationError("Password must contain at least one digit.")
                if not is_length_valid:
                    raise ValidationError("Password must be 8-16 characters long.")
                
                user.password_hash = make_password(new_password) 
                user.save()
                messages.success(request, "Password updated successfully.")
        else:
            messages.error(request, "Current password is incorrect.")
    return redirect(profile_view)
        

def profile_update(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]
    
    if request.method == 'POST':
        form = EmployeeProfileUpdateForm(request.POST,instance=user,logged_in_user=user)
        if form.is_valid():
            form.save()
            messages.success(request,"Profile Updated")
        else:
            print(form.errors)
            messages.error(request, "submitted form is invalid")
        return redirect(profile_view)
    else:
        form = EmployeeProfileUpdateForm(instance=user,logged_in_user=user)
        reporting_manager_name = user.reporting_manager.name() if user.reporting_manager else "Nil"
        department_name = user.department.department_name if user.department else "Nil"

        role_name = user.get_role_display() if user.role else "Nil"
        position_name = user.get_position_display() if user.position else "Nil"
    return render(request, 'profile_update_form.html', {
        'reporting_manager_name': reporting_manager_name,
        'department_name': department_name,
        'position_name': position_name,
        'role_name': role_name,
        'form': form,
        'user':user,
        'action':'Update',
        'operations': operations1,
        'level':level,
        'active_title':'Profile',
        'page_paths':['Profile','Edit Profile'],
    })


def toggle_check_in_check_out(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    is_check_in = is_user_checked_in(user)
    today = localtime().date()
    print("Today date : ",today)
    yesterday = today - timedelta(days=1)
    print("Yesterday Date : ",yesterday)

    if is_check_in:
        check_out = CheckInOut.objects.create(employee=user, is_check_in=False)
    else:
        check_in = CheckInOut.objects.create(employee=user, is_check_in=True)
    
    
    attendance_yesterday = calculate_attendance(user,yesterday)

    attendance = calculate_attendance(user,today)
    is_check_in = is_user_checked_in(user)
    total_seconds = attendance.total_worked_seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
    return JsonResponse({
        "is_check_in": is_check_in,
        "hours":hours,
        "minutes":minutes,
        "seconds":seconds,
        "time_string":time_string,
    })

def get_total_time_worked(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    today = localtime().date()  
    start_of_day = make_aware(datetime(today.year, today.month, today.day, 0, 0, 0))  # Start of today
    end_of_day = make_aware(datetime(today.year, today.month, today.day, 23, 59, 59))  # End of today

    check_ins_outs = CheckInOut.objects.filter(
        employee=user,
        timestamp__gte=start_of_day,  # Greater than or equal to start of today
        timestamp__lte=end_of_day,  # Less than or equal to end of today
    )

    # Total worked hours calculation
    total_worked_time = timedelta()
    last_check_in_time = None

    if check_ins_outs.exists():
        for entry in check_ins_outs:
            entry_time_ist = localtime(entry.timestamp)  # Convert each entry timestamp to IST
            if entry.is_check_in:
                last_check_in_time = entry_time_ist
            else:
                if last_check_in_time:
                    total_worked_time += (entry_time_ist - last_check_in_time)
                    last_check_in_time = None

        last_check_out_ist = localtime(check_ins_outs.last().timestamp)
        now = localtime()
        if check_ins_outs.last().is_check_in:
            total_worked_time += now - last_check_out_ist

    total_worked_seconds = total_worked_time.total_seconds()
         
    is_check_in = is_user_checked_in(user)
    total_seconds = int(total_worked_seconds)
    print("Total seconds is :", total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    print("Hours :", hours,"Minutes :",minutes, "Seconds :",seconds)
    time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
    print("Time worked is ", time_string)
    return JsonResponse({
        "is_check_in": is_check_in,
        "hours":hours,
        "minutes":minutes,
        "seconds":seconds,
        "time_string":time_string,
    })


def shift_initializing_code(request):
    shift, created = Shift.objects.get_or_create(
        name="General Shift"
    )

    employees = Employee.objects.all()
    for employee in employees:
        employee.shift = shift
        employee.save()

    if created:
        response_data = {
            "message": "A new Shift object was created.",
            "shift_id": shift.id,  # Optionally include the ID of the created shift
            "shift_name": shift.name,
        }
    else:
        response_data = {
            "message": "The Shift object already exists.",
            "shift_id": shift.id,  # Optionally include the ID of the existing shift
            "shift_name": shift.name,
        }
    return JsonResponse(response_data)

def attendance_tabular_view(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    week_or_month="week"
    today = datetime.now()
    start_of_week_timestamp = today - timedelta(days=today.weekday())  # Monday is the start of the week
    end_of_week_timestamp = start_of_week_timestamp + timedelta(days=6)  # Sunday is the end of the week
    start_date_of_week = start_of_week_timestamp.date()
    end_date_of_week = end_of_week_timestamp.date()
    month = datetime.now().strftime("%B")
    start_date_of_month = today.replace(day=1).date()
    if today.month == 12:
        end_date_of_month = datetime(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date_of_month = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
    end_date_of_month = end_date_of_month.date()
    print("The Employee is : ", user.name())
    print("The Employee is : ", user.name())
    print("The Employee is : ", user.name())
    print("The Employee is : ", user.name())
    print("The Employee  ID is : ", user.employee_id)

    data = generate_attendance_list(start_date_of_week,end_date_of_week, user.employee_id)
    

    if request.method == "POST":
        action = request.POST.get("action_for_view")
        week_or_month = request.POST.get("week_or_month")
        start_date_of_week = request.POST.get("current_week_start_date")
        end_date_of_week = request.POST.get("current_week_end_date")
        start_date_of_month = request.POST.get("current_month_start_date")
        month = request.POST.get("current_month")

        today = datetime.now()

        if week_or_month == "week":
            start_date_of_week = datetime.strptime(request.POST.get("current_week_start_date"), "%B %d, %Y")
            if action == "next":
                start_date_of_week += timedelta(days=7)
            elif action == "previous":
                start_date_of_week -= timedelta(days=7)
            start_of_week_timestamp = start_date_of_week
            end_of_week_timestamp = start_of_week_timestamp + timedelta(days=6)
            end_date_of_week = end_of_week_timestamp.date()
            start_date_of_week = start_of_week_timestamp.date()

            month_data = majority_month(start_date_of_week, end_date_of_week)
            month = month_data["month_name"]
            start_date_of_month = month_data["month_start_date"]
            end_date_of_month = month_data["month_end_date"]

        else:  # month
            start_date_of_month = datetime.strptime(request.POST.get("current_month_start_date"), "%B %d, %Y")
            if action == "next":
                next_month = start_date_of_month.month + 1 if start_date_of_month.month < 12 else 1
                year = start_date_of_month.year if next_month > 1 else start_date_of_month.year + 1
                start_date_of_month = datetime(year, next_month, 1).date()
            elif action == "previous":
                prev_month = start_date_of_month.month - 1 if start_date_of_month.month > 1 else 12
                year = start_date_of_month.year if prev_month < 12 else start_date_of_month.year - 1
                start_date_of_month = datetime(year, prev_month, 1).date()

            start_date_of_month = datetime.combine(start_date_of_month, datetime.min.time())
            end_date_of_month = (datetime(start_date_of_month.year, start_date_of_month.month + 1, 1) - timedelta(days=1)).date()
            start_date_of_month = start_date_of_month.date()
            month = start_date_of_month.strftime("%B")

            start_month_timestamp = datetime.combine(start_date_of_month, datetime.min.time())

            start_date_of_week_timestamp = start_month_timestamp - timedelta(days=start_month_timestamp.weekday())
            start_date_of_week = start_date_of_week_timestamp.date()
            end_date_of_week = (start_date_of_week_timestamp + timedelta(days=6)).date()

        if action in ["month", "week"]:
            if action == "month" :
                week_or_month = "month" 
            elif action == "week" :
                week_or_month = "week"
            else:
                pass
        if week_or_month == "month":
            start_date = start_date_of_month
            end_date = end_date_of_month
        else:
            start_date = start_date_of_week
            end_date = end_date_of_week

        # Fetch updated attendance list
        data = generate_attendance_list(start_date, end_date, user.employee_id)

        week_start = start_date_of_week
        week_end = end_date_of_week

        start_date_of_week = start_date_of_week.strftime("%B %d, %Y")
        end_date_of_week = end_date_of_week.strftime("%B %d, %Y")
        start_date_of_month = start_date_of_month.strftime("%B %d, %Y")
        end_date_of_month =  end_date_of_month.strftime("%B %d, %Y")
        action = "idle"

        rendered_html = render_to_string("attendance/attendance_tabular_changed_view.html", {
            "attendance_list": data,
            "week_or_month": week_or_month,
            "current_week_start_date": start_date_of_week,
            "current_week_end_date": end_date_of_week,
            "current_month_start_date": start_date_of_month,
            "current_month_end_date": end_date_of_month,
            "week_start":week_start,
            "week_end":week_end,
            "current_month": month,
            "action" : action,
        })

        # Prepare the response data
        response_data = {
            "html": rendered_html,
        }

        # Return a JSON response with the rendered HTML
        return JsonResponse(response_data)

    return render(request, 'attendance/attendance_tabular_view.html', {
        'user':user,
        'operations': operations1,
        'level':level,
        'active_title' : 'Attendance',
        'page_paths': ['Attendance','Tabular View'],
        'attendance_list' : data,
        'week_or_month' : week_or_month,
        'current_week_start_date' : start_date_of_week,
        'current_week_end_date' : end_date_of_week,
        'current_month_start_date' : start_date_of_month,
        'current_month_end_date' : end_date_of_month,
        'week_start': start_date_of_week,
        'week_end' : end_date_of_week,
        'current_month' : month,
        'action':"idle",
    })

def attendance_audit_history(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    today = datetime.now()
    current_date = today
    if request.method == 'POST':
        data = json.loads(request.body)
        current_date_str = data.get('date')
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()

        check_in_outs = log_timings(user,current_date)

        date_display = current_date.strftime("%A, %B %d, %Y")
        current_date = current_date.strftime("%Y-%m-%d")
        html_response = render_to_string('attendance/audit_history_filtered.html', {
            'date_display' : date_display,
            'current_date' : current_date,
            'check_in_outs' : check_in_outs,
            'user':user,
        })
        return JsonResponse({'html': html_response})

    check_in_outs = log_timings(user,current_date)

    date_display = current_date.strftime("%A, %B %d, %Y")
    current_date = current_date.strftime("%Y-%m-%d")
    return render(request, 'attendance/attendance_audit_history.html', {
        'date_display':date_display,
        'current_date':current_date,
        'check_in_outs':check_in_outs,
        'user':user,
        'operations': operations1,
        'level':level,
        'active_title' : 'Attendance',
        'page_paths': ['Attendance','Audit History'],
    })



def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Employee.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.employee_id))
            token = token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'your_email@gmail.com',
                [email],
                fail_silently=False,
            )
            return redirect('password_reset_sent')
        except Employee.DoesNotExist:
            messages.error(request, "No user found with that email.")
    return render(request, 'password/password_reset_form.html')


def password_reset_sent(request):
    return render(request, 'password/password_reset_sent.html')



def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Employee.objects.get(employee_id=uid)
    except (TypeError, ValueError, OverflowError, Employee.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.password = make_password(password1)  # Make sure to hash in real use!
                user.save()
                return redirect('password_reset_complete')
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, 'password/password_reset_confirm.html', {'validlink': True})
    else:
        return render(request, 'password/password_reset_confirm.html', {'validlink': False})
    

def password_reset_complete(request):
    return render(request, 'password/password_reset_complete.html')
