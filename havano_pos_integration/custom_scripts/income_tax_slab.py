from frappe.model.document import Document

# import frappe
import erpnext

def validate(doc, method):
		if doc.company:
			doc.currency = doc.currency