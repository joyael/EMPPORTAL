from django import forms
from django.core.validators import MaxLengthValidator,MinValueValidator, RegexValidator
from .models import Permission, Department, Employee


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
            'DOB': forms.DateInput(attrs={'type': 'date'}),  # Date input for DOB
            'join_date': forms.DateInput(attrs={'type': 'date'}),  # Date input for join_date
        }

        


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