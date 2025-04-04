# Copyright (c) 2025, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SortJSON(Document):
	pass

@frappe.whitelist()
def sort_json(json_data):
	"""
	Sorts the given JSON data by 'dt' (Doctype) and 'name' if applicable.
	"""
	if isinstance(json_data, str):
		json_data = frappe.parse_json(json_data)
		
	if isinstance(json_data, list):
		json_data.sort(key=lambda x: (x.get("name", "")))

	json_data = frappe.as_json(json_data, indent=4, ensure_ascii=False)
	return json_data