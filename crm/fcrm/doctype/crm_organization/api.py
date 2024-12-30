import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_organization(name):
	Organization = frappe.qb.DocType("CRM Organization")

	query = (
		frappe.qb.from_(Organization)
		.select("*")
		.where(Organization.name == name)
		.limit(1)
	)

	organization = query.run(as_dict=True)
	if not len(organization):
		frappe.throw(_("organization not found"), frappe.DoesNotExistError)
	organization = organization.pop()


	organization["doctype"] = "CRM Organization"
	organization["fields_meta"] = get_fields_meta("CRM Organization") 
	organization["_form_script"] = get_form_script('CRM Organization')
	organization["_assign"] = get_assigned_users("CRM Organization", organization.name, organization.owner)
	return organization