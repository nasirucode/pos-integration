// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["ZIMRA ITF16"] = {
	"filters": [
		{
			fieldname: "currency",
			label: __("Currency"),
			fieldtype: "Link",
			options: "Currency",
		},
		{
			fieldname: "payroll_period",
			fieldtype: "Date",
			label: __("Payroll Period"),
		},
		{
			fieldname: "employee",
			fieldtype: "Link",
			label: __("Employee"),
			options: "Employee",
		},
	]
};
