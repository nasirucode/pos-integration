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
        {"label": "Commencement Date", "fieldname": "commencement_date", "fieldtype": "Date", "width": 150},
        {"label": "First Names", "fieldname": "first_names", "fieldtype": "Data", "width": 200},
        {"label": "Surname", "fieldname": "surname", "fieldtype": "Data", "width": 150},
        {"label": "SSN", "fieldname": "ssn", "fieldtype": "Data", "width": 150},
        {"label": "Employee Staff No", "fieldname": "staff_no", "fieldtype": "Data", "width": 150},
        {"label": "National ID No", "fieldname": "national_id", "fieldtype": "Data", "width": 150},
        {"label": "Date of Cessation", "fieldname": "cessation_date", "fieldtype": "Date", "width": 150},
        {"label": "Reason for Cessation", "fieldname": "reason_for_cessation", "fieldtype": "Data", "width": 150},
        {"label": "Nature of Employment", "fieldname": "nature_of_employment", "fieldtype": "Data", "width": 150},
        {"label": "NPS Insurable Earnings (ZIG)", "fieldname": "nps_insurable_earnings_zig", "fieldtype": "Currency", "width": 180},
        {"label": "Total NPS (9%) Contribution", "fieldname": "total_nps_contribution", "fieldtype": "Currency", "width": 180},
        {"label": "Basic Salary (WCIF)", "fieldname": "basic_salary_wcif", "fieldtype": "Currency", "width": 180},
        {"label": "Currency", "fieldname": "currency", "fieldtype": "Data", "width": 100}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("payroll_period"):
        conditions += f" AND CONCAT(ss.start_date, ' to ', ss.end_date) = '{filters.get('payroll_period')}'"
    if filters.get("currency"):
        conditions += f" AND ss.currency = '{filters.get('currency')}'"
    
    query = f"""
        SELECT
            ss.start_date AS commencement_date,
            emp.first_name AS first_names,
            emp.last_name AS surname,
            emp.ssn,
            emp.employee_id AS staff_no,
            emp.national_id,
            ss.end_date AS cessation_date,
            ss.reason_for_cessation,
            ss.nature_of_employment,
            ss.gross_pay AS nps_insurable_earnings_zig,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NPS Contribution') AS total_nps_contribution,
            (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='WCIF Basic Salary') AS basic_salary_wcif,
            ss.currency
        FROM `tabSalary Slip` ss
        JOIN `tabEmployee` emp ON ss.employee = emp.name
        WHERE ss.docstatus = 1 {conditions}
    """
    
    return frappe.db.sql(query, as_dict=True)


