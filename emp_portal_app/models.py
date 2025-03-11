from django.db import models
from django.contrib.auth.hashers import make_password
from datetime import datetime

#Create your models here.

class RefreshToken(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'refreshtokens'
    
    def __str__(self):
        return f"{self.token[:5]}... {self.check_active()}"
    
    def check_active(self):
        return "Active" if self.is_active else "Not Active"

class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    level = models.IntegerField()

    class Meta:
        db_table = 'permissions'

    def __str__(self):
        return self.name
    
    

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Department'

    def __str__(self):
        return self.department_name


class Employee(models.Model): 
    employee_id = models.AutoField(primary_key=True) 
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50) 
    DOB = models.DateField() 
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True) 
    join_date = models.DateField() 
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    ROLE_CHOICES = [
        ('1', 'Admin'),
        ('2', 'Manager'),
        ('3', 'Employee'),
    ]
    role = models.CharField(
        max_length=2,
        choices= ROLE_CHOICES,
        default='1',
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    POSITION_CHOICES = [
        ('0','Nil'),
        ('1', 'Trainee'),
        ('2', 'Software Engineer'),
        ('3', 'Senior Software Engineer'),
        ('4', 'Project Manager'),
        ('5', 'UI/UX Engineer'),
        ('6', 'Senior UI/UX Engineer'),
        ('7', 'Software Tester'),
    ]
    position = models.CharField(
        max_length=2,
        choices=POSITION_CHOICES,
        default='1',
    )

    password_hash = models.CharField(max_length=128)  # Hashed password
    created_at = models.DateTimeField(auto_now_add=True)
    EMPLOYEE_STATUS_CHOICES = [
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
        ('temporarily_not_exists', 'Temporarily not Exists'),
        ('deceased', 'Deceased'),
        ('active', 'Active'),
        ('not_active','Not Active'),
    ]
    status = models.CharField(
        max_length=50,
        choices= EMPLOYEE_STATUS_CHOICES,
        default='active',
    )

    def save(self, *args, **kwargs):
        if not self.password_hash.startswith('pbkdf2_sha256$'):
            self.password_hash = make_password(self.password_hash)
        super().save(*args, **kwargs)

    def level(self):
        return int(self.role)
    def name(self):
        return f"{self.first_name} {self.last_name}"
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'employees'



class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=200)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('withdrawn', 'Withdrawn'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    comment = models.CharField(max_length=200,blank=True,null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.project_name
    

class ProjectAssignation(models.Model):
    assign_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # Correctly references Project
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignations')  # Correctly references Employee
    assigning_manager = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='managed_assignations')  # Correctly references Employee
    role = models.CharField(max_length=200, blank=True, null=True)
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('withdrawn', 'Withdrawn'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
        ('archived', 'Archived'),
    ] 
    status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.project.project_name} - {self.employee.first_name} {self.employee.last_name} ({self.role})"
    
SHIFT_HOURS_IN_A_DAY = 8

class Timesheet(models.Model):
    date = models.DateField()  
    hours = models.IntegerField() 
    minutes = models.IntegerField()  
    seconds = models.IntegerField() 
    task_id = models.CharField(max_length=255, null=True, blank=True) 
    description = models.TextField(blank=True)  
    project = models.CharField(max_length=255)  
    project_real = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f'Timesheet for {self.date} - {self.hours}h {self.minutes}m {self.seconds}s'

    def formatted_date(self):
        return self.date.strftime('%a, %d-%b-%Y')
    
    class Meta:
        verbose_name = 'Timesheet'
        verbose_name_plural = 'Timesheets'
    
    def total_hours_decimal(self):
        total_hours = self.hours + (self.minutes / 60) + (self.seconds / 3600)
        num = round(total_hours, 2)
        float_num = format(num, ".2f")
        return float_num 
    

RH_YEARLY_COUNT = 2
CASUAL_LEAVE_QUARTERLY_COUNT = 3
SICK_LEAVE_QUARTERLY_COUNT = 1.5

class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    LEAVE_TYPE_CHOICES = [
        ('casual', 'Casual Leave'),
        ('sick', 'Sick Leave'),
        ('restricted', 'Restricted Holiday'),
        ('LOP', 'Loss of Pay'),
    ]
    leave_type = models.CharField(max_length=128, choices=LEAVE_TYPE_CHOICES)
    date = models.DateField(null=True, blank=True)
    LEAVE_GENRE_CHOICES = [
        ('full_day', 'Full Day'),
        ('first_half', 'First Half'),
        ('second_half', 'Second Half'),
    ]
    leave_genre = models.CharField(max_length=128, choices=LEAVE_GENRE_CHOICES)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default='pending')  
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} on {self.date} ({self.status})"
