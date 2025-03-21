# Copyright (c) 2025, Alphazen Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, formatdate, format_date
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    
    # Pre-calculate totals
    currency = filters.get("currency", "USD")
    total_earnings = 0
    total_contributions = 0
    total_arrears = 0
    total_prepayments = 0
    total_surcharge = 0
    total_payment = 0
    
    for item in data:
        if currency == "USD":
            total_earnings += flt(item.get("total_insurable_earnings_usd") or 0)
            total_contributions += flt(item.get("current_contributions_usd") or 0)
            total_arrears += flt(item.get("arrears_usd") or 0)
            total_prepayments += flt(item.get("prepayments_usd") or 0)
            total_surcharge += flt(item.get("surcharge_usd") or 0)
            total_payment += flt(item.get("total_payment_usd") or 0)
        else:
            total_earnings += flt(item.get("total_insurable_earnings_zwl") or 0)
            total_contributions += flt(item.get("current_contributions_zwl") or 0)
            total_arrears += flt(item.get("arrears_zwl") or 0)
            total_prepayments += flt(item.get("prepayments_zwl") or 0)
            total_surcharge += flt(item.get("surcharge_zwl") or 0)
            total_payment += flt(item.get("total_payment_zwl") or 0)
    
    wcif_contribution = round(total_earnings * 0.0125, 2)
    grand_total = total_payment + wcif_contribution
    
    # Create data_to_be_printed dictionary
    data_to_be_printed = {
        "employee_count": len(data),
        "total_earnings": total_earnings,
        "total_contributions": total_contributions,
        "total_arrears": total_arrears,
        "total_prepayments": total_prepayments,
        "total_surcharge": total_surcharge,
        "total_payment": total_payment,
        "wcif_contribution": wcif_contribution,
        "grand_total": grand_total,
        "company": frappe.defaults.get_user_default("Company"),
        "user": frappe.session.user_fullname,
        "today": frappe.utils.today()
    }
    
    return columns, data, None, None, data_to_be_printed

def get_columns(filters):
    # Your existing get_columns code remains the same
    currency_label = filters.get("currency", "Currency")
    
    columns = [
        {"label": "Surname", "fieldname": "surname", "fieldtype": "Data", "width": 150},
        {"label": "First Names", "fieldname": "first_names", "fieldtype": "Data", "width": 200},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 150},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 150},
    ]
    
    if currency_label == "USD":
        columns.extend([
            {"label": "Total Insurable Earnings (USD)", "fieldname": "total_insurable_earnings_usd", "fieldtype": "Currency", "width": 180},
            {"label": "Current Contributions (USD)", "fieldname": "current_contributions_usd", "fieldtype": "Currency", "width": 180},
            {"label": "Arrears (USD)", "fieldname": "arrears_usd", "fieldtype": "Currency", "width": 150},
            {"label": "Prepayments (USD)", "fieldname": "prepayments_usd", "fieldtype": "Currency", "width": 150},
            {"label": "Surcharge (USD)", "fieldname": "surcharge_usd", "fieldtype": "Currency", "width": 150},
            {"label": "Total Payment (USD)", "fieldname": "total_payment_usd", "fieldtype": "Currency", "width": 180}
        ])
    elif currency_label == "ZWL":
        columns.extend([
            {"label": "Total Insurable Earnings (ZWL)", "fieldname": "total_insurable_earnings_zwl", "fieldtype": "Currency", "width": 180},
            {"label": "Current Contributions (ZWL)", "fieldname": "current_contributions_zwl", "fieldtype": "Currency", "width": 180},
            {"label": "Arrears (ZWL)", "fieldname": "arrears_zwl", "fieldtype": "Currency", "width": 150},
            {"label": "Prepayments (ZWL)", "fieldname": "prepayments_zwl", "fieldtype": "Currency", "width": 150},
            {"label": "Surcharge (ZWL)", "fieldname": "surcharge_zwl", "fieldtype": "Currency", "width": 150},
            {"label": "Total Payment (ZWL)", "fieldname": "total_payment_zwl", "fieldtype": "Currency", "width": 180}
        ])
    
    return columns
    
def get_data(filters):
    # Your existing get_data code remains the same
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
            CASE WHEN ss.currency = 'USD' THEN ss.gross_pay END AS total_insurable_earnings_usd,
            CASE WHEN ss.currency = 'USD' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Contribution') END AS current_contributions_usd,
            CASE WHEN ss.currency = 'USD' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Arrears') END AS arrears_usd,
            CASE WHEN ss.currency = 'USD' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Prepayments') END AS prepayments_usd,
            CASE WHEN ss.currency = 'USD' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Surcharge') END AS surcharge_usd,
            CASE WHEN ss.currency = 'USD' THEN (
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Contribution'), 0) +
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Arrears'), 0) +
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Prepayments'), 0) +
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Surcharge'), 0)
            ) END AS total_payment_usd,
            CASE WHEN ss.currency = 'ZWL' THEN ss.gross_pay END AS total_insurable_earnings_zwl,
            CASE WHEN ss.currency = 'ZWL' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Contribution') END AS current_contributions_zwl,
            CASE WHEN ss.currency = 'ZWL' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Arrears') END AS arrears_zwl,
            CASE WHEN ss.currency = 'ZWL' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Prepayments') END AS prepayments_zwl,
            CASE WHEN ss.currency = 'ZWL' THEN (SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Surcharge') END AS surcharge_zwl,
            CASE WHEN ss.currency = 'ZWL' THEN (
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Contribution'), 0) +
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Arrears'), 0) +
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Prepayments'), 0) +
                COALESCE((SELECT amount FROM `tabSalary Detail` WHERE parent=ss.name AND salary_component='NSSA Surcharge'), 0)
            ) END AS total_payment_zwl
        FROM `tabSalary Slip` ss
        JOIN `tabEmployee` emp ON ss.employee = emp.name
        WHERE ss.docstatus = 1 {conditions}
    """
    
    return frappe.db.sql(query, as_dict=True)
