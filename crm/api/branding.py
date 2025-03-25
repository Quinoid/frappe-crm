# your_app/api/branding.py
import frappe


@frappe.whitelist()
def get_branding():
    return {
        "title": frappe.conf.get("app_title", "Default App"),
        "favicon": frappe.conf.get("app_favicon", "/assets/crm/apple-icon-1802.png"),
        "logo": frappe.conf.get("app_logo", "/assets/crm/apple-icon-1802.png"),

    }
