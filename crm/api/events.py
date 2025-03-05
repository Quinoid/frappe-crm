import requests
import frappe
from frappe import _
from frappe.utils import nowdate, add_days
import json
from frappe.model.document import get_controller
from frappe.model import no_value_fields
from pypika import Criterion
from frappe.utils import make_filter_tuple

from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script


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
    # Fetch Event details
    Event = frappe.qb.DocType("Event")
    CustomUser = frappe.qb.DocType("Custom User")

    # Query Event details
    event_query = frappe.qb.from_(Event).select("*").where(Event.name == name).limit(1)
    event = event_query.run(as_dict=True)
    
    if not event:
        frappe.throw(_("Event not found"), frappe.DoesNotExistError)
    
    event = event[0]
    event["doctype"] = "Event"

    # Query Custom Participants linked to the Event
    participants_query = (
        frappe.qb.from_(CustomUser)
        .select(CustomUser.link_field)
        .where(CustomUser.parent == name)
    )
    participants = participants_query.run(as_dict=True)

    # Convert the participants to a comma-separated string and wrap it in an array
    event["custom_participant"] = [p["link_field"] for p in participants]

    return event




@frappe.whitelist()
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

    # Update main fields with the data provided in kwargs
    for key, value in kwargs.items():
        if key == "custom_participant":
            # Handle child table updates
            if isinstance(value, list):
                event.custom_participant = []  # Clear existing entries
                for participant in value:
                    event.append("custom_participant", participant)
        elif hasattr(event, key):
            setattr(event, key, value)

    # Save changes to the database
    event.save(ignore_permissions=True)
    frappe.db.commit()  # Ensure the changes are saved

    # Return confirmation message with updated event details
    return {"message": "Event updated successfully", "event_name": event.name}



@staticmethod
def custom_event_default_list_data():
    columns = [
        {
            'label': 'Event Category',
            'type': 'Data',
            'key': 'event_category',
            'width': '8rem',
        },
        {
            'label': 'Subject',
            'type': 'Link',
            'key': 'subject',
            'width': '10rem',
        },
        {
            'label': 'Starts On',
            'type': 'Data',
            'key': 'starts_on',
            'width': '12rem',
        },
        {
            'label': 'Ends On',
            'type': 'Data',
            'key': 'ends_on',
            'width': '12rem',
        },
        {
            'label': 'Owner',
            'type': 'Data',
            'key': 'owner',
            'width': '12rem',
        },   


        # {
        #     'label': 'Last Modified',
        #     'type': 'Datetime',
        #     'key': 'modified',
        #     'width': '8rem',
        # },
    ]
    rows = [
        "name",
        "subject",
        "organization",
        "event_category",
        "starts_on",
        "ends_on",
        "modified",
    ]
    return {'columns': columns, 'rows': rows}



