import frappe

def validate(doc, method):
    calculate_nssa(doc)
    update_total_deductions(doc)
    calculate_allowable_deductions(doc)
    calculate_tax(doc)

def calculate_nssa(doc):
    for row in doc.deductions:
        if row.salary_component == 'NSSA':
            gross_pay = doc.gross_pay or 0
            row.amount = gross_pay * 0.045

def update_total_deductions(doc):
    total = 0
    for row in doc.deductions:
        total += row.amount or 0
    doc.total_deduction = total

def calculate_allowable_deductions(doc):
    medical_amount = 0
    nssa_amount = 0
    
    # Get Medical and NSSA amounts
    for row in doc.deductions:
        if row.salary_component == 'Medical':
            medical_amount = row.amount
        if row.salary_component == 'NSSA':
            nssa_amount = row.amount
    
    # Calculate allowable deductions
    total_allowable = (medical_amount * 0.5) + nssa_amount
    doc.custom_total_allowable_deductions = total_allowable
    
    # Calculate taxable income
    doc.custom_total_taxable_income = doc.gross_pay - total_allowable

def calculate_tax(doc):
    salary_structure_assignment = frappe.get_value(
        "Salary Structure Assignment",
        {
            "employee": doc.employee,
            # "salary_structure": doc.salary_structure,
            "docstatus": 1
        },
        "income_tax_slab"
    )
    
    if not salary_structure_assignment:
        return
        
    taxable_income = doc.custom_total_taxable_income
    tax_slab = frappe.get_doc("Income Tax Slab", salary_structure_assignment)
    total_tax = 0
    
    for slab in tax_slab.slabs:
        if (taxable_income >= slab.from_amount and (taxable_income <= slab.to_amount or not slab.to_amount)):
            tax = (taxable_income * (slab.percent_deduction / 100)) - slab.custom_amount_deduction
            total_tax = tax
            break

    payee_exists = False

    # Update PAYEE component in deductions
    for row in doc.deductions:
        if row.salary_component == 'Payee':  # Adjust component name if different
            row.amount = total_tax
            payee_exists = True
        if row.salary_component == 'Aids Levy':
            row.amount = total_tax * 0.03

    # Add PAYEE if it doesn't exist
    if not payee_exists:
        doc.append('deductions', {
            'salary_component': 'Payee',
            'amount': total_tax
        })
    
    update_total_deductions(doc)
