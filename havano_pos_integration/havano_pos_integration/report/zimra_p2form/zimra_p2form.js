// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["ZIMRA P2FORM"] = {
	"filters": [
		{
			fieldname: "currency",
			label: __("Currency"),
			fieldtype: "Link",
			options: "Currency",
		},
		{
			fieldname: "payroll_frequency",
			fieldtype: "Date",
			label: __("Payroll Frequency"),
		}
	]
};
