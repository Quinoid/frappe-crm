import requests
import frappe
from frappe import _
from frappe.utils import nowdate, add_days
from frappe.query_builder import Order
from frappe.query_builder import Field
import json
from frappe.query_builder import DocType
from frappe.query_builder.functions import IfNull


@frappe.whitelist()
def custom_dashboard():
    Task = frappe.qb.DocType("CRM Task")
    Lead = frappe.qb.DocType("CRM Lead")
    Deal = frappe.qb.DocType("CRM Deal")
    Event = frappe.qb.DocType("Event")
    Contact = frappe.qb.DocType("Contact")
    Organisation = frappe.qb.DocType("CRM Organization")
    
    current_date = nowdate()
    current_user = frappe.session.user
    is_admin = current_user == "Administrator"

    # Query to fetch tasks due today or with a previous due date and status backlog/todo
    task_query = (
        frappe.qb.from_(Task)
        .select("*")
        .where(
            ((Task.due_date >= current_date) |
            ((Task.due_date < current_date) & 
            (Task.status.isin(["Backlog", "Todo", "In Progress"]))))
        )
        .orderby(Task.due_date, order=Order.asc)

    )

    if not is_admin:
        task_query = task_query.where(Task.assigned_to == current_user)

    tasks = task_query.run(as_dict=True)
    task_total_count = len(tasks)

    # if not tasks:
    #     return {"task_total_count": task_total_count, "message": _("No tasks found for today")}


    lead_query = frappe.qb.from_(Lead).select("*").where(Field("converted") != 1)
    # if not is_admin:
    #     lead_query = lead_query.where(Lead._assign == current_user)

    leads = lead_query.run(as_dict=True)
    lead_total_count = len(leads)


    deal_query = frappe.qb.from_(Deal).select("*")
    # if not is_admin:
    #     deal_query = deal_query.where(Deal._assign == current_user)

    deals = deal_query.run(as_dict=True)
    deal_total_count = len(deals)

    #contact_query = frappe.qb.from_(Contact).select("*")
    # Construct the query
    contact_query = (
        frappe.qb
        .from_(Contact)
        .select("*")
        .where(IfNull(Field("user"), "") == "")
    )
    contacts = contact_query.run(as_dict=True)
    contact_total_count = len(contacts)

    organisation_query = frappe.qb.from_(Organisation).select("*")
    organisations = organisation_query.run(as_dict=True)
    organisation_total_count = len(organisations)


    event_query = (
        frappe.qb.from_(Event)
        .select("*")
        .where(Field("starts_on").like(f"{current_date}%"))
        .orderby(Event.starts_on, order=Order.asc)

    )
    # if not is_admin:
    #     lead_query = lead_query.where(Lead._assign == current_user)

    events = event_query.run(as_dict=True)
    event_total_count = len(events)

    CallLog = frappe.qb.DocType("CRM Call Log")

    # Fetch the last 5 records ordered by creation or a specific field
    call_log_data = (
        frappe.qb.from_(CallLog)
        .select("*")
        .orderby(CallLog.creation, order=Order.desc) 
        .limit(5)
    )

    call_logs = call_log_data.run(as_dict=True)

    return {
        "task_total_count": task_total_count,
        "lead_total_count": lead_total_count,
        "deal_total_count": deal_total_count,
        "event_total_count": event_total_count,
        "contact_total_count": contact_total_count,
        "organisation_total_count": organisation_total_count,
        "tasks": tasks,
        "events":events,
        "call_logs":call_logs
    }


@frappe.whitelist()
def custom_task_details(name):
    Task = frappe.qb.DocType("CRM Task")

    query = frappe.qb.from_(Task).select("*").where(Task.name == name).limit(1)

    task = query.run(as_dict=True)
    if not len(task):
        frappe.throw(_("Task not found"), frappe.DoesNotExistError)
    task = task.pop()

    task["doctype"] = "CRM Task"

    return task


# @frappe.whitelist()
# def custom_record_count(doctype, domain):

#     limit_counts = {
#         "CRM Lead": 1000,
#         "Contact": 10,
#         "CRM Deal": 10
#     }

#     limit_count = limit_counts.get(doctype)

#     try:
#         DocType = frappe.qb.DocType(doctype)
#         current_user = frappe.session.user

#         record_query = frappe.qb.from_(DocType).select("*")
#         records = record_query.run(as_dict=True)
#         record_total_count = len(records)

#         return {
#             "status": 200,
#             "record_total_count": record_total_count,
#             "limit_count": limit_count
            
#         }
    
#     except frappe.DoesNotExistError:
#         frappe.response["http_status_code"] = 400
#         frappe.throw(_(f"The specified doctype '{doctype}' does not exist."), frappe.ValidationError)

