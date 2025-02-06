from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
import jwt

from EMPPORTAL import settings
from emp_portal_app.auth import get_current_user, role_required
from .operations_by_role import operations

from .forms import *
from .utils import create_access_token,check_refresh_token,create_refresh_token,insert_refresh_token, is_refresh_token_active, make_refresh_token_inactive

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
    return render(request, 'department_list.html', {'departments': departments, 'operations': operations1, 'level':int(level)})


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
    return render(request, 'department_form.html', {'form': form, 'action': 'Create', 'operations': operations1, 'level':int(level)})


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
    return render(request, 'department_form.html', {'form': form, 'action': 'Update', 'operations': operations1, 'level':int(level)})


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
    return render(request, 'department_confirm_delete.html', {'department': department, 'operations': operations1, 'level':int(level)})



def employee_list(request):
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees, 'operations': operations1, 'level':int(level)})


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
    return render(request, 'employee_form.html', {'form': form, 'action': 'Create', 'operations': operations1, 'level':int(level)})


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
    return render(request, 'employee_form.html', {'form': form, 'action': 'Update', 'operations': operations1, 'level':int(level)})


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
    return render(request, 'employee_disable_form.html', {'employee': employee,'form':form, 'operations': operations1, 'level':int(level)})




def login(request):
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
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    return render(request, 'home.html', {'operations': operations1, 'level':int(level)})




def project_list(request):
    validate_user = role_required(request=request,permission_name="employee")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    projects = Project.objects.all().order_by('created_at')
    return render(request, 'projects/project_list.html', {'projects': projects, 'operations': operations1, 'level':int(level)})

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
    return render(request, 'projects/project_form.html', {'form': form, 'operations': operations1, 'level':int(level)})

def project_update(request, pk):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form ': form, 'operations': operations1, 'level':int(level)})

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
    return render(request, 'projects/project_confirm_delete.html', {'project': project, 'operations': operations1, 'level':int(level)})

def project_individual_view(request, pk):
    validate_user = role_required(request=request,permission_name="admin")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_individual_view.html', {'project': project, 'operations': operations1, 'level':int(level)})


def employees_under_manager(request):
    validate_user = role_required(request=request,permission_name="manager")
    if isinstance(validate_user, JsonResponse):
        return validate_user
    user = get_current_user(request)
    level = user.role
    operations1 = operations[level]
    manager = user

    # Get all employees reporting to this manager
    employees = Employee.objects.filter(reporting_manager=manager)

    # Render the template with the manager and their employees
    return render(request, 'employees_under_manager.html', {
        'manager': manager,
        'employees': employees, 'operations': operations1, 'level':int(level)
    })