@frappe.whitelist()
def custom_get_data(
    doctype: str,
    filters: dict,
    order_by: str,
    page_length=20,
    page_length_count=20,
    column_field=None,
    title_field=None,
    columns=[],
    rows=[],
    kanban_columns=[],
    kanban_fields=[],
    view=None,
    default_filters=None,
):
    custom_view = False
    filters = frappe._dict(filters)
    rows = frappe.parse_json(rows or "[]")
    columns = frappe.parse_json(columns or "[]")
    kanban_fields = frappe.parse_json(kanban_fields or "[]")
    kanban_columns = frappe.parse_json(kanban_columns or "[]")

    custom_view_name = view.get('custom_view_name') if view else None
    view_type = view.get('view_type') if view else None
    group_by_field = view.get('group_by_field') if view else None

    for key in filters:
        value = filters[key]
        if isinstance(value, list):
            if "@me" in value:
                value[value.index("@me")] = frappe.session.user
            elif "%@me%" in value:
                index = [i for i, v in enumerate(value) if v == "%@me%"]
                for i in index:
                    value[i] = "%" + frappe.session.user + "%"
        elif value == "@me":
            filters[key] = frappe.session.user

    if default_filters:
        default_filters = frappe.parse_json(default_filters)
        filters.update(default_filters)

    is_default = True
    data = []
    _list = get_controller(doctype)
    default_rows = []
    if hasattr(_list, "custom_event_default_list_data"):
        default_rows = custom_event_default_list_data().get("rows")

    if view_type != "kanban":
        if columns or rows:
            custom_view = True
            is_default = False
            columns = frappe.parse_json(columns)
            rows = frappe.parse_json(rows)

        if not columns:
            columns = [
                {"label": "Name", "type": "Data", "key": "name", "width": "16rem"},
                {"label": "Last Modified", "type": "Datetime", "key": "modified", "width": "8rem"},
            ]

        if not rows:
            rows = ["name"]

        default_view_filters = {
            "dt": doctype,
            "type": view_type or 'list',
            "is_default": 1,
            "user": frappe.session.user,
        }

        if not custom_view and frappe.db.exists("CRM View Settings", default_view_filters):
            list_view_settings = frappe.get_doc("CRM View Settings", default_view_filters)
            columns = frappe.parse_json(list_view_settings.columns)
            rows = frappe.parse_json(list_view_settings.rows)
            is_default = False
        elif not custom_view or is_default and hasattr(_list, "custom_event_default_list_data"):
            rows = default_rows
            columns = custom_event_default_list_data().get("columns")

        # check if rows has all keys from columns if not add them
        for column in columns:
            if column.get("key") not in rows:
                rows.append(column.get("key"))
            column["label"] = _(column.get("label"))

            if column.get("key") == "_liked_by" and column.get("width") == "10rem":
                column["width"] = "50px"

        # check if rows has group_by_field if not add it
        if group_by_field and group_by_field not in rows:
            rows.append(group_by_field)

        data = frappe.get_list(
            doctype,
            fields=rows,
            filters=filters,
            order_by=order_by,
            page_length=page_length,
        ) or []

    if view_type == "kanban":
        if not rows:
            rows = default_rows

        if not kanban_columns and column_field:
            field_meta = frappe.get_meta(doctype).get_field(column_field)
            if field_meta.fieldtype == "Link":
                kanban_columns = frappe.get_all(
                    field_meta.options,
                    fields=["name"],
                    order_by="modified asc",
                )
            elif field_meta.fieldtype == "Select":
                kanban_columns = [{"name": option} for option in field_meta.options.split("\n")]

        if not title_field:
            title_field = "name"
            if hasattr(_list, "default_kanban_settings"):
                title_field = _list.default_kanban_settings().get("title_field")

        if title_field not in rows:
            rows.append(title_field)

        if not kanban_fields:
            kanban_fields = ["name"]
            if hasattr(_list, "default_kanban_settings"):
                kanban_fields = json.loads(_list.default_kanban_settings().get("kanban_fields"))

        for field in kanban_fields:
            if field not in rows:
                rows.append(field)

        for kc in kanban_columns:
            column_filters = { column_field: kc.get('name') }
            order = kc.get("order")
            if column_field in filters and filters.get(column_field) != kc.name or kc.get('delete'):
                column_data = []
            else:
                column_filters.update(filters.copy())
                page_length = 20

                if kc.get("page_length"):
                    page_length = kc.get("page_length")

                if order:
                    column_data = get_records_based_on_order(doctype, rows, column_filters, page_length, order)
                else:
                    column_data = frappe.get_list(
                        doctype,
                        fields=rows,
                        filters=convert_filter_to_tuple(doctype, column_filters),
                        order_by=order_by,
                        page_length=page_length,
                    )

                new_filters = filters.copy()
                new_filters.update({ column_field: kc.get('name') })

                all_count = len(frappe.get_list(doctype, filters=convert_filter_to_tuple(doctype, new_filters)))

                kc["all_count"] = all_count
                kc["count"] = len(column_data)

                for d in column_data:
                    getCounts(d, doctype)

            if order:
                column_data = sorted(
                    column_data, key=lambda x: order.index(x.get("name"))
                    if x.get("name") in order else len(order)
                )

            data.append({"column": kc, "fields": kanban_fields, "data": column_data})

    # fields = frappe.get_meta(doctype).fields
    # print("-------------------------------------------", fields)
    # #fields = ["subject", "event_category", "event_type", "custom_color", "repeat_this_event", "starts_on", "ends_on", "status", "sync_with_google_calendar", "description"]

    # fields = [field for field in fields if field.fieldtype not in no_value_fields]
    # fields = [
    #     {
    #         "label": _(field.label),
    #         "type": field.fieldtype,
    #         "value": field.fieldname,
    #         "options": field.options,
    #     }
    #     for field in fields
    #     if field.label and field.fieldname
    # ]

    # std_fields = [
    #     {"label": "Name", "type": "Data", "value": "name"},
    #     {"label": "Created On", "type": "Datetime", "value": "creation"},
    #     {"label": "Last Modified", "type": "Datetime", "value": "modified"},
    #     {
    #         "label": "Modified By",
    #         "type": "Link",
    #         "value": "modified_by",
    #         "options": "User",
    #     },
    #     {"label": "Owner", "type": "Link", "value": "owner", "options": "User"},
    #     {"label": "Like", "type": "Data", "value": "_liked_by"},
    # ]

    # for field in std_fields:
    #     if field.get('value') not in rows:
    #         rows.append(field.get('value'))
    #     if field not in fields:
    #         field["label"] = _(field["label"])
    #         fields.append(field)

    # List of specific field names you want to retrieve
    selected_fieldnames = ["subject", "event_category", "event_type", "custom_color", 
                           "repeat_this_event", "starts_on", "ends_on", "status", 
                           "sync_with_google_calendar", "description"]

    # Get all fields for the doctype
    all_fields = frappe.get_meta(doctype).fields

    # Filter to include only selected fields
    fields = [
        {
            "label": _(field.label),
            "type": field.fieldtype,
            "value": field.fieldname,
            "options": field.options,
        }
        for field in all_fields
        if field.fieldname in selected_fieldnames and field.fieldtype not in no_value_fields
    ]

    # Add standard fields if they’re not already in `fields`
    std_fields = [
        {"label": "Name", "type": "Data", "value": "name"},
        {"label": "Created On", "type": "Datetime", "value": "creation"},
        {"label": "Last Modified", "type": "Datetime", "value": "modified"},
        {
            "label": "Modified By",
            "type": "Link",
            "value": "modified_by",
            "options": "User",
        },
        {"label": "Owner", "type": "Link", "value": "owner", "options": "User"},
        {"label": "Like", "type": "Data", "value": "_liked_by"},
    ]

    for field in std_fields:
        if field.get("value") not in rows:
            rows.append(field.get("value"))
        # Append standard fields only if they are not already in fields
        if all(f.get("value") != field["value"] for f in fields):
            field["label"] = _(field["label"])
            fields.append(field)


    if not is_default and custom_view_name:
        is_default = frappe.db.get_value("CRM View Settings", custom_view_name, "load_default_columns")

    if group_by_field and view_type == "group_by":
        def get_options(type, options):
            if type == "Select":
                return [option for option in options.split("\n")]
            else:
                has_empty_values = any([not d.get(group_by_field) for d in data])
                options = list(set([d.get(group_by_field) for d in data]))
                options = [u for u in options if u]
                if has_empty_values:
                    options.append("")

                if order_by and group_by_field in order_by:
                    order_by_fields = order_by.split(",")
                    order_by_fields = [(field.split(" ")[0], field.split(" ")[1]) for field in order_by_fields]
                    if (group_by_field, "asc") in order_by_fields:
                        options.sort()
                    elif (group_by_field, "desc") in order_by_fields:
                        options.sort(reverse=True)
                else:
                    options.sort()
                return options

        for field in fields:
            if field.get("value") == group_by_field:
                group_by_field = {
                    "label": field.get("label"),
                    "name": field.get("value"),
                    "type": field.get("type"),
                    "options": get_options(field.get("type"), field.get("options")),
                }

    return {
        "data": data,
        "columns": columns,
        "rows": rows,
        "fields": fields,
        "column_field": column_field,
        "title_field": title_field,
        "kanban_columns": kanban_columns,
        "kanban_fields": kanban_fields,
        "group_by_field": group_by_field,
        "page_length": page_length,
        "page_length_count": page_length_count,
        "is_default": is_default,
        "views": get_views(doctype),
        "total_count": len(frappe.get_list(doctype, filters=filters)),
        "row_count": len(data),
        "form_script": get_form_script(doctype),
        "list_script": get_form_script(doctype, "List"),
        "view_type": view_type,
    }






