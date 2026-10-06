import frappe

from true_move.mover_portal import (
	format_move_date,
	get_customer,
	get_session_movers,
	get_status_colors,
	require_login,
)

no_cache = 1


def get_context(context):
	name = frappe.form_dict.get("name") or ""
	require_login(f"/moves/deal?name={name}")

	if not name:
		frappe.local.flags.redirect_location = "/moves"
		raise frappe.Redirect

	doc = frappe.get_doc("CRM Deal", name)
	if not doc.custom_mover or doc.custom_mover not in get_session_movers():
		raise frappe.PermissionError

	context.doc = doc
	context.customer = get_customer(doc)
	context.move_date_display = format_move_date(doc.custom_move_date)
	context.status_color = get_status_colors().get(doc.status, "gray")
	context.amount_display = doc.get_formatted("deal_value") if doc.deal_value else None
	context.manager = frappe.db.get_value("User", doc.deal_owner, ["full_name", "mobile_no"], as_dict=True)
	context.title = context.customer.name or doc.name
	context.show_sidebar = False
