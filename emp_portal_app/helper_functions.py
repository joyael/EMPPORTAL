from datetime import datetime, timedelta, date
from datetime import timezone as datetime_timezone

from django.utils.timezone import localtime, make_aware, get_default_timezone
from django.utils import timezone
from datetime import timedelta
from .models import Attendance, CheckInOut

from emp_portal_app.models import CASUAL_LEAVE_QUARTERLY_COUNT, RH_YEARLY_COUNT, SHIFT_HOURS_IN_A_DAY, SICK_LEAVE_QUARTERLY_COUNT, LeaveRequest
from django.db.models import Q

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
        
        leave_days = 0
        leaves = LeaveRequest.objects.filter(
            employee=employee,
            date__range=(from_date_input, to_date_input),
        )
        total_leave_days = 0
        for leave in leaves:
            total_leave_days += get_leave_value(leave.leave_genre)  # Add full day or half-day values
        leave_days=total_leave_days

        total_h = bench_h + training_h + learning_h + project_h + (leave_days*SHIFT_HOURS_IN_A_DAY)
        total_m = bench_m + training_m + learning_m + project_m
        total_s = bench_s + training_s + learning_s + project_s

        emp_name = employee.name()
        reporting_manager = employee.reporting_manager.name() if employee.reporting_manager else "Admin"
        project_hours = total_hours_decimal(project_h,project_m,project_s)
        bench_hours = total_hours_decimal(bench_h,bench_m,bench_s)
        
        

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
    user_time_entries = [item for item in time_entries if item.employee.employee_id == user.employee_id]
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
            employee=employee, leave_type='restricted', date__year=current_year,
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
    return 0  #Default case

def get_remaining_leave_data(employee):
    current_date = date.today()
    casual={
        "total": 0,
        "used": 0,
        "available": 0
    }
    sick={
        "total": 0,
        "used": 0,
        "available": 0
    }
    restricted={
        "total": 0,
        "used": 0,
        "available": 0
    }
    casual["total"] = CASUAL_LEAVE_QUARTERLY_COUNT * get_count(get_quarter(current_date)["quarter"])
    sick["total"] = SICK_LEAVE_QUARTERLY_COUNT  * get_count(get_quarter(current_date)["quarter"])
    restricted["total"] = RH_YEARLY_COUNT
    quarter_data = get_quarter(current_date)
    for quarter in get_quarters_till_now(quarter_data["quarter"]):
        data = get_quarter_data(current_date.year)
        casual_used_for_this_quarter = get_used_leave_days(employee, "casual", data[quarter]["quarter_start"], data[quarter]["quarter_end"])
        print("Quarter start date : ",data[quarter]["quarter_start"])
        print("Quarter start date : ",data[quarter]["quarter_end"])
        casual["used"]+=casual_used_for_this_quarter
        sick_used_for_this_quarter = get_used_leave_days(employee, "sick", data[quarter]["quarter_start"], data[quarter]["quarter_end"])
        sick["used"]+=sick_used_for_this_quarter
    
    year = current_date.year
    rh_leaves = LeaveRequest.objects.filter(
        employee=employee,
        leave_type="restricted",
        date__range=(datetime(year, 1, 1), datetime(year, 12, 31)),
    )
    rh_used_days = 0
    for leave in rh_leaves:
        rh_used_days += get_leave_value(leave.leave_genre)
    restricted["used"] = rh_used_days

    casual["available"] = casual["total"] - casual["used"]
    sick["available"] = sick["total"] - sick["used"]
    restricted["available"] = restricted["total"] - restricted["used"]

    return {
        "casual":casual,
        "sick":sick,
        "restricted":restricted,
    }

def get_quarter_data(year):
    quarter_data = {
        "first":{
        "quarter": "first",
        "quarter_start":datetime(year, 1, 1),
        "quarter_end":datetime(year, 3, 31),
        },
        "second":{
        "quarter": "second",
        "quarter_start":datetime(year, 4, 1),
        "quarter_end":datetime(year, 6, 30),
        },
        "third":{
        "quarter": "third",
        "quarter_start":datetime(year, 7, 1),
        "quarter_end":datetime(year, 9, 30),
        },
        "fourth":{
        "quarter": "fourth",
        "quarter_start":datetime(year, 10, 1),
        "quarter_end":datetime(year, 12, 31),
        }
    }
    return quarter_data
   
