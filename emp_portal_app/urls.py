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
    path('employees/delete/<int:pk>/', employee_delete, name='employee_delete'),

    path('login/', login, name='login'),
    path('home/',home,name='home'),
]


    
