import frappe
from frappe import _

@frappe.whitelist()
def validate_warehouses():
    sales_invoice = frappe.get_all("Sales Invoice",
        filters={
            "docstatus": 1
        },
        pluck="name"
    )
    processed = 0
    for inv in sales_invoice:
        doc = frappe.get_doc('Sales Invoice', inv)
        if doc.docstatus == 1:  # Only run for submitted documents
            has_mismatch = False
            
            for item in doc.items:
                if item.warehouse != doc.set_warehouse:
                    has_mismatch = True
                    break
                    
            if has_mismatch:
                # Cancel the document
                doc.cancel()
                
                # Update item warehouses
                for item in doc.items:
                    item.warehouse = doc.set_warehouse
                
                # Save and submit
                doc.docstatus = 0  # Set as draft
                doc.save()
                doc.submit()
                processed += 1
                
    return processed