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



@frappe.whitelist(allow_guest=True)
def custom_create_event(subject, starts_on, ends_on, event_category="Event", event_type="Private", **kwargs):
    # Create a new document for the Event doctype
    event = frappe.get_doc({
        "doctype": "Event",
        "subject": subject,
        "starts_on": starts_on,
        "ends_on": ends_on,
        "event_category": event_category,
        "event_type": event_type,
        **kwargs  # Allows additional fields to be set dynamically
    })
    
    # Insert the new event document into the database
    event.insert(ignore_permissions=True)
    frappe.db.commit()  # Ensure the data is saved to the database

    # Return the event details to confirm creation
    return {"message": "Event created successfully", "event_name": event.name}


@frappe.whitelist()
def custom_edit_event(name, **kwargs):
    # Fetch the event document by name (ID)
    event = frappe.get_doc("Event", name)

    # Update the fields with the data provided in kwargs
    for key, value in kwargs.items():
        if hasattr(event, key):
            setattr(event, key, value)
    
    # Save changes to the database
    event.save(ignore_permissions=True)
    frappe.db.commit()  # Ensure the changes are saved

    # Return confirmation message with updated event details
    return {"message": "Event updated successfully", "event_name": event.name}

