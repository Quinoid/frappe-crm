import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_lead(name):
    Lead = frappe.qb.DocType("CRM Lead")
    CustomLeadService = frappe.qb.DocType("Custom Lead Service")

    # Query the CRM Lead details
    query = frappe.qb.from_(Lead).select("*").where(Lead.name == name).limit(1)
    lead = query.run(as_dict=True)
    
    if not len(lead):
        frappe.throw(_("Lead not found"), frappe.DoesNotExistError)
    lead = lead.pop()

    lead["doctype"] = "CRM Lead"

    # Fetch the interested services from the Custom Lead Service table
    services_query = (
        frappe.qb.from_(CustomLeadService)
        .select(CustomLeadService.link_field)  # Replace 'link_field' with your actual field name
        .where(CustomLeadService.parent == name)
    )
    services = services_query.run(as_dict=True)
    
    # Add the interested services to the lead data
    lead["interested_services_for_lead"] = [service["link_field"] for service in services]

    # Additional fields
    lead["fields_meta"] = get_fields_meta("CRM Lead")
    lead["_form_script"] = get_form_script('CRM Lead')
    lead["_assign"] = get_assigned_users("CRM Lead", lead.name, lead.owner)

    return lead

