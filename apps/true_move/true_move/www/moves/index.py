import frappe
from frappe.utils import getdate, today

from true_move.mover_portal import (
	format_move_date,
	get_customer,
	get_lost_statuses,
	get_session_movers,
	get_status_colors,
	require_login,
)

no_cache = 1


def get_context(context):
	require_login("/moves")

	context.title = "Мои переезды"
	context.show_sidebar = False
	context.upcoming, context.past = [], []

	movers = get_session_movers()
	if not movers:
		return

	filters = {"custom_mover": ["in", movers]}
	if lost := get_lost_statuses():
		filters["status"] = ["not in", lost]

	deals = frappe.get_all(
		"CRM Deal",
		filters=filters,
		fields=["name", "status", "custom_move_date", "custom_from_address", "custom_to_address",
			"first_name", "last_name", "lead_name", "mobile_no", "phone"],
		order_by="custom_move_date asc",
	)
	colors = get_status_colors()
	start_of_today = getdate(today())

	for deal in deals:
		deal.contacts = frappe.get_all("CRM Contacts", filters={"parent": deal.name, "parenttype": "CRM Deal"},
			fields=["full_name", "mobile_no", "phone", "is_primary"])
		deal.customer = get_customer(deal)
		deal.move_date_display = format_move_date(deal.custom_move_date)
		deal.status_color = colors.get(deal.status, "gray")
		is_past = deal.custom_move_date and getdate(deal.custom_move_date) < start_of_today
		(context.past if is_past else context.upcoming).append(deal)

	context.past = list(reversed(context.past))[:20]
