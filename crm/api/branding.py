# your_app/api/branding.py
import frappe


@frappe.whitelist()
def get_branding():
    app_org = frappe.conf.get("app_org", "default")
    dynamic_favicon_key = f"{app_org}_app_favicon"

    return {
        "title": frappe.conf.get("app_title", "Default App"),
        "logo": frappe.conf.get("app_logo", "/assets/crm/manifest/default-logo.png"),
        "favicon": frappe.conf.get(dynamic_favicon_key) or frappe.conf.get("app_favicon", "/assets/crm/manifest/default-favicon.png"),
        "appOrg": app_org,
    }
