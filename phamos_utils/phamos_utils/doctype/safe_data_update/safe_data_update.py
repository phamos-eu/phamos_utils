# Copyright (c) 2025, Phamos GmbH and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
import logging
import uuid
import json
from datetime import datetime

class SafeDataUpdate(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger_name = kwargs.get("logger_name", "data_update_runner")
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.backups = []

    def safe_update(self, doc_name, field_name, new_value, update_modified=False):
        """
        Calls frappe.db.set_value after saving a backup.
        """
        try:
            original_value = frappe.db.get_value(self.target_doctype, doc_name, field_name)
            self.backups.append({
                "document_name": doc_name,
                "document_type": self.target_doctype,
                "field_name": field_name,
                "original_value": original_value,
            })

            frappe.db.set_value(self.target_doctype, doc_name, field_name, new_value, update_modified=update_modified)
            self.logger.info(f"Updated {self.target_doctype} {doc_name}, {field_name} set to {new_value}.")
        except Exception as e:
            self.logger.error(f"Error updating {self.target_doctype} {doc_name}, {field_name}: {e}", exc_info=True)
            raise

    def run(self, update_function, **kwargs):
        """
        Executes the update function with backup and rollback.
        """
        data_backup_run_id = str(uuid.uuid4())
        self.run_id = data_backup_run_id
        self.start_time = datetime.now()
        self.status = "Pending"
        self.save()

        try:
            frappe.db.commit()

            update_function(self, **kwargs)
            
            self.data_backup = json.dumps(self.backups)
            self.status = "Completed"
            self.end_time = datetime.now()
            self.save(ignore_permissions=True)
            frappe.db.commit()

            self.logger.info(f"{self.target_doctype} update completed successfully.")

        except Exception as outer_e:
            self.logger.error(f"Error during {self.target_doctype} update: {outer_e}", exc_info=True)
            frappe.db.rollback()
            self.rollback_changes(self.name)
            self.status = "Rolled Back"
            self.end_time = datetime.now()
            self.save(ignore_permissions=True)
            raise

    @frappe.whitelist()
    def rollback_changes(self):
        """
        Rolls back changes using the single Safe Data Update document.
        """
        self.logger.info(f"Starting rollback for document {self.name}...")
        backups = json.loads(self.data_backup)
        for backup in reversed(backups):
            try:
                if backup["original_value"] is not None:
                    frappe.db.set_value(backup["document_type"], backup["document_name"], backup["field_name"], backup["original_value"], update_modified=False)
                else:
                    frappe.db.sql(f"UPDATE `tab{backup['document_type']}` SET `{backup['field_name']}` = NULL WHERE `name` = %s", (backup["document_name"],))
                self.logger.info(f"Restored {backup['document_type']} {backup['document_name']}, field {backup['field_name']}.")
            except Exception as e:
                self.logger.error(f"Error restoring {backup['document_type']} {backup['document_name']}, field {backup['field_name']}: {e}", exc_info=True)
                frappe.db.rollback()
        self.status = "Rolled back"
        self.save(ignore_permissions=True)
        frappe.db.commit()
        self.logger.info(f"Rollback for document {self.name} completed.")

if __name__ == "__main__":
    def your_update_function(runner, **kwargs):
        """
        Example update function using safe_update.
        """
        for doc in frappe.get_all("Customer", fields=["name", "customer_group"]):
            runner.safe_update(doc.name, "customer_group", "Commercial")

    # Create an instance of SafeDataUpdate
    safe_data_update_instance = frappe.get_doc({"doctype": "Safe Data Update", "target_doctype": "Customer"})
    safe_data_update_instance.insert()
    
    # Run the test update function
    safe_data_update_instance.run(your_update_function)