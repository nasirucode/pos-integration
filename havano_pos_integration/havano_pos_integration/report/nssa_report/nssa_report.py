# Copyright (c) 2025, Alphazen Technologies and contributors
# For license information, please see license.txt

# import frappe


#def execute(filters=None):
#	columns, data = [], []
#	return columns, data
import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "First Name", "fieldname": "first_name", "fieldtype": "Data", "width": 150},
        {"label": "Surname", "fieldname": "surname", "fieldtype": "Data", "width": 150},
        {"label": "NSSA (ZIG) Employee", "fieldname": "nssa_zig_employee", "fieldtype": "Currency", "width": 150},
        {"label": "NSSA (ZIG) Employer", "fieldname": "nssa_zig_employer", "fieldtype": "Currency", "width": 150},
        {"label": "NSSA (USD) Employee", "fieldname": "nssa_usd_employee", "fieldtype": "Currency", "width": 150},
        {"label": "NSSA (USD) Employer", "fieldname": "nssa_usd_employer", "fieldtype": "Currency", "width": 150},
        {"label": "Payroll Period", "fieldname": "payroll_period", "fieldtype": "Data", "width": 180}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("employee"):
        conditions += f" AND ss.employee = '{filters.get('employee')}'"
    if filters.get("currency"):
        conditions += f" AND ss.currency = '{filters.get('currency')}'"
    if filters.get("payroll_frequency"):
        conditions += f" AND ss.payroll_frequency = '{filters.get('payroll_frequency')}'"
    
    query = f"""
        SELECT
            emp.first_name, emp.last_name AS surname,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA' AND parentfield='deductions' AND ss.currency='ZWL') AS nssa_zig_employee,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA' AND parentfield='employer_contributions' AND ss.currency='ZWL') AS nssa_zig_employer,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA' AND parentfield='deductions' AND ss.currency='USD') AS nssa_usd_employee,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA' AND parentfield='employer_contributions' AND ss.currency='USD') AS nssa_usd_employer,
            CONCAT(ss.start_date, ' to ', ss.end_date) AS payroll_period
        FROM `tabSalary Slip` ss
        JOIN `tabEmployee` emp ON ss.employee = emp.name
        WHERE ss.docstatus = 1 {conditions}
    """
    
    return frappe.db.sql(query, as_dict=True)
