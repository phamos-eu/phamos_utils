// Copyright (c) 2025, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sort JSON", {
	refresh(frm) {

	},

    sort_json: function(frm) {
        frappe.call({
            method: "phamos_utils.phamos_utils.doctype.sort_json.sort_json.sort_json",
            args: {
                json_data: frm.doc.input_json
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("sorted", r.message);
                }
            }
        });
    }
});
