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
                new_doc = frappe.copy_doc(doc)
                new_doc.docstatus = 0
                new_doc.amended_from = doc.name
                
                # Update warehouses in the new document
                for item in new_doc.items:
                    item.warehouse = new_doc.set_warehouse
                
                new_doc.save()
                new_doc.submit()
                processed += 1
                
    return processed