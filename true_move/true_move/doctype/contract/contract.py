# Copyright (c) 2026, True Move and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from true_move.permissions import MOVER_ROLE


class Contract(Document):
	def validate(self):
		self.validate_mover()

	def validate_mover(self):
		if self.mover and MOVER_ROLE not in frappe.get_roles(self.mover):
			frappe.throw(_("Пользователь {0} не является грузчиком").format(self.mover))
