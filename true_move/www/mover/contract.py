import frappe
from frappe.utils import format_datetime

no_cache = 1


def get_context(context):
	name = frappe.form_dict.get("name")
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = f"/login?redirect-to=/mover/contract?name={name or ''}"
		raise frappe.Redirect

	if not name:
		frappe.local.flags.redirect_location = "/mover"
		raise frappe.Redirect

	doc = frappe.get_doc("Contract", name)
	doc.check_permission("read")  # чужой контракт → 403

	context.doc = doc
	context.move_date_display = format_datetime(doc.move_date, "dd.MM.yyyy HH:mm")
	context.amount_display = doc.get_formatted("amount")
	context.manager = frappe.db.get_value("User", doc.manager, ["full_name", "mobile_no"], as_dict=True)
	context.title = doc.customer_name or doc.name
	context.show_sidebar = False
