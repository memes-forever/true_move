import frappe

MOVER_ROLE = "Грузчик"

# У этих ролей полный доступ к контрактам; ограничение «только свои» для них не действует
STAFF_ROLES = {"System Manager", "Sales Manager", "Sales User"}


def is_mover_only(user: str | None = None) -> bool:
	user = user or frappe.session.user
	if user == "Administrator":
		return False
	roles = set(frappe.get_roles(user))
	return MOVER_ROLE in roles and not (roles & STAFF_ROLES)


def contract_query_conditions(user: str | None = None) -> str:
	"""Грузчик в списках и отчётах видит только контракты, где он назначен."""
	user = user or frappe.session.user
	if is_mover_only(user):
		return f"`tabContract`.`mover` = {frappe.db.escape(user)}"
	return ""


def contract_has_permission(doc, ptype: str = "read", user: str | None = None) -> bool:
	"""Грузчик может открыть только свой контракт (в т.ч. по прямой ссылке и через API)."""
	user = user or frappe.session.user
	if is_mover_only(user):
		return doc.mover == user
	return True
