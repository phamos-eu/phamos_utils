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

@frappe.whitelist()
def export_fixtures_and_sort_them():
	"""
	Exports all fixtures from all apps in the apps folder and sorts them by 'dt' (Doctype) and 'name' if applicable.
	"""
	import os
	import json

	sorted_fixtures = []

	# Path to the apps folder
	apps_folder = os.path.abspath(os.path.join(frappe.get_app_path("frappe"), "..", ".."))

	print(f"Apps folder: {apps_folder}")

	# Iterate through all apps in the apps folder
	for app_name in os.listdir(apps_folder):
		app_path = os.path.join(apps_folder, app_name)
		fixtures_folder = os.path.join(app_path, app_name, "fixtures")
		print(f"Fixtures folder: {fixtures_folder}")

		# Check if the fixtures folder exists in the app
		if os.path.exists(fixtures_folder) and os.path.isdir(fixtures_folder):
			# Iterate through all JSON files in the fixtures folder
			for file_name in os.listdir(fixtures_folder):
				print(f"Fixture file: {file_name}")
				if file_name.endswith(".json"):
					file_path = os.path.join(fixtures_folder, file_name)
					with open(file_path, "r", encoding="utf-8") as f:
						fixture_data = json.load(f)
						sorted_data = sort_json(fixture_data)
						sorted_fixtures.append(sorted_data)

						# Save the sorted data back to the file
						with open(file_path, "w", encoding="utf-8") as f:
							f.write(sorted_data)
					frappe.msgprint(f"Sorted fixture file: {file_path}")
