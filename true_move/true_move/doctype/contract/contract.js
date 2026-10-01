// Copyright (c) 2026, True Move and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract", {
	setup(frm) {
		frm.set_query("mover", () => ({ query: "true_move.api.search_movers" }));
	},
});
