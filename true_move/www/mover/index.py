import frappe
from frappe.utils import format_datetime

no_cache = 1

ACTIVE_STATUSES = ["Черновик", "Подтверждён", "В работе"]


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/mover"
		raise frappe.Redirect

	fields = ["name", "customer_name", "move_date", "status", "from_address", "to_address"]
	user = frappe.session.user

	context.active = frappe.get_list(
		"Contract",
		filters={"mover": user, "status": ["in", ACTIVE_STATUSES]},
		fields=fields,
		order_by="move_date asc",
	)
	context.done = frappe.get_list(
		"Contract",
		filters={"mover": user, "status": "Выполнен"},
		fields=fields,
		order_by="move_date desc",
		limit=20,
	)
	for row in context.active + context.done:
		row.move_date_display = format_datetime(row.move_date, "dd.MM.yyyy HH:mm")

	context.title = "Мои контракты"
	context.show_sidebar = False
