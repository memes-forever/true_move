# Copyright (c) 2026, True Move and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

MOVER_ROLE = "Mover"


class Mover(Document):
	def validate(self):
		if self.user and MOVER_ROLE not in frappe.get_roles(self.user):
			frappe.throw(_("User {0} does not have the {1} role").format(self.user, MOVER_ROLE))


def sync_mover_for_user(user, method=None):
	"""User.on_update: у пользователя с ролью Mover всегда есть активная запись Mover,
	без роли — запись отключается (не удаляется: на неё ссылаются сделки)."""
	has_role = MOVER_ROLE in {r.role for r in user.get("roles", [])}
	mover = frappe.db.get_value("Mover", {"user": user.name}, ["name", "enabled"], as_dict=True)

	if has_role and not mover:
		full_name = user.full_name or user.name
		if frappe.db.exists("Mover", full_name):
			full_name = f"{full_name} ({user.name})"
		frappe.get_doc(
			{"doctype": "Mover", "full_name": full_name, "phone": user.mobile_no, "user": user.name}
		).insert(ignore_permissions=True)
	elif mover and mover.enabled != has_role:
		frappe.db.set_value("Mover", mover.name, "enabled", int(has_role))


def unlink_mover_from_user(user, method=None):
	"""User.on_trash: отвязать запись Mover, чтобы пользователя можно было удалить."""
	for name in frappe.get_all("Mover", filters={"user": user.name}, pluck="name"):
		frappe.db.set_value("Mover", name, {"user": None, "enabled": 0})


def get_session_movers() -> list[str]:
	"""Записи Mover, привязанные к текущему пользователю."""
	return frappe.get_all("Mover", filters={"user": frappe.session.user, "enabled": 1}, pluck="name")
