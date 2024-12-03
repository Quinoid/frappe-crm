from bs4 import BeautifulSoup
import frappe
from frappe import _
from frappe.translate import get_all_translations
from frappe.utils import validate_email_address, split_emails, cstr
from frappe.utils.telemetry import POSTHOG_HOST_FIELD, POSTHOG_PROJECT_FIELD


@frappe.whitelist(allow_guest=True)
def get_translations():
	if frappe.session.user != "Guest":
		language = frappe.db.get_value("User", frappe.session.user, "language")
	else:
		language = frappe.db.get_single_value("System Settings", "language")

	return get_all_translations(language)


@frappe.whitelist()
def get_user_signature():
	user = frappe.session.user
	user_email_signature = (
		frappe.db.get_value(
			"User",
			user,
			"email_signature",
		)
		if user
		else None
	)

	signature = user_email_signature or frappe.db.get_value(
		"Email Account",
		{"default_outgoing": 1, "add_signature": 1},
		"signature",
	)

	if not signature:
		return

	soup = BeautifulSoup(signature, "html.parser")
	html_signature = soup.find("div", {"class": "ql-editor read-mode"})
	_signature = None
	if html_signature:
		_signature = html_signature.renderContents()
	content = ""
	if (cstr(_signature) or signature):
		content = f'<br><p class="signature">{signature}</p>'
	return content


@frappe.whitelist()
def get_posthog_settings():
	return {
		"posthog_project_id": frappe.conf.get(POSTHOG_PROJECT_FIELD),
		"posthog_host": frappe.conf.get(POSTHOG_HOST_FIELD),
		"enable_telemetry": frappe.get_system_settings("enable_telemetry"),
		"telemetry_site_age": frappe.utils.telemetry.site_age(),
	}


def check_app_permission():
	if frappe.session.user == "Administrator":
		return True

	roles = frappe.get_roles()
	if any(role in ["System Manager", "Sales User", "Sales Manager", "Sales Master Manager"] for role in roles):
		return True

	return False


@frappe.whitelist(allow_guest=True)
def accept_invitation(key: str = None):
    
    # Check if the key is provided
    if not key:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/invitation-error"
        return  # Ensure the function exits here

    # Fetch the invitation based on the key
    result = frappe.db.get_all("CRM Invitation", filters={"key": key}, pluck="name")
    if not result:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/invitation-error"
        return  # Ensure the function exits here if no result is found

    # Proceed with the invitation if the result exists
    invitation = frappe.get_doc("CRM Invitation", result[0])
    invitation.accept()
    invitation.reload()

    # Check if the invitation was accepted
    if invitation.status == "Accepted":
        frappe.local.login_manager.login_as(invitation.email)
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/crm"
        return  # Ensure the function exits after redirection


# @frappe.whitelist()
# def invite_by_email(emails: str, role: str):
# 	if not emails:
# 		return
# 	email_string = validate_email_address(emails, throw=False)
# 	email_list = split_emails(email_string)
# 	if not email_list:
# 		return
# 	existing_members = frappe.db.get_all("User", filters={"email": ["in", email_list]}, pluck="email")
# 	existing_invites = frappe.db.get_all(
# 		"CRM Invitation",
# 		filters={"email": ["in", email_list], "role": ["in", ["Sales Manager", "Sales User"]]},
# 		pluck="email",
# 	)

# 	to_invite = list(set(email_list) - set(existing_members) - set(existing_invites))

# 	for email in to_invite:
# 		frappe.get_doc(doctype="CRM Invitation", email=email, role=role).insert(ignore_permissions=True)

@frappe.whitelist()
def invite_by_email(emails: str, role: str):
    if not emails:
        #frappe.throw(_("No email addresses provided."))  # Throw an error if no emails are provided
        frappe.response["http_status_code"] = 400
        return {
                "status": "error",
                "message": "No email addresses provided."
            }

    email_string = validate_email_address(emails, throw=False)
    email_list = split_emails(email_string)
    
    if not email_list:
    	frappe.response["http_status_code"] = 400
    	return {
                "status": "error",
                "message": "No valid email addresses found."
            }
        #frappe.throw(_("No valid email addresses found."))  # Throw an error if email list is empty

    frappe.log_error(f"Emails after split: {email_list}")  # Log the list for debugging

    # Get existing members and invites
    existing_members = frappe.db.get_all("User", filters={"email": ["in", email_list]}, pluck="email")
    existing_invites = frappe.db.get_all(
        "CRM Invitation",
        filters={"email": ["in", email_list], "role": ["in", ["Sales Manager", "Sales User"]]},
        pluck="email",
    )

    frappe.log_error(f"Existing members: {existing_members}")
    frappe.log_error(f"Existing invites: {existing_invites}")

    # Calculate emails to invite
    to_invite = list(set(email_list) - set(existing_members) - set(existing_invites))
    
    # If no emails to invite, show a message
    if not to_invite:
    	frappe.response["http_status_code"] = 400
    	return {
                "status": "error",
                "message": "All emails are either existing members or already invited."
            }
        #frappe.msgprint(_("All emails are either existing members or already invited."))  # Show message if no new invites

    frappe.log_error(f"Emails to invite: {to_invite}")  # Log the emails that will be invited

    # Invite the remaining emails
    for email in to_invite:
        try:
            frappe.get_doc(doctype="CRM Invitation", email=email, role=role).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error inviting {email}: {str(e)}")  # Log any error encountered while inviting
            frappe.msgprint(_("Error inviting {0}: {1}").format(email, str(e)))  # Show error message if invite fails

    # Optionally, refresh the list after inviting
    # Refresh logic goes here (e.g., re-fetch the list or notify the user that the process is complete)

