import requests
import frappe
from frappe import _
from frappe.utils import nowdate, add_days


@frappe.whitelist()
def custom_list_events(starts_on=None, ends_on=None):
    Event = frappe.qb.DocType("Event")
    
    # Get current date and the date 6 days from now
    current_date = nowdate()
    next_six_days = add_days(current_date, 6)

    # Set default values if starts_on and ends_on are None
    if not starts_on:
        starts_on = current_date
    if not ends_on:
        ends_on = next_six_days


    # Query to fetch events that are between the provided starts_on and ends_on
    query = (
        frappe.qb.from_(Event)
        .select("*")
        .where(
            ((Event.starts_on >= starts_on) & (Event.starts_on <= ends_on)) &
            ((Event.ends_on >= starts_on) & (Event.ends_on <= ends_on)) 
        )
    )
    events = query.run(as_dict=True)

    if not events:
        return {"message": _("No events found")}

    return events


@frappe.whitelist()
def custom_get_event_details(name):
    Event = frappe.qb.DocType("Event")

    query = frappe.qb.from_(Event).select("*").where(Event.name == name).limit(1)

    event = query.run(as_dict=True)
    if not len(event):
        frappe.throw(_("Event not found"), frappe.DoesNotExistError)
    event = event.pop()

    event["doctype"] = "Event"

    return event
