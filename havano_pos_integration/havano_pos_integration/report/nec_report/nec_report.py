# Copyright (c) 2025, Alphazen Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Surname", "fieldname": "surname", "fieldtype": "Data", "width": 150},
        {"label": "First Names", "fieldname": "first_names", "fieldtype": "Data", "width": 200},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 150},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 150},
        {"label": "Grade", "fieldname": "grade", "fieldtype": "Data", "width": 150},
        {"label": "NEC Earnings ({filters.get('currency', 'Currency')})", "fieldname": "nec_earnings", "fieldtype": "Currency", "width": 150},
        {"label": "Employee Contribution ({filters.get('currency', 'Currency')})", "fieldname": "employee_contribution", "fieldtype": "Currency", "width": 150},
        {"label": "Employer Contribution ({filters.get('currency', 'Currency')})", "fieldname": "employer_contribution", "fieldtype": "Currency", "width": 150},
        {"label": "Total NEC ({filters.get('currency', 'Currency')})", "fieldname": "total_nec", "fieldtype": "Currency", "width": 150}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("currency"):
        conditions += f" AND ss.currency = '{filters.get('currency')}'"
    if filters.get("payroll_period"):
        conditions += f" AND CONCAT(ss.start_date, ' to ', ss.end_date) = '{filters.get('payroll_period')}'"
    
    query = f"""
        SELECT
            emp.last_name AS surname,
            emp.first_name AS first_names,
            ss.start_date,
            ss.end_date,
            emp.grade,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NEC Earnings') AS nec_earnings,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NEC Employee Contribution') AS employee_contribution,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NEC Employer Contribution') AS employer_contribution,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NEC Total') AS total_nec
        FROM `tabSalary Slip` ss
        JOIN `tabEmployee` emp ON ss.employee = emp.name
        WHERE ss.docstatus = 1 {conditions}
    """
    
    return frappe.db.sql(query, as_dict=True)

