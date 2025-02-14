import datetime
from django import forms
from django.core.validators import MaxLengthValidator,MinValueValidator, RegexValidator
from .models import Permission, Department, Employee, Project, ProjectAssignation
from django.core.exceptions import ValidationError
import re


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name', 'level']




class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'description']

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea(attrs={
            'placeholder': 'Enter department description',
            'rows': 5,
            'cols': 40,
        })

    def clean_department_name(self):
        department_name = self.cleaned_data.get('department_name')
        if not department_name:
            raise ValidationError("Department Name is required.")
        if len(department_name) > 100:
            raise ValidationError("Department Name must be less than 100 characters.")
        return department_name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise ValidationError("Description is required.")
        if len(description) > 1000:
            raise ValidationError("Department Description must be less than 1000 characters.")
        return description

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name', 
            'last_name', 
            'DOB', 
            'email', 
            'phone', 
            'join_date', 
            'reporting_manager', 
            'role', 
            'department', 
            'position', 
            'password_hash'
        ]

        labels = {
            'password_hash': 'Password',
            'DOB': 'Date of Birth',
            'join_date': 'Join Date',
        }
        widgets = {
            'password_hash': forms.PasswordInput(render_value=True),
            'DOB': forms.DateInput(attrs={'type': 'date'}),  #Date input for DOB
            'join_date': forms.DateInput(attrs={'type': 'date'}),  #Date input for join_date
        }


    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError("First name is required.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError("Last name is required.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            raise ValidationError("Please enter a valid email address.")
        
        if Employee.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        return phone

    def clean_password_hash(self):
        password = self.cleaned_data.get('password_hash')
        
        if not password:
            raise ValidationError("Password is required.")
        
        has_lower_case = any(c.islower() for c in password)
        has_upper_case = any(c.isupper() for c in password)
        has_special_char = any(c in "!@#$%^&*" for c in password)
        has_digit = any(c.isdigit() for c in password)
        is_length_valid = 8 <= len(password) <= 16

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
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
        


class EmployeeLoginForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['email', 'password_hash']  

        labels = {
            'password_hash': 'Password',
        }
        widgets = {
            'password_hash': forms.PasswordInput(render_value=True),
            
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_name',
            'manager',
            'status',
            'comment',
            'description',
            'start_date',
            'end_date',
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a comment'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter project description', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['manager'].queryset = Employee.objects.filter(status='active', role='2')  # Assuming '2' is the role for Manager

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        description = cleaned_data.get('description')

        if start_date and end_date and end_date <= start_date:
            raise ValidationError('End date must be greater than start date.')
        
        if description and len(description) > 1000:
            raise ValidationError('Description must not exceed 1000 characters.')

        return cleaned_data


class EmployeeStatusForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['status']

        labels = {
            'status': 'Employee Status',
        }

        widgets = {
            'status': forms.Select(),
        }




class ProjectAssignationForm(forms.ModelForm):
    class Meta:
        model = ProjectAssignation
        fields = [
            'project',
            'employee',
            'role',
            'status',
            'start_date',
            'end_date',
            'assigning_manager',
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter role'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.logged_in_user = kwargs.pop('logged_in_user', None)
        super(ProjectAssignationForm, self).__init__(*args, **kwargs)
            
        if self.logged_in_user.level() <= 1:
            self.fields['assigning_manager'].queryset = Employee.objects.all()
        else:
            self.fields.pop('assigning_manager')
            self.fields['project'].queryset = Project.objects.filter(manager=self.logged_in_user)

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        assigning_manager = cleaned_data.get('assigning_manager')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if project and assigning_manager:
            if project.manager != assigning_manager:
                raise ValidationError('The assigning manager must be the manager of the selected project.')

        if start_date and end_date and end_date <= start_date:
            raise ValidationError('End date must be greater than start date.')

        return cleaned_data