import frappe
import csv
from frappe.utils import get_site_path

@frappe.whitelist()
def export_data(doctype):
    """Exports data from the specified Doctype and returns the file path."""
    
    # Check if the Doctype exists
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(f"Doctype '{doctype}' does not exist", frappe.DoesNotExistError)
    
    # Get all fields dynamically
    meta = frappe.get_meta(doctype)
    all_fields = [df.fieldname for df in meta.fields]

    # Ensure only valid fields are used
    valid_fields = [field for field in all_fields if frappe.db.has_column(doctype, field)]

    # Fetch all data
    records = frappe.get_all(doctype, fields=valid_fields)

    # Define file path (Public for easy access)
    file_path = get_site_path("public", "files", f"{doctype}_export.csv")

    # Write data to CSV
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(valid_fields)  # Write headers
        for record in records:
            writer.writerow([record.get(field) for field in valid_fields])

    return f"/public/files/{doctype}_export.csv"  # Public file URL



import frappe
import csv
import time
import re
from frappe.utils import get_site_path

# Function to remove HTML tags
def strip_html(text):
    """Removes HTML tags from a string."""
    if not text:
        return ""
    return re.sub(r"<.*?>", "", text)

@frappe.whitelist()
def export_data_all(doctype, filters=None):
    """Exports data from the specified Doctype with optional filters and returns a unique file path."""

    # Check if Doctype exists
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(f"Doctype '{doctype}' does not exist", frappe.DoesNotExistError)

    # Replace spaces with underscores in filename
    safe_doctype = doctype.replace(" ", "_")

    # Generate unique timestamp-based filename
    timestamp = int(time.time())  # Current timestamp in seconds
    filename = f"{safe_doctype}_export_{timestamp}.csv"

    # Get all fields dynamically
    meta = frappe.get_meta(doctype)
    all_fields = [df.fieldname for df in meta.fields]

    # Validate fields
    valid_fields = [field for field in all_fields if frappe.db.has_column(doctype, field)]

    # Convert filters from JSON string (if coming from API call)
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    # Fetch data with optional filters
    records = frappe.get_all(doctype, fields=valid_fields, filters=filters or {})

    # Define file path
    file_path = get_site_path("public", "files", filename)

    # Write data to CSV
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(valid_fields)  # Write headers

        for record in records:
            cleaned_record = [strip_html(str(record.get(field))) for field in valid_fields]
            writer.writerow(cleaned_record)

    return f"/public/files/{filename}"
