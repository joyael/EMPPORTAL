# departments
# create department - admin - level=1
# update department - admin - level=1
# delete department - admin - level=1
# view departments - employee - level=3

# employees
# insert-employee               - admin - level=1
# update-employee-any           - admin - level=1
# update-employee-self          - employee - level=3
# view-employees-limited-detail - employee - level=3
# view-employees-with-detail    - admin - level=1

# projects
# create-project - admin - level=1
# update-project - admin - level=1
# delete-project - admin - level=1
# view-projects - manager - level=2

# project-assignations
# create-project-assignation - mangager - level=2
# update-project-assignation-any - admin - level=1
# update-project-assignation-self - manager - level=2
# view-project-assignations-any - admin - level=1
# view-project-assignations-self - employee - level=3


from datetime import datetime, timedelta
from django.utils.timezone import now

from emp_portal_app.models import CASUAL_LEAVE_QUARTERLY_COUNT, RH_YEARLY_COUNT, SHIFT_HOURS_IN_A_DAY, SICK_LEAVE_QUARTERLY_COUNT, LeaveRequest


operations = {
    "1": {
        "Departments": {
            "Create Department": "department_create",
            "View Departments": "department_list"
        },
        "Employees": {
            "Insert Employee": "employee_create",
            "View Employees with detail": "employee_list",
        },
        "Projects": {
            "CreateProject": "project_create",
            "View Projects": "project_list"
        },
        "Project Assignations": {
            "Create Project Assignation": "project_assignation_create",
            "View Project Assignations any": "project_assignation_list",
        }
    },
    "2": {
        "Departments": {
            "View Departments": "department_list"
        },
        "Employees": {
            "View Employees": "employee_list",
            "Employees under me":"employees_under_manager",
        },
        "Projects": {
            "View Projects": ""
        },
        "Project Assignations": {
            "Create Project Assignation": "project_assignation_create",
            "View My Project Assignations": "project_assignation_list"
        },
        "Timesheet": {
            "Submit Time Entry": "submit_time_entry",
            "Timesheet Overview": "timesheet_overview",
            "Timesheet Breakdown": "timesheet_breakdown",
        },
        "Leave":{
            "Apply Leave": "apply_leave",
            "Leave Applications" : "leave_applications",
        }
    },
    "3": {
        "Departments": {
            "View Departments": "department_list"
        },
        "Employees": {
            "View Employees": "employee_list",
        },
        "Project Assignations": {
            "View Project Assignations to me": "project_assignation_list"
        },
        "Timesheet": {
            "Submit Time Entry": "submit_time_entry",
            "Timesheet Overview": "timesheet_overview",
            "Timesheet Breakdown": "timesheet_breakdown",
        },
        "Leave":{
            "Apply Leave": "apply_leave",
            "Leave Applications" : "leave_applications",
        }
    }
}




def total_hours_decimal(hours, minutes, seconds):
    total_hours = hours + (minutes / 60) + (seconds / 3600)
    return round(total_hours, 2)  # 2 decimal places

def calculate_business_days(from_date, to_date, exclude_saturdays=False):
    current_date = from_date
    business_days_count = 0
    while current_date <= to_date:
        if current_date.weekday() == 6:  # Sunday
            current_date += timedelta(days=1)
            continue
        if exclude_saturdays and current_date.weekday() == 5:  # Saturday
            current_date += timedelta(days=1)
            continue
        if not exclude_saturdays and current_date.weekday() == 5:  # Saturday
            if (current_date.day - 1) // 7 == 1:  # Second Saturday
                current_date += timedelta(days=1)
                continue
        
        if current_date <= to_date:
            business_days_count += 1
        
        current_date += timedelta(days=1)
    return business_days_count

