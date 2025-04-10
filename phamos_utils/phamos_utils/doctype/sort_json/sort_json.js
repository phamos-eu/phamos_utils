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
    },

    copy_to_clipboard: function(frm) {
        const sortedJson = frm.doc.sorted;
        if (sortedJson) {
            navigator.clipboard.writeText(sortedJson).then(function() {
                frappe.msgprint({
                    title: __('Success'),
                    message: __('Sorted JSON copied to clipboard.'),
                    indicator: 'green'
                });
            }, function(err) {
                frappe.msgprint({
                    title: __('Error'),
                    message: __('Failed to copy sorted JSON to clipboard.'),
                    indicator: 'red'
                });
            });
        } else {
            frappe.msgprint({
                title: __('Error'),
                message: __('No sorted JSON available to copy.'),
                indicator: 'red'
            });
        }
    },

    export_fixtures_and_sort_them: function(frm) {
        frappe.call({
            method: "phamos_utils.phamos_utils.doctype.sort_json.sort_json.export_fixtures_and_sort_them",
            callback: function(r) {
                frappe.msgprint({
                    title: __('Success'),
                    message: __('Fixtures exported and sorted successfully.'),
                    indicator: 'green'
                });
            }
        });
    }
});
