// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["NSSA Report"] = {
	"filters": [
		{
			fieldname: "currency",
			label: __("Currency"),
			fieldtype: "Link",
			options: "currency",
			reqd: 1,
		},
		{
			fieldname: "payroll_frequency",
			fieldtype: "Date",
			label: __("Payroll Frequency"),
		},
		{
			fieldname: "employee",
			fieldtype: "Link",
			label: __("Employee"),
			options: "Employee",
		},
	]
};
