# Copyright (c) 2025, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.model.rename_doc import rename_doc
from frappe.utils import nowdate, nowtime
from erpnext.stock.stock_ledger import make_sl_entries


class NegativeStockCorrection(Document):
	def on_submit(self):
		self.update_stock_ledger()

	def update_stock_ledger(self):
		original_item_settings = []
		try:
			# Temporarily update item masters to bypass serial/batch validation
			for item in self.items:
				original_settings = frappe.db.get_value("Item", item.item_code, ["has_serial_no", "has_batch_no"], as_dict=1)
				if original_settings and (original_settings.has_serial_no or original_settings.has_batch_no):
					original_item_settings.append({
						"item_code": item.item_code,
						"has_serial_no": original_settings.has_serial_no,
						"has_batch_no": original_settings.has_batch_no
					})
					frappe.db.set_value("Item", item.item_code, {"has_serial_no": 0, "has_batch_no": 0}, update_modified=False)
			
			if original_item_settings:
				frappe.clear_cache(doctype="Item")

			# Prepare and create Stock Ledger Entries
			sl_entries = []
			for item in self.items:
				sle_dict = frappe._dict({
					"doctype": "Stock Ledger Entry",
					"item_code": item.item_code,
					"warehouse": item.warehouse,
					"posting_date": self.posting_date,
					"posting_time": self.posting_time,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
					"voucher_detail_no": item.name,
					"actual_qty": item.qty,
					"stock_uom": frappe.get_value('Item', item.item_code, 'stock_uom'),
					"incoming_rate": 0,
					"company": self.company,
					"is_adjustment_entry": 1,
					"fiscal_year": frappe.get_cached_value('Global Defaults', None, 'current_fiscal_year'),
				})
				sl_entries.append(sle_dict)

			make_sl_entries(sl_entries, allow_negative_stock=True)

			# Manually rename the created SLEs to use the standard naming series
			created_sles = frappe.get_all("Stock Ledger Entry",
				filters={"voucher_type": self.doctype, "voucher_no": self.name, "is_cancelled": 0},
				pluck="name")

			for sle_name in created_sles:
				if not sle_name.startswith("MAT-SLE"):
					new_name = make_autoname('MAT-SLE-.YYYY.-.#####', 'Stock Ledger Entry')
					rename_doc("Stock Ledger Entry", sle_name, new_name, ignore_permissions=True)
		finally:
			# Restore original item settings
			for settings in original_item_settings:
				frappe.db.set_value("Item", settings["item_code"], {
					"has_serial_no": settings["has_serial_no"],
					"has_batch_no": settings["has_batch_no"]
				}, update_modified=False)
			
			if original_item_settings:
				frappe.clear_cache(doctype="Item")


	def on_cancel(self):
		original_item_settings = []
		try:
			# Temporarily update item masters to bypass serial/batch validation
			for item in self.items:
				original_settings = frappe.db.get_value("Item", item.item_code, ["has_serial_no", "has_batch_no"], as_dict=1)
				if original_settings and (original_settings.has_serial_no or original_settings.has_batch_no):
					original_item_settings.append({
						"item_code": item.item_code,
						"has_serial_no": original_settings.has_serial_no,
						"has_batch_no": original_settings.has_batch_no
					})
					frappe.db.set_value("Item", item.item_code, {"has_serial_no": 0, "has_batch_no": 0}, update_modified=False)
			
			if original_item_settings:
				frappe.clear_cache(doctype="Item")

			sl_entries = []
			for item in self.items:
				sle_dict = frappe._dict({
					"doctype": "Stock Ledger Entry",
					"item_code": item.item_code,
					"warehouse": item.warehouse,
					"posting_date": self.posting_date,
					"posting_time": self.posting_time,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
					"voucher_detail_no": item.name,
					"actual_qty": -1 * item.qty,  # Reverse the quantity
					"stock_uom": frappe.get_value('Item', item.item_code, 'stock_uom'),
					"incoming_rate": 0,
					"company": self.company,
					"is_adjustment_entry": 1,
					"fiscal_year": frappe.get_cached_value('Global Defaults', None, 'current_fiscal_year'),
				})
				sl_entries.append(sle_dict)

			make_sl_entries(sl_entries, allow_negative_stock=True)
		finally:
			# Restore original item settings
			for settings in original_item_settings:
				frappe.db.set_value("Item", settings["item_code"], {
					"has_serial_no": settings["has_serial_no"],
					"has_batch_no": settings["has_batch_no"]
				}, update_modified=False)
			
			if original_item_settings:
				frappe.clear_cache(doctype="Item")
