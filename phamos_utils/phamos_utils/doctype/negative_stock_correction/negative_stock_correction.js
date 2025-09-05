// Copyright (c) 2025, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Project Configuration", {
    refresh(frm) {
        apply_filters_to_documents_to_submit(frm)
    },
});

var apply_filters_to_documents_to_submit = function (frm) {
    frm.set_query("doctype_to_submit", "documents_to_submit", function () {
        return {
            filters: {
                name: ["in", ["Sales Order", "Purchase Order", "ProMa Checklist", "Quotation"]]
            }
        };
    });
}