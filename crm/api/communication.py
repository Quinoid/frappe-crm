import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from frappe.utils.password import update_password
import json
from frappe.model.document import get_controller
from frappe.model import no_value_fields
from pypika import Criterion
from frappe.utils import make_filter_tuple

from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

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
def get_communications_by_recipient():
    """
    Fetch communications where the recipients field contains the session user's email.
    """
    user_email = frappe.session.user

    if user_email == "Guest":
        return {"status": "error", "message": "Guest users cannot retrieve communications."}

    # Fetch communications where the recipients field contains the user's email
    return frappe.get_all(
        "Communication",
        filters=[["recipients", "like", f"%{user_email}%"]],
        fields=["name", "subject", "content", "recipients", "communication_date"]
    )


@frappe.whitelist()
def get_communications_by_email():
    """
    Fetch communications where the session user's email is present in sender, recipients, cc, or bcc.
    """
    user_email = frappe.session.user

    if user_email == "Guest":
        return {"status": "error", "message": "Guest users cannot retrieve communications."}

    user_email = user_email.lower()

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

    communications = frappe.db.sql(
        query, 
        (f"%{user_email}%", f"%{user_email}%", f"%{user_email}%", f"%{user_email}%"), 
        as_dict=True
    )

    return communications



# @frappe.whitelist()
# def change_password(new_password: str, confirm_password: str):

#     if not new_password or not confirm_password:
#             return {"status": "error", "message": "Password fields cannot be empty."}
        
#     if new_password != confirm_password:
#         return {"status": "error", "message": "The new password and confirm password do not match."}

#     try:
#         user = frappe.session.user

#         # Ensure the user exists
#         if not frappe.db.exists("User", user):
#             return {"status": "error", "message": f"User '{user}' does not exist."}

#         update_password(user, new_password)

#         return {"status": "success", "message": f"Password for user '{user}' has been updated successfully."}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Change Password Error")
#         return {"status": "error", "message": "An unexpected error occurred. Please try again later."}





@frappe.whitelist()
def change_password(new_password: str, confirm_password: str, old_password: str = None):
    # Validate that new and confirm passwords are provided
    if not new_password or not confirm_password:
        return {"status": "error", "message": "New password and confirm password fields cannot be empty."}

    # Check if new password matches confirm password
    if new_password != confirm_password:
        return {"status": "error", "message": "The new password and confirm password do not match."}

    try:
        user = frappe.session.user

        # Ensure the user exists
        if not frappe.db.exists("User", user):
            return {"status": "error", "message": f"User '{user}' does not exist."}

        # Validate the old password if provided
        if old_password:
            from frappe.utils.password import check_password
            try:
                check_password(user, old_password)
            except frappe.exceptions.AuthenticationError:
                return {"status": "error", "message": "The old password is incorrect."}

        # Update the password
        update_password(user, new_password)

        return {"status": "success", "message": f"Password for user '{user}' has been updated successfully."}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Change Password Error")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}


@frappe.whitelist()
def is_password_set():
    try:
        user = frappe.session.user

        # Ensure the user exists
        if not frappe.db.exists("User", user):
            return {"status": "error", "message": f"User '{user}' does not exist."}

        # Check if password is set
        auth_enabled = frappe.db.get_value("User", user, "enabled")
        if not auth_enabled:
            return {
                "status": "success",
                "is_password_set": False,
                "message": "No password is set or user is disabled."
            }

        return {
            "status": "success",
            "is_password_set": True,
            "message": "Password is set for this user."
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check Password Status Error")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}





