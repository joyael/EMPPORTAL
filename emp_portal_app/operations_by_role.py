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
        },
        "Timesheet": {
            "Submit Time Entry": "submit_time_entry",
            "Timesheet Overview": "timesheet_overview",
            "Timesheet Breakdown": "timesheet_breakdown",
        },
        "Leave":{
            "Apply Leave": "apply_leave",
            "Leave Applications" : "leave_applications",
        },
        "Attendance":{
            "Tabular View": "attendance_tabular_view",
            "Audit History":"attendance_audit_history",
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
            "View Projects": "project_list",
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
        },
        "Attendance":{
            "Tabular View": "attendance_tabular_view",
            "Audit History":"attendance_audit_history",
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
        },
        "Attendance":{
            "Tabular View": "attendance_tabular_view",
            "Audit History":"attendance_audit_history",
        }
    }
}