import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_doctype_data(doctype, name):
    Doctype = frappe.qb.DocType(doctype)

    query = frappe.qb.from_(Doctype).select("*").where(Doctype.name == name).limit(1)

    data = query.run(as_dict=True)
    if not len(data):
        frappe.throw(_("data not found"), frappe.DoesNotExistError)
    data = data.pop()

    data["doctype"] = doctype
    data["fields_meta"] = get_fields_meta(doctype)
    data["_form_script"] = get_form_script(doctype)
    data["_assign"] = get_assigned_users(doctype, data.name, data.owner)
    return data


@frappe.whitelist()
def get_company_details():
    Doctype = frappe.qb.DocType('Company')


    company = frappe.db.get_single_value("Global Defaults", "default_company")

    query = frappe.qb.from_(Doctype).select("*").where(Doctype.name == company).limit(1)

    data = query.run(as_dict=True)
    if not len(data):
        frappe.throw(_("data not found"), frappe.DoesNotExistError)
    data = data.pop()

    data["doctype"] = 'Company'
    data["fields_meta"] = get_fields_meta('Company')
    data["_form_script"] = get_form_script('Company')
    data["_assign"] = get_assigned_users('Company', data.name, data.owner)
    return data