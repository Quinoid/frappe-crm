import frappe
from frappe import _
from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
@frappe.whitelist()
def get_organization(name):
	Organization = frappe.qb.DocType("CRM Organization")
	CustomLeadService = frappe.qb.DocType("Custom Lead Service")
	CustomLeadTags = frappe.qb.DocType("Custom Lead Tags")
	query = (
		frappe.qb.from_(Organization)
		.select("*")
		.where(Organization.name == name)
		.limit(1)
	)
	organization = query.run(as_dict=True)

	# Fetch the custom_tags from the Custom Lead Tags table
	

	if not len(organization):
		frappe.throw(_("organization not found"), frappe.DoesNotExistError)
	organization = organization.pop()
	tags_query = (
		frappe.qb.from_(CustomLeadTags)
		.select(CustomLeadTags.link_field) 
		.where(CustomLeadTags.parent == name)
	)
	tags = tags_query.run(as_dict=True)
	
	organization["custom_tags"] = [tag["link_field"] for tag in tags]

	organization["doctype"] = "CRM Organization"
	organization["fields_meta"] = get_fields_meta("CRM Organization") 
	organization["_form_script"] = get_form_script('CRM Organization')
	organization["_assign"] = get_assigned_users("CRM Organization", organization.name, organization.owner)
	return organization