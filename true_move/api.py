import frappe

from true_move.permissions import MOVER_ROLE


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def search_movers(doctype: str, txt: str, searchfield: str, start: int, page_len: int, filters: dict | None = None):
	"""Поиск для поля «Грузчик»: только активные пользователи с ролью «Грузчик»."""
	user = frappe.qb.DocType("User")
	has_role = frappe.qb.DocType("Has Role")
	like = f"%{txt}%"
	return (
		frappe.qb.from_(user)
		.join(has_role)
		.on((has_role.parent == user.name) & (has_role.parenttype == "User"))
		.select(user.name, user.full_name)
		.where((has_role.role == MOVER_ROLE) & (user.enabled == 1))
		.where(user.name.like(like) | user.full_name.like(like))
		.distinct()
		.orderby(user.full_name)
		.limit(page_len)
		.offset(start)
		.run()
	)
