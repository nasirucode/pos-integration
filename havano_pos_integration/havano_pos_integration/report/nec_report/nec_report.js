// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["NEC Report"] = {
	"filters": [
		{
			fieldname: "currency",
			label: __("Currency"),
			fieldtype: "Link",
			options: "Currency",
			default: "USD",
		},
		{
            "fieldname": "payroll_period",
            "label": __("Payroll Period"),
            "fieldtype": "DateRange",
            "reqd": 0
        },
	],
	"onload": function(report) {
        // Add a custom button to render the report
        report.page.add_inner_button(__("Print Nec Form"), function() {
            // Get the latest data from the report
            const latestData = report.get_values();
            
            // Run the report again to get fresh data
            frappe.query_report.refresh()
                .then(() => {
                    // After refresh, render the report with the latest data
                    renderNecForm(report);
                });
        });
    }
};
