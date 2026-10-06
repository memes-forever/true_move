"""Серверные обработчики CRM Deal."""


def drop_empty_move_items(doc, method=None):
	"""CRM Deal.before_validate: убрать пустые строки Inventory.

	В Vue-интерфейсе CRM таблица сохраняется целиком, и случайно добавленная пустая строка
	(Add Row без названия предмета) валила сохранение по обязательному item_name — вместе
	с остальными правками, например удалением строк. before_validate идёт до проверки обязательных полей.
	"""
	items = doc.get("custom_move_items") or []
	filled = [row for row in items if (row.item_name or "").strip()]
	if len(filled) != len(items):
		for idx, row in enumerate(filled, start=1):
			row.idx = idx
		doc.set("custom_move_items", filled)
