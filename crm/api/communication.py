import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from frappe.utils.password import update_password

@frappe.whitelist()
def get_communications(reference_doctype=None, reference_name=None):
    filters = []
    if reference_doctype:
        filters.append(["reference_doctype", "=", reference_doctype])
    if reference_name:
        filters.append(["reference_name", "=", reference_name])
    return frappe.get_all(
        "Communication",
        filters=filters,
        fields=["name", "subject", "content", "communication_date"]
    )

@frappe.whitelist()
def get_communications_by_recipient(email):
    # Fetch communications where the recipients field contains the given email
    return frappe.get_all(
        "Communication",
        filters=[["recipients", "like", f"%{email}%"]],
        fields=["name", "subject", "content", "recipients", "communication_date"]
    )


@frappe.whitelist()
def get_communications_by_email(email):
    if isinstance(email, list):
        if len(email) == 1:
            email = email[0]
        else:
            frappe.throw("Email parameter must be a single string, not a list.")
    
    if not isinstance(email, str):
        frappe.throw("Email must be a string.")

    email = email.lower()

    # Construct the SQL query with OR conditions for sender, recipients, cc, or bcc
    query = """
        SELECT name, subject, content, sender, recipients, cc, bcc, communication_date
        FROM `tabCommunication`
        WHERE LOWER(sender) LIKE %s
        OR LOWER(recipients) LIKE %s
        OR LOWER(cc) LIKE %s
        OR LOWER(bcc) LIKE %s
        ORDER BY communication_date DESC
    """

    communications = frappe.db.sql(query, (f"%{email}%", f"%{email}%", f"%{email}%", f"%{email}%"), as_dict=True)

    return communications




@frappe.whitelist(allow_guest=True)
def change_password(new_password, confirm_password, user=None):
    """Custom API to change the password for a specific user."""
    
    

    # If no user is provided, default to the current logged-in user
    user = user or frappe.session.user
    
    # Check if the user exists
    if not frappe.db.exists("User", user):
        frappe.throw(_("User not found"))
    
    # Use frappe.auth.set_password() for password change
    frappe.set_password(user, new_password)

    return _("Password changed successfully")


@frappe.whitelist()
def change_password(new_password: str, confirm_password: str):

    if not new_password or not confirm_password:
            return {"status": "error", "message": "Password fields cannot be empty."}
        
    if new_password != confirm_password:
        return {"status": "error", "message": "The new password and confirm password do not match."}

    try:
        user = frappe.session.user

        # Ensure the user exists
        if not frappe.db.exists("User", user):
            return {"status": "error", "message": f"User '{user}' does not exist."}

        update_password(user, new_password)

        return {"status": "success", "message": f"Password for user '{user}' has been updated successfully."}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Change Password Error")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}









