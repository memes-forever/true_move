// Desk-форма CRM Deal: кнопка удаления в строке Inventory (в Vue-интерфейсе CRM её обрабатывает CRM Form Script)
frappe.ui.form.on("CRM Deal", {
	refresh(frm) {
		frm.fields_dict.custom_move_items.grid.update_docfield_property("delete_row", "label", "🗑");
	},
});

frappe.ui.form.on("Move Item", {
	delete_row(frm, cdt, cdn) {
		frappe.model.clear_doc(cdt, cdn);
		frm.refresh_field("custom_move_items");
		frm.dirty();
	},
});