def timesheeet_overview_data_extract(user,from_date_input,to_date_input,employees,time_entries):
    the_timesheet_overview_data = []
    if user.position == '1':
        business_days = calculate_business_days(from_date_input, to_date_input, exclude_saturdays=False)
    else:
        business_days = calculate_business_days(from_date_input, to_date_input, exclude_saturdays=True)
    minimum_working_hours = business_days * SHIFT_HOURS_IN_A_DAY
    print("Number of employees before function : ",len(employees))

    for employee in employees:
        emp_time_entries = time_entries.filter(employee=employee)
        each_employee_data = dict()
        bench_h = 0
        bench_m = 0
        bench_s = 0
        training_h = 0
        training_m = 0
        training_s = 0
        learning_h = 0
        learning_m = 0
        learning_s = 0
        project_h = 0
        project_m = 0
        project_s = 0
        leave_days = 0
        for time_entry in emp_time_entries :
            if time_entry.project == 'bench':
                bench_h = bench_h + time_entry.hours
                bench_m = bench_m + time_entry.minutes
                bench_s = bench_s + time_entry.seconds
            elif time_entry.project == 'training':
                training_h = training_h + time_entry.hours
                training_m = training_m + time_entry.minutes
                training_s = training_s + time_entry.seconds
            elif time_entry.project == 'learning':
                learning_h = learning_h + time_entry.hours
                learning_m = learning_m + time_entry.minutes
                learning_s = learning_s + time_entry.seconds
            else:
                project_h = project_h + time_entry.hours
                project_m = project_m + time_entry.minutes
                project_s = project_s + time_entry.seconds
        
        
        total_h = bench_h + training_h + learning_h + project_h + (leave_days*SHIFT_HOURS_IN_A_DAY)
        total_m = bench_m + training_m + learning_m + project_m
        total_s = bench_s + training_s + learning_s + project_s

        emp_name = employee.name()
        reporting_manager = employee.reporting_manager.name()
        project_hours = total_hours_decimal(project_h,project_m,project_s)
        bench_hours = total_hours_decimal(bench_h,bench_m,bench_s)
        leave_days = 0
        training_hours = total_hours_decimal(training_h,training_m,training_s)
        learning_hours = total_hours_decimal(learning_h,learning_m,learning_s)
        total_hours = total_hours_decimal(total_h,total_m,total_s)

        if employee.position == '1':
            business_days = calculate_business_days(from_date_input, to_date_input, exclude_saturdays=False)
        else:
            business_days = calculate_business_days(from_date_input, to_date_input, exclude_saturdays=True)
        minimum_working_hours_of_emp = business_days*SHIFT_HOURS_IN_A_DAY
        deviation = total_hours - minimum_working_hours_of_emp
        if deviation < 0:
            has_deviation = True
        else:
            has_deviation = False

        each_employee_data["emp_name"] = emp_name
        each_employee_data["reporting_manager"] = reporting_manager
        each_employee_data["project_hours"] = project_hours
        each_employee_data["bench_hours"] = bench_hours
        each_employee_data["leave_days"] = leave_days
        each_employee_data["training_hours"] = training_hours
        each_employee_data["learning_hours"] = learning_hours
        each_employee_data["total_hours"] = total_hours
        each_employee_data["deviation"] = deviation
        each_employee_data["has_deviation"] = has_deviation

        the_timesheet_overview_data.append(each_employee_data)
    
    output = {
        "the_timesheet_overview_data": the_timesheet_overview_data,
        "minimum_working_hours" : minimum_working_hours,
    }
    
    return output


def get_the_overview_total_data(the_timesheet_overview_data):
    overview_total_data = {
        'total_project_hours': 0,
        'total_bench_hours': 0,
        'total_leave_days': 0,
        'total_training_hours': 0,
        'total_learning_hours': 0,
        'total_total_hours': 0,
        'total_deviation': 0,
        'total_has_deviation': False  
    }
    
    for each_employee_data in the_timesheet_overview_data:
        overview_total_data['total_project_hours'] += each_employee_data.get("project_hours", 0)
        overview_total_data['total_bench_hours'] += each_employee_data.get("bench_hours", 0)
        overview_total_data['total_leave_days'] += each_employee_data.get("leave_days", 0)
        overview_total_data['total_training_hours'] += each_employee_data.get("training_hours", 0)
        overview_total_data['total_learning_hours'] += each_employee_data.get("learning_hours", 0)
        overview_total_data['total_total_hours'] += each_employee_data.get("total_hours", 0)
        overview_total_data['total_deviation'] += each_employee_data.get("deviation", 0)
    
    overview_total_data['total_has_deviation'] = overview_total_data['total_deviation'] < 0
    
    return overview_total_data


