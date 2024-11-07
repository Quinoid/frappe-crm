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
    if not is_admin:
        lead_query = lead_query.where(Lead._assign == current_user)

    leads = lead_query.run(as_dict=True)
    lead_total_count = len(leads)


    deal_query = frappe.qb.from_(Deal).select("*")
    if not is_admin:
        deal_query = deal_query.where(Deal._assign == current_user)

    deals = deal_query.run(as_dict=True)
    deal_total_count = len(deals)

    return {
        "task_total_count": task_total_count,
        "lead_total_count": lead_total_count,
        "deal_total_count": deal_total_count,
        "tasks": tasks
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