def get_quarter(date):
    data = get_quarter_data(date.year)
    month = date.month
    if month in [1, 2, 3]:
        return data["first"]
    elif month in [4, 5, 6]:
        return data["second"]
    elif month in [7, 8, 9]:
        return data["third"]
    else:
        return data["fourth"]

def get_quarters_till_now(quarter):
    if quarter == "first":
        return ["first"]
    elif  quarter == "second":
        return ["first","second"]
    elif  quarter == "third":
        return ["first","second","third"]
    elif  quarter == "fourth":
        return ["first","second","third","fourth"]
    else:
        return ["first"]
    
def get_count(quarter):
    if quarter == "first":
        return 1
    elif  quarter == "second":
        return 2
    elif  quarter == "third":
        return 3
    elif  quarter == "fourth":
        return 4
    else:
        return 1
    

def get_dates():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) 
    current_date = today

    start_of_last_week = start_of_week - timedelta(weeks=1)
    end_of_last_week = start_of_last_week + timedelta(days=6)

    first_date_current_month = today.replace(day=1)  
    current_date_current_month = today

    if today.month == 1:
        first_date_last_month = today.replace(year=today.year - 1, month=12, day=1)
    else:
        first_date_last_month = today.replace(month=today.month - 1, day=1)
    
    last_day_last_month = first_date_last_month.replace(day=28) + timedelta(days=4) 
    last_day_last_month = last_day_last_month - timedelta(days=last_day_last_month.day)

    return {
        "current_week": {
            "first_date": start_of_week,
            "current_date": current_date,
        },
        "last_week": {
            "first_date": start_of_last_week,
            "last_date": end_of_last_week,
        },
        "current_month": {
            "first_date": first_date_current_month,
            "current_date": current_date_current_month,
        },
        "last_month": {
            "first_date": first_date_last_month,
            "last_date": last_day_last_month,
        },
    }


def check_overlap(start1, end1, start2, end2):
    """
    Check if the first date range (start1, end1) overlaps with the second date range (start2, end2).

    :param start1: Start date of the first range (datetime object)
    :param end1: End date of the first range (datetime object)
    :param start2: Start date of the second range (datetime object)
    :param end2: End date of the second range (datetime object)
    :return: True if the date ranges overlap, False otherwise
    """
    return start1 <= end2 and start2 <= end1







def is_user_checked_in(employee):
    today = localtime().date()  # Get today's date in IST
    start_of_day = make_aware(datetime(today.year, today.month, today.day, 0, 0, 0))  # Start of today
    end_of_day = make_aware(datetime(today.year, today.month, today.day, 23, 59, 59))  # End of today

    today_check_ins = CheckInOut.objects.filter(
        employee=employee,
        timestamp__gte=start_of_day,  # Greater than or equal to start of today
        timestamp__lte=end_of_day,  # Less than or equal to end of today
    )

    if not today_check_ins.exists():
        return False  # No check-ins today → Not checked in

    last_check_in = today_check_ins.latest('timestamp')
    return last_check_in.is_check_in  # Return True if last action was a check-in


