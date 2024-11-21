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





