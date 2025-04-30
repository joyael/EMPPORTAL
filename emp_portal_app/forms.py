from datetime import datetime, date, timezone
from django import forms
from django.core.validators import MaxLengthValidator,MinValueValidator, RegexValidator

from emp_portal_app.helper_functions import check_overlap
from .models import LeaveRequest, Permission, Department, Employee, Project, ProjectAssignation, Timesheet
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
        employee = cleaned_data.get('employee')
        instance=self.instance

        pas = ProjectAssignation.objects.filter(employee=employee,project=project)
        pas = pas.exclude(assign_id=instance.assign_id)
        for pa in pas:
            if check_overlap(pa.start_date,pa.end_date,start_date,end_date):
                raise ValidationError('Same project and employee overlapping on the existing date range on a project assignation')

        if project and assigning_manager:
            if project.manager != assigning_manager:
                raise ValidationError('The assigning manager must be the manager of the selected project.')

        if start_date and end_date and end_date <= start_date:
            raise ValidationError('End date must be greater than start date.')

        return cleaned_data
    


TOTAL_HOURS_IN_A_DAY = 8

class TimesheetForm(forms.ModelForm):
    project = forms.ChoiceField(choices=[], required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Timesheet
        fields = ['date', 'project', 'hours', 'minutes', 'seconds', 'task_id', 'description']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'date' : forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        self.logged_in_user = kwargs.pop('logged_in_user', None)
        super(TimesheetForm, self).__init__(*args, **kwargs)

        starting_choices=[
            ('nil','Select Project'),
        ]
        self.fields['project'].choices = starting_choices
 

    def clean_project(self):
        project = self.cleaned_data.get('project')
        valid_projects = [project.project_name for project in Project.objects.all()] + ['bench', 'learning', 'training', 'leave hours']
        if project not in valid_projects:
            raise forms.ValidationError("Invalid project. Please select a valid project or use 'bench', 'learning', or 'training'.")
        return project

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        hours = cleaned_data.get('hours', 0)
        minutes = cleaned_data.get('minutes', 0)
        seconds = cleaned_data.get('seconds', 0)
        employee = cleaned_data.get('employee')

        if date > datetime.now().date():
            raise forms.ValidationError("The date cannot be in the future.")
        
        if date and employee:
            join_date = employee.join_date
            if date < join_date:
                raise forms.ValidationError("The timesheet entry date cannot be before the employee's join date.")

        if hours == 0 and minutes == 0 and seconds == 0:
            raise forms.ValidationError("Total time must be greater than zero.")
        
        total_time = hours + (minutes / 60) + (seconds / 3600)

        if date:
            existing_timesheets = Timesheet.objects.filter(date=date)
            existing_total_time = sum(ts.hours + (ts.minutes / 60) + (ts.seconds / 3600) for ts in existing_timesheets)

            if existing_total_time + total_time > TOTAL_HOURS_IN_A_DAY:
                raise forms.ValidationError(f"Total time for {date} exceeds {TOTAL_HOURS_IN_A_DAY} hours.")

        description = cleaned_data.get('description')
        if description and len(description) > 1000:
            raise forms.ValidationError("Description must be less than 1000 characters.")

        return cleaned_data
    
class TimesheetUpdateForm(forms.ModelForm):
    project = forms.ChoiceField(choices=[], required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Timesheet
        fields = ['date', 'project', 'hours', 'minutes', 'seconds', 'task_id', 'description']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.logged_in_user = kwargs.pop('logged_in_user', None)
        super(TimesheetForm, self).__init__(*args, **kwargs)

        starting_choices=[
            ('nil','Select Project'),
        ]
        self.fields['project'].choices = starting_choices
    def clean_project(self):
        project = self.cleaned_data.get('project')
        valid_projects = [project.project_name for project in Project.objects.all()] + ['bench', 'learning', 'training', 'leave hours']
        if project not in valid_projects:
            raise forms.ValidationError("Invalid project. Please select a valid project or use 'bench', 'learning', or 'training'.")
        return project

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        hours = cleaned_data.get('hours', 0)
        minutes = cleaned_data.get('minutes', 0)
        seconds = cleaned_data.get('seconds', 0)
        employee = cleaned_data.get('employee')

        if date > datetime.timezone.now().date():
            raise forms.ValidationError("The date cannot be in the future.")
        
        if date and employee:
            join_date = employee.join_date
            if date < join_date:
                raise forms.ValidationError("The timesheet entry date cannot be before the employee's join date.")

        if hours == 0 and minutes == 0 and seconds == 0:
            raise forms.ValidationError("Total time must be greater than zero.")
        
        total_time = hours + (minutes / 60) + (seconds / 3600)

        if date:
            existing_timesheets = Timesheet.objects.filter(date=date)
            existing_total_time = sum(ts.hours + (ts.minutes / 60) + (ts.seconds / 3600) for ts in existing_timesheets)
            existing_total_time -= total_time

            if existing_total_time + total_time > TOTAL_HOURS_IN_A_DAY:
                raise forms.ValidationError(f"Total time for {date} exceeds {TOTAL_HOURS_IN_A_DAY} hours.")

        description = cleaned_data.get('description')
        if description and len(description) > 1000:
            raise forms.ValidationError("Description must be less than 1000 characters.")

        return cleaned_data
    

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['date', 'leave_type', 'leave_genre','reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Use a date input widget for the date field
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter reason...'}),
        }
        labels = {
            'leave_type': 'Leave Type',
            'date': 'Leave Date',
            'leave_genre': 'Full day or Half day',
            'reason': 'Reason',
        }
        



class EmployeeProfileUpdateForm(forms.ModelForm):
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
        ]
        labels = {
            'DOB': 'Date of Birth',
            'join_date': 'Join Date',
        }
        widgets = {
            'DOB': forms.DateInput(attrs={'type': 'date'}),  
            'join_date': forms.DateInput(attrs={'type': 'date'}),  
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
        
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, email):
            raise ValidationError("Please enter a valid email address.")
        
        instance = self.instance
        the_other_employee =  Employee.objects.filter(email=email).exclude(employee_id=instance.employee_id).first()
        if the_other_employee:
            print(the_other_employee.employee_id)
            print(instance.employee_id)
            raise forms.ValidationError("An employee with this email already exists. BYE BYE")
        return email


    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone
    
    def __init__(self, *args, **kwargs):
        self.logged_in_user = kwargs.pop('logged_in_user', None)
        super(EmployeeProfileUpdateForm, self).__init__(*args, **kwargs)

        if self.logged_in_user and self.logged_in_user.level() > 1:
            self.fields['join_date'].widget.attrs['readonly'] = 'readonly'

            self.fields['join_date'].disabled = True
            self.fields['reporting_manager'].disabled = True
            self.fields['role'].disabled = True
            self.fields['department'].disabled = True
            self.fields['position'].disabled = True


            self.fields['join_date'].initial = self.instance.join_date
            self.fields['reporting_manager'].initial = self.instance.reporting_manager
            self.fields['role'].initial = self.instance.reporting_manager
            self.fields['department'].initial = self.instance.department
            self.fields['position'].initial = self.instance.position

            self.fields['join_date'].widget = forms.DateInput(attrs={'readonly': 'readonly',})
            self.fields['reporting_manager'].widget = forms.TextInput(attrs={'readonly': 'readonly'})
            self.fields['role'].widget = forms.TextInput(attrs={'readonly': 'readonly'})
            self.fields['department'].widget = forms.TextInput(attrs={'readonly': 'readonly'})
            self.fields['position'].widget = forms.TextInput(attrs={'readonly': 'readonly'})

            self.fields['join_date'].required = False
            self.fields['reporting_manager'].required = False
            self.fields['role'].required = False
            self.fields['department'].required = False
            self.fields['position'].required = False

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