#     except Exception as e:
#         frappe.log_error(message=str(e), title="Custom Record Count Error")
#         frappe.throw(_("An error occurred while fetching the record count."), frappe.ValidationError)


@frappe.whitelist()
def custom_record_count():
    try:
        import json

        file_path = frappe.get_site_path("domain_limit.json")

        # Load the domain limits JSON file
        with open(file_path, "r") as file:
            domain_limit = json.load(file)

        # Validate the JSON structure
        if not domain_limit.get("limits") or not isinstance(domain_limit["limits"], list):
            frappe.response["http_status_code"] = 500
            frappe.throw(_("Invalid structure in domain_limit.json file."), frappe.ValidationError)

        limits = domain_limit["limits"][0]

        doctype_limit_map = {
            "CRM Lead": "lead_limit_count",
            "Contact": "contact_limit_count",
            "CRM Deal": "deal_limit_count",
            "User": "user_limit_count",
        }

        result = {}

        for doctype, limit_key in doctype_limit_map.items():
            limit_count = limits.get(limit_key, 0)

            DocType = frappe.qb.DocType(doctype)
            
            if doctype == "CRM Lead":
                record_query = frappe.qb.from_(DocType).select("*").where(frappe.qb.Field("converted") != 1)
            else:
                record_query = frappe.qb.from_(DocType).select("*")

            records = record_query.run(as_dict=True)
            record_total_count = len(records)

            result[doctype.split()[-1].lower()] = {
                limit_key: limit_count,
                "record_total_count": record_total_count,
            }

        # Add additional features to the response
        result.update({
            "email_feature": limits.get("email_feature", 1),
            "calendar_feature": limits.get("calendar_feature", 1),
            "twilio_feature": limits.get("twilio_feature", 1),
            "whatsapp_feature": limits.get("whatsapp_feature", 1),
            "custom_view_setup": limits.get("custom_view_setup", 1),
            "custom_field_setup": limits.get("custom_field_setup", 1),
            "custom_reports": limits.get("custom_reports", 1),
            "attachment_size": limits.get("attachment_size", 5),
            "total_storage": limits.get("total_storage", 10),
        })

        return {"limits": result}

    except FileNotFoundError:
        frappe.response["http_status_code"] = 500
        frappe.throw(_("The domain_limit.json file is missing in the sites folder."), frappe.ValidationError)

    except json.JSONDecodeError:
        frappe.response["http_status_code"] = 500
        frappe.throw(_("Error parsing the domain_limit.json file. Please check its structure."), frappe.ValidationError)

    except Exception as e:
        frappe.log_error(message=str(e), title="Custom Record Count Error")
        frappe.throw(_("An error occurred while fetching the record count."), frappe.ValidationError)





@frappe.whitelist()
def custom_delete(doctype, name):
    try:
        # Attempt to delete the document
        frappe.delete_doc(doctype, name, ignore_permissions=True)
        
        # Success response
        return {
            "status": "success",
            "message": _(f"{doctype} '{name}' has been successfully deleted.")
        }
    
    except frappe.LinkExistsError as e:
        # Custom error response for link exists error
        frappe.response["http_status_code"] = 400
        return {
            "status": "error",
            "error_type": "LinkExistsError",
            "message": str(e)
        }
    
    except Exception as e:
        # General error response
        frappe.response["http_status_code"] = 400
        return {
            "status": "error",
            "error_type": "GeneralError",
            "message": str(e)
        }


@frappe.whitelist()
def get_users_with_roles():
    """
    Fetch all users along with their assigned roles who have either 'Sales Manager' or 'Sales User' roles.
    """
    users = frappe.get_all("User", fields=["name", "full_name", "email", "enabled"])
    filtered_users = []
    
    for user in users:
        # Fetch roles directly from the User's child table
        roles = [role.role for role in frappe.get_all("Has Role", filters={"parent": user["name"]}, fields=["role"])]
        
        # Check if the user has 'Sales Manager' or 'Sales User' role
        if "Sales Manager" in roles or "Sales User" in roles:
            user["roles"] = roles
            filtered_users.append(user)
    
    return filtered_users



@frappe.whitelist()
def set_user_status(user_email, enabled):
    """
    Enable or disable a user based on the `enabled` flag.
    :param user_email: Email ID of the user to update
    :param enabled: 1 to enable, 0 to disable
    """
    if not frappe.db.exists("User", user_email):
        frappe.throw(f"User with email {user_email} does not exist.")
    
    enabled_flag = int(enabled)
    frappe.db.set_value("User", user_email, "enabled", enabled_flag)
    frappe.db.commit()
    return {"message": f"User {user_email} {'enabled' if enabled_flag else 'disabled'} successfully."}
