// Copyright (c) 2025, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Get Pull Requests from Github", {
    get_pull_requests(frm) {
        console.log('get_pull_requests');

        frappe.msgprint('Fetching pull requests from Github...');
        
        frappe.call({
            method: 'phamos_utils.phamos_utils.doctype.get_pull_requests_from_github.get_pull_requests_from_github.fetch_pull_requests',
            callback: (response) => {
                frm.reload_doc();
                frappe.msgprint('Pull requests fetched successfully.');
            }
        });    
    }
});
