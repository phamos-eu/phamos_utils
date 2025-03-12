// Copyright (c) 2025, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Safe Data Update", {
	refresh(frm) {
        if (frm.doc.status === "Completed") {
            // add button to call the rollback_changes function in the python file
            frm.add_custom_button(__('Rollback Changes'), function() {
                frappe.call({
                    method: 'rollback_changes',
                    doc: frm.doc,
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                        }
                    }
                });
            });
        }
	},
});
