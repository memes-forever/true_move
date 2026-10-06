import frappe


def execute():
	"""Item в Inventory стал ссылкой на справочник Inventory Item: внести в него уже введённые предметы."""
	names = frappe.get_all("Move Item", filters={"item_name": ["is", "set"]}, pluck="item_name", distinct=True)
	for name in {n.strip() for n in names if n.strip()}:
		if not frappe.db.exists("Inventory Item", name):
			frappe.get_doc({"doctype": "Inventory Item", "item_name": name}).insert(ignore_permissions=True)
