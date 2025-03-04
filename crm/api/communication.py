import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from frappe.utils.password import update_password
import json
from frappe.model.document import get_controller
from frappe.model import no_value_fields
from pypika import Criterion
from frappe.utils import make_filter_tuple

from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from frappe.utils.password import get_decrypted_password
from frappe.query_builder import Table
from bs4 import BeautifulSoup


def strip_html(html_content):
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        return " ".join(soup.get_text().split())
    return ""

@frappe.whitelist()
def change_password(new_password: str, confirm_password: str, old_password: str = None):
    # Validate that new and confirm passwords are provided
    if not new_password or not confirm_password:
        return {"status": "error", "message": "New password and confirm password fields cannot be empty."}

    # Check if new password matches confirm password
    if new_password != confirm_password:
        return {"status": "error", "message": "The new password and confirm password do not match."}

    try:
        user = frappe.session.user

        # Ensure the user exists
        if not frappe.db.exists("User", user):
            return {"status": "error", "message": f"User '{user}' does not exist."}

        # Validate the old password if provided
        if old_password:
            from frappe.utils.password import check_password
            try:
                check_password(user, old_password)
            except frappe.exceptions.AuthenticationError:
                return {"status": "error", "message": "The old password is incorrect."}

        # Update the password
        update_password(user, new_password)

        return {"status": "success", "message": f"Password for user '{user}' has been updated successfully."}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Change Password Error")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}


Auth = Table("__Auth")


@frappe.whitelist()
def is_password_set():

    user = frappe.session.user
    user_email = frappe.db.get_value("User", user, "email")

    try:
        result = (
            frappe.qb.from_(Auth)
            .select(Auth.password)
            .where(
                (Auth.doctype == 'User')
                & (Auth.name == user_email)
                & (Auth.fieldname == "password")
            )
            .limit(1)
        ).run()
        
        if result:
            return {
                "status": "success",
                "is_password_set": True,
                "message": "Password is set for this user."
            }
        else:
            return {
                "status": "success",
                "is_password_set": False,
                "message": "No password is set or user is disabled."
            }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check Password Status Error")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}


@staticmethod
def custom_communication_default_list_data():
    columns = [

        {
            'label': 'Email Date',
            'type': 'Data',
            'key': 'communication_date',
            'width': '8rem',
        },
        {
            'label': 'Sender',
            'type': 'Data',
            'key': 'sender',
            'width': '8rem',
        },
        {
            'label': 'Recipients',
            'type': 'Data',
            'key': 'recipients',
            'width': '8rem',
        },

        {
            'label': 'Subject',
            'type': 'Data',
            'key': 'subject',
            'width': '10rem',
        },
        {
            'label': 'Content',
            'type': 'Data',
            'key': 'content',
            'width': '8rem',
        },
        

        

        # {
        #     'label': 'Cc',
        #     'type': 'Data',
        #     'key': 'cc',
        #     'width': '8rem',
        # },

        # {
        #     'label': 'Bcc',
        #     'type': 'Data',
        #     'key': 'bcc',
        #     'width': '8rem',
        # },

        


        # {
        #     'label': 'Last Modified',
        #     'type': 'Datetime',
        #     'key': 'modified',
        #     'width': '8rem',
        # },
    ]
    rows = [
        # "name",
        "subject",
        "content",
        "sender",
        # "recipients",
        # "cc",
        # "bcc",
        "communication_date",
        "modified",
    ]
    return {'columns': columns, 'rows': rows}



@frappe.whitelist()
def get_communication_data(
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
    if hasattr(_list, "custom_communication_default_list_data"):
        default_rows = custom_communication_default_list_data().get("rows")

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
        elif not custom_view or is_default and hasattr(_list, "custom_communication_default_list_data"):
            rows = default_rows
            columns = custom_communication_default_list_data().get("columns")

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


        user_email = frappe.session.user
        if user_email == "Guest":
            return {"status": "error", "message": "Guest users cannot retrieve communications."}

        user_email = user_email.lower()
        # Construct the SQL query with OR conditions for sender, recipients, cc, or bcc
        query = """
            SELECT name, subject, content, sender, recipients, cc, bcc, communication_date
            FROM `tabCommunication`
            WHERE LOWER(sender) LIKE %s
            OR LOWER(recipients) LIKE %s
            OR LOWER(cc) LIKE %s
            OR LOWER(bcc) LIKE %s
            ORDER BY communication_date DESC
        """
        communications = frappe.db.sql(
            query, 
            (f"%{user_email}%", f"%{user_email}%", f"%{user_email}%", f"%{user_email}%"), 
            as_dict=True
        )
        #return communications

        

        for comm in communications:
            comm["content"] = strip_html(comm["content"])

        data = communications

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

    fields = frappe.get_meta(doctype).fields
    fields = [field for field in fields if field.fieldtype not in no_value_fields]
    fields = [
        {
            "label": _(field.label),
            "type": field.fieldtype,
            "value": field.fieldname,
            "options": field.options,
        }
        for field in fields
        if field.label and field.fieldname
    ]

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
        {"label": "Assigned To", "type": "Link", "value": "_assign", "options": "User"},
        {"label": "Owner", "type": "Link", "value": "owner", "options": "User"},
        {"label": "Like", "type": "Data", "value": "_liked_by"},
    ]

    for field in std_fields:
        if field.get('value') not in rows:
            rows.append(field.get('value'))
        if field not in fields:
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

@frappe.whitelist()
def custom_get_communication_details(name):
    # Fetch Communication details
    Communication = frappe.qb.DocType("Communication")

    # Query Communication details
    communication_query = frappe.qb.from_(Communication).select("*").where(Communication.name == name).limit(1)
    communication = communication_query.run(as_dict=True)
    
    if not communication:
        frappe.throw(_("Communication not found"), frappe.DoesNotExistError)
    
    communication = communication[0]
    communication["doctype"] = "Communication"

    return communication


@frappe.whitelist()
def is_twilio_set():
    try:
        # Fetch the value of 'auth_token' from tabSingles for 'Twilio Settings'
        auth_token = frappe.db.get_single_value("Twilio Settings", "auth_token")
        account_sid = frappe.db.get_single_value("Twilio Settings", "account_sid")
        api_key = frappe.db.get_single_value("Twilio Settings", "api_key")
        api_secret = frappe.db.get_single_value("Twilio Settings", "api_secret")

        if auth_token and account_sid and api_key and api_secret:
            return {
                "status": "success",
                "is_twilio_set": True,
                "message": "Twilio is set."
            }
        else:
            return {
                "status": "error",
                "is_twilio_set": False,
                "message": "No credentials are set for Twilio."
            }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Twilio Error")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}


@frappe.whitelist()
def custom_edit_company(name, **kwargs):
    # Fetch the company document by name (ID)
    company = frappe.get_doc("Company", name)

    # Update main fields with the data provided in kwargs
    for key, value in kwargs.items():
        if hasattr(company, key):
            setattr(company, key, value)

    # Save changes to the database
    company.save(ignore_permissions=True)
    frappe.db.commit()  # Ensure the changes are saved

    # Return confirmation message with updated company details
    return {"message": " Company details updated successfully", "company_name": company.name}