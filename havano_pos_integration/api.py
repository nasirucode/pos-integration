import frappe
from frappe import _

@frappe.whitelist()
def test_api(name):
    # Create a welcome message
    msg = f"Welcome {name}!!!"
    # Fetch product details
    product_details = frappe.get_all("Item", fields=["name", "item_code", "item_group"])
    
    return msg

@frappe.whitelist()
def create_pos_opening_entry():
    try:
        # Get form data
        data = frappe.local.form_dict

        # Check for required fields
        required_fields = ["period_start_date", "company", "user", "pos_profile", "balance_details"]
        for field in required_fields:
            if field not in data:
                frappe.throw(_("Missing required field: {0}").format(field))

        # Create POS Opening Entry document
        pos_opening_entry = frappe.get_doc({
            "doctype": "POS Opening Entry",
            "period_start_date": data.get("period_start_date"),
            "company": data.get("company"),
            "user": data.get("user"),
            "pos_profile": data.get("pos_profile"),
            "balance_details": data.get("balance_details")
        })

        # Insert and submit the document
        pos_opening_entry.insert()
        pos_opening_entry.submit()

        # Commit the transaction
        frappe.db.commit()

        return pos_opening_entry.as_dict()

    except Exception as e:
        # Log error and return error message
        frappe.log_error(message=str(e), title="Error creating POS Opening Entry")
        return {"error": str(e)}

@frappe.whitelist()
def get_inventory():
    # Fetch price list, inventory, and item price list
    price_list = frappe.get_all("Price List", fields = ["price_list_name","currency"])
    inventory = frappe.get_all("Bin", fields = ["item_code","valuation_rate","warehouse","actual_qty","ordered_qty","stock_value"])
    item_price_list = frappe.get_all("Item Price", fields = ["item_code","uom","price_list","price_list_rate","currency","currency","supplier"])
    return { "price_list": price_list, "inventory": inventory, "item_price_list": item_price_list }

@frappe.whitelist()
def get_warehouses():
    # Fetch inventory and warehouse details
    inventory = frappe.get_all("Bin", fields=["item_code", "valuation_rate", "warehouse", "actual_qty", "ordered_qty", "stock_value"])
    warehouses = frappe.get_all("Warehouse", fields=["name", "company", "account", "warehouse_type"])
    
    # Calculate total quantity and value for each warehouse
    warehouse_inventory = {}
    for item in inventory:
        warehouse = item["warehouse"]
        if warehouse not in warehouse_inventory:
            warehouse_inventory[warehouse] = {
                "total_quantity": 0,
                "total_value": 0
            }
        warehouse_inventory[warehouse]["total_quantity"] += item["actual_qty"]
        warehouse_inventory[warehouse]["total_value"] += item["stock_value"]

    # Add total quantity and value to warehouse details
    for warehouse in warehouses:
        name = warehouse["name"]
        warehouse["total_quantity"] = warehouse_inventory.get(name, {}).get("total_quantity", 0)
        warehouse["total_value"] = warehouse_inventory.get(name, {}).get("total_value", 0)

    return warehouses

@frappe.whitelist()
def get_cost_center():
    # Fetch cost center details
    return frappe.get_all("Cost Center", fields = ["cost_center_name", "cost_center_number", "parent_cost_center", "company"])

@frappe.whitelist()
def get_pos_profile():
    # Fetch POS profile details
    pos_profiles = frappe.get_all("POS Profile", fields=["name", "company", "warehouse", "customer", "company_address", "cost_center","selling_price_list"])

    response = []

    for profile in pos_profiles:
        profile_data = {
            "name": profile.name,
            "company": profile.company,
            "warehouse": profile.warehouse,
            "customer": profile.customer,
            "company_address": profile.company_address,
            "cost_center": profile.cost_center,
            "applicable_for_users": [],
            "payments": [],
            "price_list": profile.selling_price_list
        }

        # Fetch applicable users for the profile
        try: 
            if frappe.db.exists("POS Profile User",{"parent":profile.name}):
                applicable_for_users = frappe.get_all("POS Profile User",filters={"parent": profile.name}, fields=["user","default"])
                profile_data["applicable_for_users"] = applicable_for_users if applicable_for_users else []
            else:
                profile_data["applicable_for_users"] = []
        except Exception as e: 
            profile_data["applicable_for_users"] = []
        
        # Fetch payment methods for the profile
        try: 
            if frappe.db.exists("POS Payment Method",{"parent":profile.name}):
               payments = frappe.get_all("POS Payment Method", filters={"parent": profile.name}, fields=["mode_of_payment", "default"])
               profile_data["payments"] = payments if payments else []
            else:
                profile_data["payments"] = []
        except Exception as e:
            profile_data["payments"] = []

        response.append(profile_data)

    return response