def get_the_break_down_total_data(time_entries,user,from_date_input,to_date_input):
    total_h = 0
    total_m = 0
    total_s = 0
    u_total_h = 0
    u_total_m = 0
    u_total_s = 0
    for time_entry in time_entries :
        total_h+=time_entry.hours
        total_m+=time_entry.minutes
        total_s+=time_entry.seconds
    user_time_entries = time_entries
    for time_entry in user_time_entries :
        u_total_h+=time_entry.hours
        u_total_m+=time_entry.minutes
        u_total_s+=time_entry.seconds
    total_timesheet_time = total_hours_decimal(total_h,total_m,total_s)
    total_time_logged_you = total_hours_decimal(u_total_h,u_total_m,u_total_s)
    if user.position == '1':
        business_days = calculate_business_days(from_date_input, to_date_input, exclude_saturdays=False)
    else:
        business_days = calculate_business_days(from_date_input, to_date_input, exclude_saturdays=True)
    total_time_available_you = business_days * SHIFT_HOURS_IN_A_DAY
    deviation_you = total_time_logged_you - total_time_available_you
    total_timesheet_time = format(total_timesheet_time, ".2f")
    total_time_available_you = format(total_time_available_you, ".2f")
    total_time_logged_you = format(total_time_logged_you, ".2f")
    

    output = {
        "total_timesheet_time":total_timesheet_time,
        "total_time_available_you":total_time_available_you,
        "total_time_logged_you":total_time_logged_you,
        "deviation_you":deviation_you,
    }
    return output



def check_leave_conflicts(employee, date, leave_genre):
    """
    Check if there is already a leave applied that conflicts with the new leave.
    """
    existing_leaves = LeaveRequest.objects.filter(employee=employee, date=date, status__in=['pending', 'approved'])

    if leave_genre == 'full_day' and existing_leaves.exists():
        return True  # Full day cannot overlap with any leave

    if leave_genre == 'first_half' and existing_leaves.filter(Q(leave_genre='full_day') | Q(leave_genre='first_half')).exists():
        return True  # First half conflicts with full day or another first half

    if leave_genre == 'second_half' and existing_leaves.filter(Q(leave_genre='full_day') | Q(leave_genre='second_half')).exists():
        return True  # Second half conflicts with full day or another second half

    return False  # No conflicts found

def check_leave_balance(employee, leave_type, leave_date, leave_genre):
    """
    Check if the employee has enough leave balance for the selected leave type.
    """
    current_year = leave_date.year
    quarter_start, quarter_end = get_quarter_range(leave_date)

    if leave_type == 'restricted':
        # Get total restricted holidays used this year
        used_days = LeaveRequest.objects.filter(
            employee=employee, leave_type='restricted', date__year=current_year, status='approved'
        ).count()

        return used_days < RH_YEARLY_COUNT  # Ensure they haven't exceeded RH limit

    elif leave_type == 'casual':
        # Get total casual leaves used in the current quarter
        used_days = get_used_leave_days(employee, 'casual', quarter_start, quarter_end)
        return (used_days + get_leave_value(leave_genre)) <= CASUAL_LEAVE_QUARTERLY_COUNT

    elif leave_type == 'sick':
        # Get total sick leaves used in the current quarter
        used_days = get_used_leave_days(employee, 'sick', quarter_start, quarter_end)
        return (used_days + get_leave_value(leave_genre)) <= SICK_LEAVE_QUARTERLY_COUNT

    return True  # No validation required for other leave types


def get_quarter_range(date):
    """
    Returns the start and end dates of the quarter for a given date.
    """
    month = date.month
    year = date.year

    if month in [1, 2, 3]:
        return (datetime(year, 1, 1), datetime(year, 3, 31))
    elif month in [4, 5, 6]:
        return (datetime(year, 4, 1), datetime(year, 6, 30))
    elif month in [7, 8, 9]:
        return (datetime(year, 7, 1), datetime(year, 9, 30))
    else:
        return (datetime(year, 10, 1), datetime(year, 12, 31))


def get_used_leave_days(employee, leave_type, start_date, end_date):
    """
    Calculate the total leave days used for a given leave type in a time range.
    """
    leaves = LeaveRequest.objects.filter(
        employee=employee,
        leave_type=leave_type,
        date__range=(start_date, end_date),
        status='approved'
    )

    total_days = 0
    for leave in leaves:
        total_days += get_leave_value(leave.leave_genre)  # Add full day or half-day values

    return total_days

def get_leave_value(leave_genre):
    """
    Returns the numerical value of leave based on genre.
    """
    if leave_genre == 'full_day':
        return 1
    elif leave_genre in ['first_half', 'second_half']:
        return 0.5
    return 0  # Default case
