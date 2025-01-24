from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

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

    def save(self, *args, **kwargs):
        if not self.password_hash.startswith('pbkdf2_sha256$'):
            self.password_hash = make_password(self.password_hash)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'employees'