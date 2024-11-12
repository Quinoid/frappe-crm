import requests
import frappe
from frappe import _
from frappe.utils import nowdate, add_days
from frappe.query_builder import Order

@frappe.whitelist()
def custom_dashboard():
    Task = frappe.qb.DocType("CRM Task")
    Lead = frappe.qb.DocType("CRM Lead")
    Deal = frappe.qb.DocType("CRM Deal")
    Event = frappe.qb.DocType("Event")
    
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


    lead_query = frappe.qb.from_(Lead).select("*")
    # if not is_admin:
    #     lead_query = lead_query.where(Lead._assign == current_user)

    leads = lead_query.run(as_dict=True)
    lead_total_count = len(leads)


    deal_query = frappe.qb.from_(Deal).select("*")
    # if not is_admin:
    #     deal_query = deal_query.where(Deal._assign == current_user)

    deals = deal_query.run(as_dict=True)
    deal_total_count = len(deals)

    event_query = (
        frappe.qb.from_(Event)
        .select("*")
        .where(
            (Event.starts_on <= current_date) & (Event.ends_on >= current_date) 
        )
        .orderby(Event.starts_on, order=Order.asc)

    )
    # if not is_admin:
    #     lead_query = lead_query.where(Lead._assign == current_user)

    events = event_query.run(as_dict=True)
    event_total_count = len(events)

    return {
        "task_total_count": task_total_count,
        "lead_total_count": lead_total_count,
        "deal_total_count": deal_total_count,
        "event_total_count": event_total_count,
        "tasks": tasks,
        "events":events
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


@frappe.whitelist()
def custom_record_count(doctype, domain):

    limit_counts = {
        "CRM Lead": 100,
        "CRM Contact": 10,
        "CRM Deal": 10
    }

    limit_count = limit_counts.get(doctype)

    try:
        DocType = frappe.qb.DocType(doctype)
        current_user = frappe.session.user

        record_query = frappe.qb.from_(DocType).select("*")
        records = record_query.run(as_dict=True)
        record_total_count = len(records)

        if record_total_count >= limit_count:
            return {
                "status": 500,
                "error_type": "LimitExceeded",
                "message": _("You have reached the maximum {0} limit of {1} for your plan and cannot create additional records.").format(doctype, limit_count),
                "record_total_count": record_total_count,
                "limit_count": limit_count
            }


        return {
            "record_total_count": record_total_count,
            "status": 200,
            "message": "Within limit"
        }
    
    except frappe.DoesNotExistError:
        frappe.throw(_(f"The specified doctype '{doctype}' does not exist."), frappe.ValidationError)

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
        return {
            "status": 500,
            "error_type": "LinkExistsError",
            "message": str(e)
        }

    except Exception as e:
        # General error response
        return {
            "status": 500,
            "error_type": "GeneralError",
            "message": str(e)
        }
