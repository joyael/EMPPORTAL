from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import jwt

from django.db.models import Q

from EMPPORTAL import settings
from emp_portal_app.auth import get_current_user, role_required
from emp_portal_app.models import SHIFT_HOURS_IN_A_DAY, CheckInOut
from .helper_functions import calculate_attendance, check_leave_balance, check_leave_conflicts, get_dates, get_remaining_leave_data, get_the_break_down_total_data, get_the_overview_total_data, is_user_checked_in, timesheeet_overview_data_extract
from .operations_by_role import operations

from .forms import *
from .utils import create_access_token, check_refresh_token, create_refresh_token, insert_refresh_token, is_refresh_token_active, make_refresh_token_inactive

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login as session_login

from django.contrib.auth.hashers import make_password

from django.contrib.sessions.models import Session
import json


from allauth.socialaccount.models import SocialAccount

from datetime import datetime, timedelta
from django.utils.timezone import now
from emp_portal_app.models import CASUAL_LEAVE_QUARTERLY_COUNT, RH_YEARLY_COUNT, SHIFT_HOURS_IN_A_DAY, SICK_LEAVE_QUARTERLY_COUNT



# Create your views here.

def refresh_token_view(request):
    refresh_token = request.COOKIES.get('refresh_token')  # Get the refresh token from the cookie
    if not refresh_token:
        return JsonResponse({'error': 'Refresh token not found'}, status=401)
    if check_refresh_token(refresh_token):
        if not is_refresh_token_active:
            return JsonResponse({'error': 'Refresh token Inactivated'}, status=401)
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = Employee.objects.get(employee_id=user_id)

        # Generate a new access token
        new_access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)

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
    return render(request, 'department_list.html', {'departments': departments, 'operations': operations1, 'level':int(level),'active_title':'Departments'})


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
    return render(request, 'employee_list.html', {'employees': employees, 'operations': operations1, 'level':int(level),'active_title':'Employees'})


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
    return render(request, 'employee_form.html', {'form': form, 'action': 'Create', 'operations': operations1, 'level':int(level),'active_title':'Employees'})


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
    return render(request, 'employee_form.html', {'form': form, 'action': 'Update', 'operations': operations1, 'level':int(level),'active_title':'Employees'})


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
    return render(request, 'employee_disable_form.html', {'employee': employee,'form':form, 'operations': operations1, 'level':int(level),'active_title':'Employees'})



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
    return render(request, 'projects/project_list.html', {'projects': projects, 'operations': operations1, 'level':int(level),'active_title':'Projects'})

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
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Create', 'operations': operations1, 'level':int(level),'active_title':'Projects'})

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
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Update', 'operations': operations1, 'level': int(level),'active_title':'Projects'})

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
    return render(request, 'projects/project_confirm_delete.html', {'project': project, 'operations': operations1, 'level':int(level),'active_title':'Projects'})

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
            received_date = timezone.datetime.strptime(date_input, '%Y-%m-%d').date()
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

    sessions = Session.objects.filter(expire_date__gte=timezone.now())  # Active sessions
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
            selected_project = form.cleaned_data.get('project')

            if selected_project not in ['bench', 'training', 'learning']:
                project_instance = get_object_or_404(Project, project_name=selected_project)
                timesheet.project_real = project_instance
            
            timesheet.save()

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

            # If validation passes, save the leave request
            if validation_passed:
                leave_request = form.save(commit=False)
                leave_request.employee = employee
                leave_request.status = 'pending'
                leave_request.save()
                return redirect('leave_applications')
        else:
            print(form.errors)
            messages.error(request, "submitted form is invalid")
    else:
        form = LeaveRequestForm()
    remaining_leave_data = get_remaining_leave_data(user)
    return render(request, 'Leaves/leave_form.html', {
        'form': form,
        'remaining_leave_data':remaining_leave_data,
        'action':'Apply',
        'operations': operations1,
        'level':level,
        'active_title':'Leave Apply',
        'page_paths':['Leave','Leave Apply'],
    })

def leave_applications(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user

    user = get_current_user(request)
    level = user.level()
    operations1 = operations[str(level)]

    # Fetch leave applications for the logged-in user
    leave_requests = LeaveRequest.objects.filter(employee=user)

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
        'leave_requests': paginated_items,
        'items':items,
        'operations': operations1,
        'level':level,
        'active_title':'Leave Applications',
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
        form = EmployeeProfileUpdateForm(request.POST,logged_in_user=user)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            messages.error(request, "submitted form is invalid")
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
        'active_title':'Edit Profile',
        'page_paths':['Profile','Edit Profile'],
    })


def toggle_check_in_check_out(request):
    validate_user = role_required(request=request, permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    is_check_in = is_user_checked_in(user)
    today = datetime.today().date()
    if is_check_in:
        check_out = CheckInOut.objects.create(employee=user, is_check_in=False)
    else:
        check_in = CheckInOut.objects.create(employee=user, is_check_in=True)

    calculate_attendance(user,today)
    is_check_in = is_user_checked_in(user)
    return JsonResponse({
        "is_check_in": is_check_in,
    })