@frappe.whitelist()
def get_products():
    # Fetch all necessary data
    products_data = frappe.get_all("Bin", fields=["item_code", "warehouse", "actual_qty"])
    price_lists = frappe.get_all("Item Price", fields=["price_list", "price_list_rate", "item_code"])
    product_details = frappe.get_all("Item", fields=["name", "item_code", "item_group"])
    
    # Initialize products dictionary with all items
    products = {detail['item_code']: {"warehouses": [], "prices": []} for detail in product_details}

    # Add warehouse data
    for product in products_data:
        item_code = product["item_code"]
        products[item_code]["warehouses"].append({
            "warehouse": product["warehouse"],
            "qtyOnHand": product["actual_qty"]
        })
    
    # Add price list data
    for price in price_lists:
        item_code = price["item_code"]
        products[item_code]["prices"].append({
            "priceName": price["price_list"],
            "price": price["price_list_rate"]
        })
    
    # Compile final products list with defaults
    final_products = []
    for detail in product_details:
        defaults = frappe.get_all("Item Default", filters={"parent": detail.name}, fields=["default_warehouse", "default_price_list"])
        item_code = detail["item_code"]

        warehouses = products[item_code]["warehouses"]
        prices = products[item_code]["prices"]

        # Add default warehouse if no warehouse data
        if not warehouses and defaults:
            warehouses.append({
                "warehouse": defaults[0].get("default_warehouse"),
                "qtyOnHand": 0
            })
        
        # Add default price list if no price data
        if not prices and defaults:
            prices.append({
                "priceName": defaults[0].get("default_price_list"),
                "price": 0
            })
        
        final_product = {
            "itemcode": item_code,
            "itemname": detail["name"],
            "groupname": detail["item_group"],
            "warehouses": warehouses,
            "prices": prices
        }
        final_products.append(final_product)

    return {"products": final_products}

@frappe.whitelist()
def get_sales_invoice():
    # Fetch sales invoice details
    final_invoice = []
    sales_invoice_list =  frappe.get_all("Sales Invoice", fields = ["name", "customer","company", "customer_name", "posting_date", "posting_time","due_date","total_qty","total","total_taxes_and_charges","grand_total"])
    for invoice in sales_invoice_list:
        # Fetch items for each invoice
        items = frappe.get_all("Sales Invoice Item", filters={"parent": invoice.name},fields = ["item_name", "qty", "rate", "amount",])
        invoice = {
            "name": invoice.name,
            "customer": invoice.customer,
            "company": invoice.company,
            "customer_name": invoice.customer_name,
            "posting_date": invoice.posting_date,
            "posting_time": invoice.posting_time,
            "due_date": invoice.due_date,
            "items": items,
            "total_qty": invoice.total_qty,
            "total": invoice.total,
            "total_taxes_and_charges": invoice.total_taxes_and_charges,
            "grand_total": invoice.grand_total
        }
        final_invoice.append(invoice)
    
    return final_invoice

@frappe.whitelist()
def get_user():
    # Fetch user details
    return frappe.get_all("User", fields = ["email","first_name", "last_name", "username", "gender","location"])

@frappe.whitelist()
def get_customer():
    # Fetch customer details with default price list
    customers = frappe.get_all("Customer", filters = {"default_price_list": ["!=", ""]} ,fields = ["customer_name","customer_type","custom_cost_center","custom_warehouse","gender","customer_pos_id","default_price_list"])
    for customer in customers:
        # Fetch item prices for each customer
        customer.items = frappe.get_all("Item Price", filters = {"price_list":customer.default_price_list}, fields = ["item_code","item_name","price_list_rate"])
    return customers

@frappe.whitelist()
def get_account():
    # Fetch account details
    return frappe.get_all("Account", fields = ["account_name","account_number","company","parent_account","account_type"])

def submit_pos_opening_entry(doc,method):
    # Submit POS Opening Entry document
    doc.submit()

def submit_pos_closing_entry(doc, method=None):
    # Submit POS Closing Entry document
    doc.submit()

def submit_pos_invoice(doc, method=None):
    # Submit POS Invoice document
    doc.submit()

def submit_payment_entry(doc, method=None):
    # Submit Payment Entry document
    doc.submit()

def submit_sales_invoice(doc, method=None):
    # Submit Sales Invoice document
    doc.submit()
