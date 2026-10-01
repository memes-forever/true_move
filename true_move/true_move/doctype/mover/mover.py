# Copyright (c) 2026, True Move and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

MOVER_ROLE = "Грузчик"


class Mover(Document):
	def validate(self):
		if self.user and MOVER_ROLE not in frappe.get_roles(self.user):
			frappe.throw(_("У пользователя {0} нет роли «{1}»").format(self.user, MOVER_ROLE))


def get_session_movers() -> list[str]:
	"""Записи «Грузчик», привязанные к текущему пользователю."""
	return frappe.get_all("Mover", filters={"user": frappe.session.user, "enabled": 1}, pluck="name")
