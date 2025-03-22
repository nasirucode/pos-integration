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
			fieldtype: "DateRange",
			label: __("Payroll Period"),
		},
		{
			fieldname: "employee",
			fieldtype: "Link",
			label: __("Employee"),
			options: "Employee",
		},
	],
	"onload": function(report) {
        // Add a custom button to render the report
        report.page.add_inner_button(__("Print Zimra ITF16"), function() {
            // Get the latest data from the report
            const latestData = report.get_values();
            
            // Run the report again to get fresh data
            frappe.query_report.refresh()
                .then(() => {
                    // After refresh, render the report with the latest data
                    renderZimraForm(report);
                });
        });
    }
};

function renderZimraForm(report) {
    // Get the report data and filters
    const filters = report.get_values();
    const data = frappe.query_report.data;
    
    if (!data || data.length === 0) {
        frappe.msgprint(__("No data available for the selected filters."));
        return;
    }
	const reportData = data.length > 1 ? data.slice(0, -1) : data;
    
    // Get company information
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Company",
            filters: { is_group: 0, name: frappe.defaults.get_user_default("Company") },
            fieldname: [
                "company_name",
            ]
        },
        callback: function(company_data) {
            if (!company_data.message) {
                frappe.msgprint(__("Company information not found."));
                return;
            }
            
            const company = company_data.message;
            
            // Calculate totals
            let totals = {
                gross_pay: 0,
                basic_pension: 0,
                paye: 0,
                aids_levy: 0
            };
            
            // Process employee data and calculate totals
            const employeeRows = reportData.map(emp => {
                // Update totals
                totals.gross_pay += flt(emp.gross_pay);
                totals.basic_pension += flt(emp.basic_pension);
                totals.paye += flt(emp.paye);
                totals.aids_levy += flt(emp.aids_levy);
                
                // Format dates
                const dob = emp.date_of_birth ? frappe.datetime.str_to_user(emp.date_of_birth) : '';
                const startDate = emp.start_date ? frappe.datetime.str_to_user(emp.start_date) : '';
                const endDate = emp.end_date ? frappe.datetime.str_to_user(emp.end_date) : '';
                
                return `
                    <tr>
                        <td></td>
                        <td>${emp.surname || ''}</td>
                        <td>${emp.first_names || ''}</td>
                        <td>${emp.employee_id || ''}</td>
                        <td>${dob}</td>
                        <td>${startDate}</td>
                        <td>${endDate}</td>
                        <td>${format_currency(emp.gross_pay || 0, emp.currency)}</td>
                        <td>${format_currency(emp.gross_pay || 0, emp.currency)}</td>
                        <td>${format_currency(0, emp.currency)}</td>
                        <td>${format_currency(0, emp.currency)}</td>
                        <td>${format_currency(emp.basic_pension || 0, emp.currency)}</td>
                        <td>${format_currency(0, emp.currency)}</td>
                        <td>${format_currency(0, emp.currency)}</td>
                        <td>${format_currency(0, emp.currency)}</td>
                        <td>${format_currency(0, emp.currency)}</td>
                        <td>${format_currency(emp.paye || 0, emp.currency)}</td>
                        <td>${format_currency(emp.aids_levy || 0, emp.currency)}</td>
                    </tr>
                `;
            }).join('');
            
            // Get the date range for the report title
            const fromDate = filters.payroll_period && filters.payroll_period[0] 
                ? frappe.datetime.str_to_user(filters.payroll_period[0]) 
                : '';
            const toDate = filters.payroll_period && filters.payroll_period[1] 
                ? frappe.datetime.str_to_user(filters.payroll_period[1]) 
                : '';
            
            // Get the year from the end date for ITF16 year
            const itf16Year = toDate ? new Date(filters.payroll_period[1]).getFullYear() : new Date().getFullYear();
            
            // Currency
            const currency = reportData[0].currency || 'USD';
            
            // Create the HTML content
            let html = `<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ITF16 Form - ZIMRA</title>
    <style>
        /* General Styles */
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10px;
            margin: 0;
            padding: 0;
        }

        .page {
            width: 95%;
            /* A4 width */
            min-height: 29.7cm;
            /* A4 height */
            margin: 0px auto;
            padding:0.3cm 1cm;
            position: relative;
        }

        /* ZIMRA Branding */
        .zimra-branding {
            text-align: center;
            margin-bottom: 10px;
        }

        .zimra-logo {
            /* Adjust logo size as needed */
            width: auto;
            height: auto;
            /* margin: 0 auto; Center the logo */
            display: block;
        }

        .payview-text {
            text-align: left;
            margin-bottom: 10px;
        }

        /* Company Information Tables */
        .company-info-table {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .company-info-table table {
            width: 48%;
            /* Adjust table width */
            border-collapse: collapse;
        }

        .company-info-table td {
            padding: 2px 5px;
        }

        .company-info-table td:first-child {
            font-weight: bold;
            width: 40%;
        }

        /* Form Title */
        .form-title {
            text-align: center;
            margin-bottom: 10px;
        }

        /* Form Details Table */
        .form-details-table table {
            width: 100%;
            border-collapse: collapse;
        }

        .form-details-table td {
            padding: 2px 5px;
        }

        .form-details-table td:nth-child(even) {
            text-align: center;
        }

        /* Employee Information Table */
        .employee-table table {
            width: 100%;
            border-collapse: collapse;
        }

        .employee-table td {
            /* border: 1px solid black; */
            padding: 2px 5px;
            text-align: right;
        }

        .employee-table th {
            font-weight: bold;
            border-bottom: 1px solid;
            border-top: 1px solid;
            padding: 2px 5px;
            text-align: left;
        }
        th{
            font-weight: bold;
        }
        td{
            font-size: 10px;
        }

        .employee-table th:nth-child(1),
        .employee-table td:nth-child(1) {
            text-align: left;
        }

        .employee-table .totals-row td {
            font-weight: bold;
        }

        /* Page Number */
        .page-number {
            position: absolute;
            bottom: 2cm;
            right: 2cm;
            font-size: 10px;
        }
    </style>
</head>

<body>

    <div class="page">
        <div class="zimra-branding">
            <img src="/files/payview.png" alt="ZIMRA Logo" class="zimra-logo">
        </div>

        <div class="company-info-table">
            <table>
                <tr>
                    <td>COMPANY NAME:</td>
                    <td>${company.company_name || 'APOINT'}</td>
                </tr>
                <tr>
                    <td>ITF16 YEAR:</td>
                    <td>${itf16Year}</td>
                </tr>
                <tr>
                    <td>CONTACT ADDRESS:</td>
                    <td>${'ZIMBABWE'}</td>
                </tr>
            </table>
            <table>
                <tr>
                    <td>BP NUMBER:</td>
                    <td>${'1234000'}</td>
                </tr>
                <tr>
                    <td>FDS METHOD:</td>
                    <td>None</td>
                </tr>
                <tr>
                    <td>CONTACT PHONE:</td>
                    <td>${'0773 100 715'}</td>
                </tr>
            </table>
            <div style="float: right;">
                <p>ITF16 FORM</p>
                <table style="text-align: right; border: 1px solid;">
                    <tr>
                        <td><img src="/files/payview.png" alt=""></td>
                    </tr>
                </table>
            </div>
           
        </div>


        <div class="form-details-table" style="clear: both;">
            <table>
                <tr>
                    <th></th>
                    <th>NO OF PAY PERIODS: ${reportData.length}</th>
                    <th>CURRENT PERIOD:</th>
                    <th>${toDate}</th>
                    <th>PAYROLL CODE: 01</th>
                    <th>CURRENCY:</th>
                    <th>${currency}</th>
                </tr>
            </table>
        </div>

        <div class="employee-table">
            <table>
                <thead>
                    <tr>
                        <th></th>
                        <th>SURNAME</th>
                        <th>FIRST NAMES</th>
                        <th>ID NUMBER</th>
                        <th>DOB</th>
                        <th>EMP/FROM</th>
                        <th>EMPL/TO</th>
                        <th>GROSS PAY</th>
                        <th>BASIC</th>
                        <th>BONUS</th>
                        <th>BENEFITS</th>
                        <th>PENSION</th>
                        <th>NSSA</th>
                        <th>NEC</th>
                        <th>T/UNION</th>
                        <th>TAX CREDITS</th>
                        <th>P.A.Y.E.</th>
                        <th>AIDS Levy</th>
                    </tr>
                </thead>
                <tbody>
                    ${employeeRows}
                    <tr class="totals-row" style="border-top: 1px solid; border-bottom: 1px solid;">
                        <td colspan="6" style="text-align: right;">PERIOD TOTALS ARE IN ${currency}</td>
                        <td></td>
                        <td>${format_currency(totals.gross_pay, currency)}</td>
                        <td>${format_currency(totals.gross_pay, currency)}</td>
                        <td>${format_currency(0, currency)}</td>
                        <td>${format_currency(0, currency)}</td>
                        <td>${format_currency(totals.basic_pension, currency)}</td>
                        <td>${format_currency(0, currency)}</td>
                        <td>${format_currency(0, currency)}</td>
                        <td>${format_currency(0, currency)}</td>
                        <td>${format_currency(0, currency)}</td>
                        <td>${format_currency(totals.paye, currency)}</td>
                        <td>${format_currency(totals.aids_levy, currency)}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="page-number">
            <p>Page: 1 of 1</p>
        </div>
    </div>

</body>

</html>`;
            
            // Open the HTML in a new window for printing
            const w = window.open();
            w.document.write(html);
            w.document.close();
            
            // Add print functionality
            setTimeout(() => {
                w.print();
                // Close the window after printing (optional)
                // w.close();
            }, 1000);
        }
    });
}

function format_currency(value, currency) {
    // Convert to number and ensure it's a valid number
    const numValue = parseFloat(value) || 0;
    
    // Format to 2 decimal places with thousand separators
    const formattedValue = numValue.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    // Add currency symbol
    return currency + " " + formattedValue;
}