def calculate_attendance(employee, date):
    shift = employee.shift
    shift_start_time = shift.start_time  
    shift_end_time = shift.end_time  
    total_shift_hours = shift.total_hours

    today = date  
    # Create naive datetime objects for 12:00 AM and 11:59 PM in IST
    start_of_day_ist = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_of_day_ist = datetime(today.year, today.month, today.day, 23, 59, 59)

    # Make these datetimes timezone-aware in the current Django timezone (IST)
    start_of_day_aware = timezone.make_aware(start_of_day_ist)
    end_of_day_aware = timezone.make_aware(end_of_day_ist)

    # Convert them to UTC
    start_of_day_utc = start_of_day_aware.astimezone(datetime_timezone.utc)
    end_of_day_utc = end_of_day_aware.astimezone(datetime_timezone.utc)

    print(start_of_day_utc)
    print(end_of_day_utc)

    check_ins_outs = CheckInOut.objects.filter(
        employee=employee,
        timestamp__gte=start_of_day_utc,  # Greater than or equal to start of today
        timestamp__lte=end_of_day_utc,  # Less than or equal to end of today
    )

    if not check_ins_outs.exists():
        print("No check in checkouts found")
        attendance_found = Attendance.objects.filter(employee=employee, date=date).exists()
        print("Employee ID : ", employee.employee_id)
        print("Date : ", date)
        print("Attendance_already_there : ", attendance_found)
        if not attendance_found:
            attendance = Attendance.objects.create(
                employee=employee,
                date=date,
            )
            return attendance
    print("Checkincheckouts were found")
    first_check_in_utc = check_ins_outs.first().timestamp
    last_check_out_utc = check_ins_outs.last().timestamp
    # Convert timestamps to IST
    first_check_in_ist = localtime(check_ins_outs.first().timestamp)  
    last_check_out_ist = localtime(check_ins_outs.last().timestamp) 

    print("First_check_in_of_the_day : ", first_check_in_ist)
    print("Last_check_in_of_the_day : ", last_check_out_ist)


    # Attendance rules in IST

    # Assuming shift_start_time is a time object and date is a date object
    shift_start_datetime = datetime.combine(date, shift_start_time)  
    shift_start_datetime_aware = make_aware(shift_start_datetime, timezone=get_default_timezone())
    shift_start_datetime_ist = localtime(shift_start_datetime_aware)

    shift_end_datetime = datetime.combine(date, shift_end_time)
    shift_end_datetime_aware = make_aware(shift_end_datetime, timezone=get_default_timezone())
    shift_end_datetime_ist = localtime(shift_end_datetime_aware)


    # Total worked hours calculation
    total_worked_time = timedelta()
    last_check_in_time = None

    for entry in check_ins_outs:
        entry_time_ist = localtime(entry.timestamp)  # Convert each entry timestamp to IST
        if entry.is_check_in:
            last_check_in_time = entry_time_ist
        else:
            if last_check_in_time:
                total_worked_time += (entry_time_ist - last_check_in_time)
                last_check_in_time = None

    total_worked_hours = total_worked_time.total_seconds() / 3600  # Convert to hours
    total_worked_seconds = total_worked_time.total_seconds()
    total_worked_seconds = int(total_worked_seconds)

    if first_check_in_ist > shift_start_datetime_ist + timedelta(minutes=30):
        first_half_absent = True
    else:
        first_half_absent = False

    # Mark attendance status
    is_full_day = total_worked_hours >= total_shift_hours
    if total_worked_hours > 13:
        second_half_absent = True  # Mark second half as absent
    elif  is_full_day:
        second_half_absent = False
    elif not  is_full_day:
        if total_worked_hours >= (total_shift_hours/2):
            if first_half_absent:
                second_half_absent = False
            else:
                second_half_absent = True
        else:
            first_half_absent = True
            second_half_absent = True
    
    if not check_ins_outs.last().is_check_in:
        if last_check_out_ist < shift_end_datetime_ist:
            second_half_absent = True
    
    if not first_half_absent and second_half_absent:
        attendance_status = "first_half_present"
    elif first_half_absent and not second_half_absent:
        attendance_status = "second_half_present"
    elif first_half_absent and second_half_absent:
        attendance_status = "absent"
    else:
        attendance_status = "present"


    # Update attendance record
    attendance_found = Attendance.objects.filter(employee=employee, date=date).exists()
    if attendance_found:
        filtered_objects = Attendance.objects.filter(employee=employee, date=date)
        attendance = filtered_objects.first()
        attendance.first_check_in = first_check_in_utc
        attendance.last_check_out = last_check_out_utc
        attendance.total_worked_seconds = total_worked_seconds
        attendance.attendance_status = attendance_status
        attendance.save()
    else:
        attendance = Attendance.objects.create(
            employee=employee,
            date=date,
            defaults={
                "first_check_in": first_check_in_utc,
                "last_check_out": last_check_out_utc,
                "total_worked_seconds": total_worked_seconds,
                "attendance_status": attendance_status,
            }
        )
    return attendance