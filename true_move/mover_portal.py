"""Общий код страниц грузчика (www/moves).

У роли Mover нет прав на CRM Deal, поэтому данные читаются без проверки прав,
но строго по сделкам, где назначен грузчик текущего пользователя.
"""

import frappe
from frappe.utils import format_datetime

from true_move.true_move.doctype.mover.mover import MOVER_ROLE, get_session_movers


def require_login(redirect_to: str):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = f"/login?redirect-to={redirect_to}"
		raise frappe.Redirect


def has_app_permission() -> bool:
	"""Плитка Moves на /desk: грузчикам и администраторам."""
	return bool({MOVER_ROLE, "System Manager"} & set(frappe.get_roles()))


def get_status_colors() -> dict[str, str]:
	return dict(frappe.get_all("CRM Deal Status", fields=["name", "color"], as_list=True))


def get_lost_statuses() -> list[str]:
	return frappe.get_all("CRM Deal Status", filters={"type": "Lost"}, pluck="name")


def get_customer(deal) -> frappe._dict:
	"""Основной контакт сделки: имя и телефон."""
	contacts = deal.get("contacts") or []
	primary = next((c for c in contacts if c.is_primary), contacts[0] if contacts else None)
	if primary:
		return frappe._dict(name=primary.full_name, phone=primary.mobile_no or primary.phone)
	name = " ".join(filter(None, [deal.get("first_name"), deal.get("last_name")]))
	return frappe._dict(name=name or deal.get("lead_name"), phone=deal.get("mobile_no") or deal.get("phone"))


def format_move_date(value) -> str:
	return format_datetime(value, "MM/dd/yyyy h:mm a") if value else "Date not set"


