import frappe

from true_move.true_move.doctype.mover.mover import MOVER_ROLE, sync_mover_for_user


def execute():
	"""Создать записи Mover для пользователей, получивших роль Mover до появления автосинхронизации."""
	users = frappe.get_all("Has Role", filters={"role": MOVER_ROLE, "parenttype": "User"}, pluck="parent", distinct=True)
	for user in users:
		sync_mover_for_user(frappe.get_doc("User", user))
