from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

from emp_portal_app.auth import get_current_user, role_required
from .operations_by_role import operations

from .forms import *
from .utils import create_access_token,check_refresh_token,create_refresh_token,insert_refresh_token

# Create your views here.

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
    departments = Department.objects.all()
    return render(request, 'department_list.html', {'departments': departments})


def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'department_form.html', {'form': form, 'action': 'Create'})


def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'department_form.html', {'form': form, 'action': 'Update'})


def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'department_confirm_delete.html', {'department': department})



def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})


def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Employee Created successfully")
            return redirect('employee_list') 
    else:
        form = EmployeeForm()
    return render(request, 'employee_form.html', {'form': form, 'action': 'Create'})


def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list') 
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_form.html', {'form': form, 'action': 'Update'})


def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')  
    return render(request, 'employee_confirm_delete.html', {'employee': employee})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Get the email from the POST data
        password = request.POST.get('password_hash')  # Get the password from the POST data
        
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
    return render(request, 'home.html', {'operations': operations1, 'level':level})
    
